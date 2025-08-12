import uuid
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.api import deps
from app.models.user.model import User
from app.schemas.deadline import DeadlineCreate, DeadlineUpdate, DeadlinePublic
from app.services import deadline_service

router = APIRouter()

@router.post("/", response_model=DeadlinePublic, status_code=status.HTTP_201_CREATED)
def create_new_deadline(
    *,
    db: Session = Depends(deps.get_db),
    deadline_in: DeadlineCreate,
    current_user: User = Depends(deps.get_current_active_user)
):
    """Cria um novo prazo no sistema."""
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
    """Atualiza um prazo existente."""
    db_obj = deadline_service.get_deadline_by_id(db, deadline_id=deadline_id)
    if not db_obj:
        raise HTTPException(status_code=404, detail="Prazo não encontrado")
    return deadline_service.update_deadline(db=db, db_obj=db_obj, obj_in=obj_in, user_id=current_user.id)

@router.delete("/{deadline_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_existing_deadline(
    deadline_id: uuid.UUID,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
):
    """Exclui um prazo."""
    db_obj = deadline_service.get_deadline_by_id(db, deadline_id=deadline_id)
    if not db_obj:
        raise HTTPException(status_code=404, detail="Prazo não encontrado")
    deadline_service.delete_deadline(db=db, db_obj=db_obj)
    return None