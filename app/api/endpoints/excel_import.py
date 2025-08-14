from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from typing import List
import pandas as pd
from datetime import datetime
import io

from app.api.deps import get_current_user, get_db
from app.models.user.model import User
from app.services.deadline_service import create_deadline
from app.schemas.deadline import DeadlineCreate

router = APIRouter()

@router.post("/import-excel")
async def import_excel_deadlines(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Importa prazos de uma planilha Excel.
    
    Estrutura esperada da planilha:
    - Coluna A: Parte 1 (Autor)
    - Coluna B: Parte 2 (Réu/Advogado)
    - Coluna C: Número do Processo
    - Coluna D: Data do Prazo e Descrição
    - Coluna E: Vara/Juizado
    """
    
    if not file.filename.endswith(('.xlsx', '.xls')):
        raise HTTPException(
            status_code=400,
            detail="Arquivo deve ser uma planilha Excel (.xlsx ou .xls)"
        )
    
    try:
        # Lê o arquivo Excel
        contents = await file.read()
        df = pd.read_excel(io.BytesIO(contents))
        
        # Remove linhas vazias e cabeçalhos
        df = df.dropna(how='all')
        
        # Pula as primeiras linhas que são cabeçalhos
        # Baseado na estrutura da planilha fornecida
        start_row = 0
        for idx, row in df.iterrows():
            if pd.notna(row.iloc[0]) and str(row.iloc[0]).strip() not in ['', 'Autor', 'PAUTA DE AGOSTO 2025']:
                start_row = idx
                break
        
        df = df.iloc[start_row:].reset_index(drop=True)
        
        imported_deadlines = []
        errors = []
        
        for idx, row in df.iterrows():
            try:
                # Extrai dados da linha
                parte1 = str(row.iloc[0]).strip() if pd.notna(row.iloc[0]) else ""
                parte2 = str(row.iloc[1]).strip() if pd.notna(row.iloc[1]) else ""
                processo = str(row.iloc[2]).strip() if pd.notna(row.iloc[2]) else ""
                prazo_desc = str(row.iloc[3]).strip() if pd.notna(row.iloc[3]) else ""
                vara = str(row.iloc[4]).strip() if pd.notna(row.iloc[4]) else ""
                
                # Pula linhas vazias
                if not any([parte1, parte2, processo, prazo_desc, vara]):
                    continue
                
                # Monta as partes
                parties = f"{parte1} x {parte2}" if parte1 and parte2 else (parte1 or parte2)
                
                # Extrai data e descrição do campo prazo_desc
                due_date = None
                task_description = prazo_desc
                
                # Tenta extrair data do formato "DD/MM/YYYY Descrição"
                import re
                date_match = re.search(r'(\d{2}/\d{2}/\d{4})', prazo_desc)
                if date_match:
                    date_str = date_match.group(1)
                    try:
                        due_date = datetime.strptime(date_str, '%d/%m/%Y')
                        # Remove a data da descrição
                        task_description = prazo_desc.replace(date_str, '').strip()
                    except ValueError:
                        pass
                
                # Se não conseguiu extrair data, usa uma data padrão (hoje + 30 dias)
                if not due_date:
                    from datetime import timedelta
                    due_date = datetime.now() + timedelta(days=30)
                
                # Cria o prazo
                deadline_data = DeadlineCreate(
                    task_description=task_description or "Prazo importado da planilha",
                    due_date=due_date,
                    process_number=processo if processo else None,
                    type="Importado",
                    parties=parties if parties else None,
                    responsible_user_id=current_user.id
                )
                
                deadline = create_deadline(db=db, deadline_in=deadline_data, user_id=current_user.id)
                imported_deadlines.append({
                    "id": str(deadline.id),
                    "task_description": deadline.task_description,
                    "parties": deadline.parties,
                    "process_number": deadline.process_number,
                    "due_date": deadline.due_date.isoformat()
                })
                
            except Exception as e:
                errors.append({
                    "linha": idx + 1,
                    "erro": str(e),
                    "dados": row.to_dict()
                })
        
        return {
            "message": f"Importação concluída. {len(imported_deadlines)} prazos importados.",
            "imported_count": len(imported_deadlines),
            "error_count": len(errors),
            "imported_deadlines": imported_deadlines,
            "errors": errors
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao processar planilha: {str(e)}"
        )