import uuid
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from app.api import deps
from app.models.user.model import User
from app.schemas.deadline import DeadlineCreate, DeadlineUpdate, DeadlinePublic
from app.schemas.attachment import AttachmentPublic
from app.schemas.user import UserProfile
from app.services import deadline_service, attachment_service

router = APIRouter()

@router.post("/", response_model=DeadlinePublic, status_code=status.HTTP_201_CREATED)
def create_new_deadline(
    *,
    db: Session = Depends(deps.get_db),
    deadline_in: DeadlineCreate,
    current_user: User = Depends(deps.get_current_active_user)
):
    """Cria um novo prazo no sistema. Apenas usuários ADMIN podem criar prazos."""
    if current_user.profile != UserProfile.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Apenas usuários ADMIN podem criar prazos"
        )
    return deadline_service.create_deadline(db=db, deadline_in=deadline_in, user_id=current_user.id)

@router.get("/", response_model=List[DeadlinePublic])
def list_all_deadlines(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    q: str = None,  # Parâmetro de busca (compatível com frontend)
    search: str = None,  # Parâmetro de busca alternativo
    type: str = None,
    responsible_id: str = None,
    classification: str = None,
    status: str = None,
    current_user: User = Depends(deps.get_current_active_user)
):
    """Lista todos os prazos cadastrados com filtros."""
    # Usa 'q' se fornecido, senão usa 'search'
    search_term = q or search
    return deadline_service.get_all_deadlines(
        db=db, 
        skip=skip, 
        limit=limit,
        search=search_term,
        type=type,
        responsible_id=uuid.UUID(responsible_id) if responsible_id else None,
        classification=classification,
        status=status
    )

@router.get("/{deadline_id}", response_model=DeadlinePublic)
def get_deadline_details(
    deadline_id: uuid.UUID,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
):
    """Obtém os detalhes de um prazo específico."""
    deadline = deadline_service.get_deadline_by_id(db, deadline_id=deadline_id)
    if not deadline:
        raise HTTPException(status_code=404, detail="Prazo não encontrado")
    return deadline

@router.put("/{deadline_id}", response_model=DeadlinePublic)
def update_existing_deadline(
    deadline_id: uuid.UUID,
    *,
    db: Session = Depends(deps.get_db),
    obj_in: DeadlineUpdate,
    current_user: User = Depends(deps.get_current_active_user)
):
    """Atualiza um prazo existente. ADMIN pode editar qualquer prazo, advogados podem editar apenas prazos sob sua responsabilidade."""
    db_obj = deadline_service.get_deadline_by_id(db, deadline_id=deadline_id)
    if not db_obj:
        raise HTTPException(status_code=404, detail="Prazo não encontrado")
    
    # Verificar permissões: ADMIN pode editar qualquer prazo, outros usuários só podem editar se forem responsáveis
    if current_user.profile != UserProfile.ADMIN and db_obj.responsible_user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Você só pode editar prazos sob sua responsabilidade"
        )
    
    return deadline_service.update_deadline(db=db, db_obj=db_obj, obj_in=obj_in, user_id=current_user.id)

@router.delete("/{deadline_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_existing_deadline(
    deadline_id: uuid.UUID,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
):
    """Exclui um prazo. Apenas usuários ADMIN podem excluir prazos."""
    if current_user.profile != UserProfile.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Apenas usuários ADMIN podem excluir prazos"
        )
    
    db_obj = deadline_service.get_deadline_by_id(db, deadline_id=deadline_id)
    if not db_obj:
        raise HTTPException(status_code=404, detail="Prazo não encontrado")
    deadline_service.delete_deadline(db=db, db_obj=db_obj)
    return None

# Endpoints para Attachments
@router.post("/{deadline_id}/attachments", response_model=AttachmentPublic, status_code=status.HTTP_201_CREATED)
def upload_attachment(
    deadline_id: uuid.UUID,
    file: UploadFile = File(...),
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user)
):
    """Faz upload de um anexo para um prazo."""
    # Verificar se o deadline existe
    deadline = deadline_service.get_deadline_by_id(db, deadline_id=deadline_id)
    if not deadline:
        raise HTTPException(status_code=404, detail="Prazo não encontrado")
    
    # Verificar permissões: ADMIN pode anexar em qualquer prazo, outros usuários só em prazos sob sua responsabilidade
    if current_user.profile != UserProfile.ADMIN and deadline.responsible_user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Você só pode anexar arquivos em prazos sob sua responsabilidade"
        )
    
    return attachment_service.create_attachment(
        db=db,
        file=file,
        deadline_id=deadline_id,
        uploaded_by_id=current_user.id
    )

@router.get("/{deadline_id}/attachments", response_model=List[AttachmentPublic])
def list_attachments(
    deadline_id: uuid.UUID,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user)
):
    """Lista todos os anexos de um prazo."""
    # Verificar se o deadline existe
    deadline = deadline_service.get_deadline_by_id(db, deadline_id=deadline_id)
    if not deadline:
        raise HTTPException(status_code=404, detail="Prazo não encontrado")
    
    return attachment_service.get_attachments_by_deadline(db=db, deadline_id=deadline_id)

@router.get("/{deadline_id}/attachments/{attachment_id}/download")
def download_attachment(
    deadline_id: uuid.UUID,
    attachment_id: uuid.UUID,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user)
):
    """Faz download de um anexo."""
    # Verificar se o attachment existe e pertence ao deadline
    attachment = attachment_service.get_attachment_by_id(db, attachment_id=attachment_id)
    if not attachment or attachment.deadline_id != deadline_id:
        raise HTTPException(status_code=404, detail="Anexo não encontrado")
    
    return FileResponse(
        path=attachment.file_path,
        filename=attachment.original_filename,
        media_type=attachment.content_type
    )

@router.delete("/{deadline_id}/attachments/{attachment_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_attachment(
    deadline_id: uuid.UUID,
    attachment_id: uuid.UUID,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user)
):
    """Deleta um anexo."""
    # Verificar se o attachment existe e pertence ao deadline
    attachment = attachment_service.get_attachment_by_id(db, attachment_id=attachment_id)
    if not attachment or attachment.deadline_id != deadline_id:
        raise HTTPException(status_code=404, detail="Anexo não encontrado")
    
    # Verificar permissões: ADMIN pode deletar qualquer anexo, outros usuários só podem deletar se forem responsáveis pelo prazo ou se fizeram o upload
    deadline = deadline_service.get_deadline_by_id(db, deadline_id=deadline_id)
    if (current_user.profile != UserProfile.ADMIN and 
        deadline.responsible_user_id != current_user.id and 
        attachment.uploaded_by_id != current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Você só pode deletar anexos de prazos sob sua responsabilidade ou que você mesmo enviou"
        )
    
    attachment_service.delete_attachment(db=db, attachment=attachment)
    return None