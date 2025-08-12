import os
import uuid
import shutil
from pathlib import Path
from typing import List, Optional
from fastapi import UploadFile, HTTPException
from sqlalchemy.orm import Session
from app.models.attachment.model import Attachment
from app.models.deadline.model import Deadline
from app.schemas.attachment import AttachmentCreate
from app.core.config import settings

# Diretório para armazenar os arquivos
UPLOADS_DIR = Path("uploads")
UPLOADS_DIR.mkdir(exist_ok=True)

def create_attachment(
    db: Session,
    file: UploadFile,
    deadline_id: uuid.UUID,
    uploaded_by_id: uuid.UUID
) -> Attachment:
    """Cria um novo attachment para um deadline."""
    
    # Verificar se o deadline existe
    deadline = db.query(Deadline).filter(Deadline.id == deadline_id).first()
    if not deadline:
        raise HTTPException(status_code=404, detail="Deadline não encontrado")
    
    # Gerar nome único para o arquivo
    file_extension = Path(file.filename).suffix if file.filename else ""
    unique_filename = f"{uuid.uuid4()}{file_extension}"
    file_path = UPLOADS_DIR / str(deadline_id) / unique_filename
    
    # Criar diretório se não existir
    file_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Salvar arquivo no disco
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao salvar arquivo: {str(e)}")
    
    # Obter tamanho do arquivo
    file_size = file_path.stat().st_size
    
    # Criar registro no banco
    attachment_data = AttachmentCreate(
        filename=unique_filename,
        original_filename=file.filename or "unknown",
        file_path=str(file_path),
        file_size=file_size,
        content_type=file.content_type or "application/octet-stream",
        deadline_id=deadline_id,
        uploaded_by_id=uploaded_by_id
    )
    
    db_attachment = Attachment(**attachment_data.model_dump())
    db.add(db_attachment)
    db.commit()
    db.refresh(db_attachment)
    
    return db_attachment

def get_attachments_by_deadline(db: Session, deadline_id: uuid.UUID) -> List[Attachment]:
    """Obtém todos os attachments de um deadline."""
    return db.query(Attachment).filter(Attachment.deadline_id == deadline_id).all()

def get_attachment_by_id(db: Session, attachment_id: uuid.UUID) -> Optional[Attachment]:
    """Obtém um attachment pelo ID."""
    return db.query(Attachment).filter(Attachment.id == attachment_id).first()

def delete_attachment(db: Session, attachment: Attachment) -> None:
    """Deleta um attachment do banco e do disco."""
    # Remover arquivo do disco
    try:
        if os.path.exists(attachment.file_path):
            os.remove(attachment.file_path)
    except Exception:
        pass  # Continua mesmo se não conseguir remover o arquivo
    
    # Remover do banco
    db.delete(attachment)
    db.commit()