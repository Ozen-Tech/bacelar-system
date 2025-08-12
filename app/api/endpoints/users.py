# app/api/endpoints/users.py (VERSÃO FINAL E CORRIGIDA)

from fastapi import APIRouter, Depends, Body, status, HTTPException
from sqlalchemy.orm import Session
# --- A CORREÇÃO ESTÁ AQUI: Adicionamos UserUpdate ---
from app.schemas.user import UserPublic, UserUpdate, PasswordChange
# --------------------------------------------------
from app.schemas.token import FCMTokenPayload
from app.api import deps
from app.models.user.model import User
from app.services import user_service
from typing import List 


router = APIRouter()

@router.get("/me", response_model=UserPublic)
def read_users_me(current_user: User = Depends(deps.get_current_active_user)):
    """Retorna os dados do usuário atualmente logado."""
    return current_user

@router.put("/me", response_model=UserPublic)
def update_user_me(
    *,
    db: Session = Depends(deps.get_db),
    obj_in: UserUpdate,
    current_user: User = Depends(deps.get_current_active_user)
):
    """Atualiza os dados do usuário logado (nome, email, telefone, etc)."""
    return user_service.update_user(db=db, db_obj=current_user, obj_in=obj_in)

@router.post("/me/change-password", status_code=status.HTTP_204_NO_CONTENT)
def change_password(
    *,
    db: Session = Depends(deps.get_db),
    password_data: PasswordChange,
    current_user: User = Depends(deps.get_current_active_user)
):
    """Altera a senha do usuário logado."""
    success = user_service.change_password(
        db=db,
        user=current_user,
        current_password=password_data.current_password,
        new_password=password_data.new_password
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Senha atual incorreta"
        )
    
    return None

@router.post("/me/fcm-token", status_code=status.HTTP_204_NO_CONTENT)
def update_fcm_token(
    payload: FCMTokenPayload = Body(...),
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
):
    """
    Recebe e salva o FCM token do aparelho do usuário logado.
    O app mobile deve chamar esta rota após o login e a cada vez que o token mudar.
    """
    current_user.fcm_token = payload.fcm_token
    db.add(current_user)
    db.commit()
    return None

@router.get("/", response_model=List[UserPublic])
def get_all_users(
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user)
):
    """
    Retorna uma lista de todos os usuários (acessível por qualquer usuário logado).
    """
    return user_service.get_all_users(db=db)