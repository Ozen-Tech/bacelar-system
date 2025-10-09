from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from sqlalchemy.orm import Session
from typing import List
import pandas as pd
from datetime import datetime
import io
import uuid

from app.api.deps import get_current_user, get_db
from app.models.user.model import User
from app.schemas.user import UserProfile
from app.services.deadline_service import create_deadline
from app.schemas.deadline import DeadlineCreate, DeadlineClassification

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


@router.post("/import-spreadsheet")
async def import_spreadsheet(
    *,
    db: Session = Depends(get_db),
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user)
):
    """
    Importa múltiplos prazos de uma planilha Excel/CSV.

    Formato esperado da planilha:
    - descricao (obrigatório): Descrição do prazo
    - data_vencimento (obrigatório): Data no formato YYYY-MM-DD ou DD/MM/YYYY
    - numero_processo (opcional): Número do processo
    - tipo (opcional): Tipo do prazo
    - partes (opcional): Partes envolvidas
    - classificacao (opcional): normal, critico ou fatal

    Retorna:
    {
        "message": "...",
        "imported_count": 10,
        "error_count": 2,
        "imported_deadlines": [...],
        "errors": [...]
    }
    """

    # 1. VERIFICAR PERMISSÕES
    if current_user.profile != UserProfile.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Apenas usuários ADMIN podem importar prazos"
        )

    # 2. VALIDAR TIPO DE ARQUIVO
    if not file.filename.endswith(('.xlsx', '.xls', '.csv')):
        raise HTTPException(
            status_code=400,
            detail="Arquivo deve ser Excel (.xlsx, .xls) ou CSV"
        )

    try:
        # 3. LER ARQUIVO
        contents = await file.read()

        if file.filename.endswith('.csv'):
            df = pd.read_csv(io.BytesIO(contents))
        else:
            df = pd.read_excel(io.BytesIO(contents))

        # 4. NORMALIZAR COLUNAS
        df.columns = df.columns.str.lower().str.strip()

        # 5. VALIDAR COLUNAS OBRIGATÓRIAS
        required_columns = ['descricao', 'data_vencimento']
        missing_columns = [col for col in required_columns if col not in df.columns]

        if missing_columns:
            raise HTTPException(
                status_code=400,
                detail=f"Colunas obrigatórias faltando: {', '.join(missing_columns)}"
            )

        imported_deadlines = []
        errors = []

        # 6. PROCESSAR CADA LINHA
        for idx, row in df.iterrows():
            try:
                # Pular linhas vazias
                if pd.isna(row['descricao']) or str(row['descricao']).strip() == '':
                    continue

                # 6.1 VALIDAR DESCRIÇÃO
                task_description = str(row['descricao']).strip()
                if len(task_description) < 5:
                    errors.append({
                        "linha": idx + 2,
                        "erro": "Descrição deve ter pelo menos 5 caracteres",
                        "descricao": task_description
                    })
                    continue

                # 6.2 PROCESSAR DATA
                try:
                    if isinstance(row['data_vencimento'], str):
                        date_str = row['data_vencimento'].strip()
                        try:
                            due_date = datetime.strptime(date_str, '%Y-%m-%d')
                        except ValueError:
                            try:
                                due_date = datetime.strptime(date_str, '%d/%m/%Y')
                            except ValueError:
                                raise ValueError("Formato de data inválido. Use YYYY-MM-DD ou DD/MM/YYYY")
                    elif isinstance(row['data_vencimento'], pd.Timestamp):
                        due_date = row['data_vencimento'].to_pydatetime()
                    else:
                        raise ValueError("Data de vencimento inválida")
                except Exception as e:
                    errors.append({
                        "linha": idx + 2,
                        "erro": f"Erro na data: {str(e)}",
                        "descricao": task_description
                    })
                    continue

                # 6.3 PROCESSAR CAMPOS OPCIONAIS
                process_number = None if pd.isna(row.get('numero_processo')) else str(row['numero_processo']).strip()
                tipo = None if pd.isna(row.get('tipo')) else str(row['tipo']).strip()
                parties = None if pd.isna(row.get('partes')) else str(row['partes']).strip()

                # 6.4 PROCESSAR CLASSIFICAÇÃO
                classification_str = 'normal'
                if 'classificacao' in row and not pd.isna(row['classificacao']):
                    classification_str = str(row['classificacao']).lower().strip()

                # 6.5 CRIAR PRAZO NO BANCO
                deadline_data = DeadlineCreate(
                    task_description=task_description,
                    due_date=due_date,
                    process_number=process_number,
                    type=tipo,
                    parties=parties,
                    responsible_user_id=current_user.id
                )

                deadline = create_deadline(
                    db=db,
                    deadline_in=deadline_data,
                    user_id=current_user.id
                )

                imported_deadlines.append({
                    "id": str(deadline.id),
                    "task_description": deadline.task_description,
                    "due_date": deadline.due_date.isoformat(),
                    "classification": deadline.classification.value if hasattr(deadline, 'classification') else 'normal'
                })

            except Exception as e:
                errors.append({
                    "linha": idx + 2,
                    "erro": str(e),
                    "descricao": task_description if 'task_description' in locals() else 'N/A'
                })

        # 7. RETORNAR RESULTADO
        return {
            "message": f"Importação concluída. {len(imported_deadlines)} prazos importados, {len(errors)} falharam.",
            "imported_count": len(imported_deadlines),
            "error_count": len(errors),
            "imported_deadlines": imported_deadlines,
            "errors": errors
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao processar planilha: {str(e)}"
        )