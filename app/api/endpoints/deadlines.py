import uuid
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from app.api import deps
from app.models.user.model import User
from app.schemas.deadline import (
    DeadlineCreate,
    DeadlineUpdate,
    DeadlinePublic,
    BulkDeadlineCreate,
    BulkImportResponse,
    BulkDeadlineError,
    BulkDeadlineSkipped
)
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

@router.post("/bulk", response_model=BulkImportResponse, status_code=status.HTTP_201_CREATED)
def create_deadlines_bulk(
    *,
    db: Session = Depends(deps.get_db),
    bulk_data: BulkDeadlineCreate,
    current_user: User = Depends(deps.get_current_active_user)
):
    """
    Cria múltiplos prazos de uma vez (importação em massa via JSON).

    Apenas usuários ADMIN podem criar prazos em massa.

    Este endpoint aceita até 500 deadlines por requisição e retorna
    um relatório detalhado com sucessos, duplicatas puladas e erros.

    **Parâmetros:**
    - `deadlines`: Lista de objetos DeadlineCreate (mínimo 1, máximo 500)
    - `skip_duplicates`: Se True, pula deadlines duplicados (padrão: True). Verifica por processo + data + descrição
    - `skip_notifications`: Se True, não envia notificações (padrão: True, recomendado para grandes volumes)
    - `skip_celery`: Se True, não dispara classificação automática (padrão: True, recomendado para grandes volumes)

    **Exemplo de uso:**
    ```json
    {
        "deadlines": [
            {
                "task_description": "Apresentar contestação",
                "due_date": "2024-12-31T23:59:59",
                "process_number": "1234567-89.2024.8.01.0001",
                "type": "Recursal",
                "parties": "João vs. Maria",
                "status": "pendente",
                "responsible_user_id": "uuid-do-usuario"
            }
        ],
        "skip_duplicates": true,
        "skip_notifications": true,
        "skip_celery": true
    }
    ```

    **Retorno:**
    ```json
    {
        "total_received": 10,
        "imported_count": 7,
        "skipped_count": 1,
        "error_count": 2,
        "deadlines": [...],  // Deadlines criados com sucesso
        "skipped": [         // Duplicatas puladas
            {
                "index": 2,
                "task_description": "Prazo duplicado",
                "process_number": "1234567-89.2024.8.01.0001",
                "due_date": "2024-12-31T23:59:59",
                "reason": "Prazo duplicado já existe no banco de dados",
                "existing_deadline_id": "uuid-do-prazo-existente"
            }
        ],
        "errors": [          // Erros encontrados
            {
                "index": 3,
                "task_description": "Prazo inválido",
                "error": "Data de vencimento não pode ser no passado"
            }
        ]
    }
    ```
    """
    # Verificar permissão ADMIN
    if current_user.profile != UserProfile.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Apenas usuários ADMIN podem criar prazos em massa"
        )

    created_deadlines: List[DeadlinePublic] = []
    skipped_deadlines: List[BulkDeadlineSkipped] = []
    errors: List[BulkDeadlineError] = []

    # Processar cada deadline individualmente
    for index, deadline_data in enumerate(bulk_data.deadlines):
        try:
            # Verificar duplicatas se a opção estiver habilitada
            if bulk_data.skip_duplicates:
                existing = deadline_service.check_duplicate_deadline(
                    db=db,
                    process_number=deadline_data.process_number,
                    due_date=deadline_data.due_date,
                    task_description=deadline_data.task_description,
                    tolerance_days=1  # Tolerância de 1 dia para considerar duplicata
                )

                if existing:
                    # Prazo duplicado encontrado - pular
                    skipped_deadlines.append(BulkDeadlineSkipped(
                        index=index,
                        task_description=deadline_data.task_description[:100],
                        process_number=deadline_data.process_number,
                        due_date=deadline_data.due_date,
                        reason="Prazo duplicado já existe no banco de dados",
                        existing_deadline_id=existing.id
                    ))
                    continue  # Pular para o próximo deadline

            # Usar a função otimizada para bulk
            deadline = deadline_service.create_deadline_bulk(
                db=db,
                deadline_in=deadline_data,
                user_id=current_user.id,
                skip_notifications=bulk_data.skip_notifications,
                skip_celery=bulk_data.skip_celery
            )

            # Converter para schema público
            deadline_public = DeadlinePublic.model_validate(deadline)
            created_deadlines.append(deadline_public)

        except HTTPException as http_ex:
            # Capturar exceções HTTP específicas
            errors.append(BulkDeadlineError(
                index=index,
                task_description=deadline_data.task_description[:50] if deadline_data.task_description else "N/A",
                error=http_ex.detail
            ))
        except ValueError as val_ex:
            # Capturar erros de validação
            errors.append(BulkDeadlineError(
                index=index,
                task_description=deadline_data.task_description[:50] if deadline_data.task_description else "N/A",
                error=f"Erro de validação: {str(val_ex)}"
            ))
        except Exception as ex:
            # Capturar outros erros
            errors.append(BulkDeadlineError(
                index=index,
                task_description=deadline_data.task_description[:50] if deadline_data.task_description else "N/A",
                error=f"Erro inesperado: {str(ex)}"
            ))

    # Retornar relatório completo
    return BulkImportResponse(
        total_received=len(bulk_data.deadlines),
        imported_count=len(created_deadlines),
        skipped_count=len(skipped_deadlines),
        error_count=len(errors),
        deadlines=created_deadlines,
        skipped=skipped_deadlines,
        errors=errors
    )

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
    due_date_from: str = None,  # Filtro de data inicial
    due_date_to: str = None,  # Filtro de data final
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
        status=status,
        due_date_from=due_date_from,
        due_date_to=due_date_to
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