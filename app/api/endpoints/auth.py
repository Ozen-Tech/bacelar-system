from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.schemas.token import Token
from app.services import user_service
from app.core.security import create_access_token
from app.api import deps
from app.models.user.model import User

router = APIRouter()

@router.post("/login", response_model=Token)
def login_for_access_token(db: Session = Depends(deps.get_db), form_data: OAuth2PasswordRequestForm = Depends()):
    user = user_service.authenticate_user(db, identifier=form_data.username, password=form_data.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Email/CPF ou senha incorretos")
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Usuário inativo")

    access_token = create_access_token(data={"sub": user.email, "profile": user.profile.value})
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/refresh", response_model=Token)
def refresh_access_token(
    *,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
):
    """
    Gera um novo access token para o usuário logado.

    Use este endpoint quando o token estiver próximo de expirar
    para renovar sem precisar fazer login novamente.

    Requer: Token JWT válido (mesmo que próximo de expirar)
    Retorna: Novo token JWT com prazo de validade renovado
    """
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Usuário inativo"
        )

    # Gera novo token
    access_token = create_access_token(
        data={"sub": current_user.email, "profile": current_user.profile.value}
    )

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }