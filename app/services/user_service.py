from sqlalchemy.orm import Session
from sqlalchemy import or_
from app.models.user.model import User
from app.schemas.user import UserCreate, UserUpdate
from app.core.security import get_password_hash, verify_password

def get_user_by_email_or_cpf(db: Session, identifier: str) -> User | None:
    return db.query(User).filter(or_(User.email == identifier, User.cpf == identifier)).first()

def get_user_by_email(db: Session, email: str) -> User | None:
    return db.query(User).filter(User.email == email).first()

def create_user(db: Session, *, user_in: UserCreate) -> User:
    db_user = User(
        email=user_in.email,
        password_hash=get_password_hash(user_in.password),
        name=user_in.name,
        profile=user_in.profile
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def authenticate_user(db: Session, *, identifier: str, password: str) -> User | None:
    user = get_user_by_email_or_cpf(db, identifier=identifier)
    if not user or not verify_password(password, user.password_hash):
        return None
    return user

def update_user(db: Session, *, db_obj: User, obj_in: UserUpdate) -> User:
    update_data = obj_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        # Lógica especial para nested Pydantic models como notification_preferences
        if isinstance(value, dict):
            # Obtém o valor antigo
            old_value = getattr(db_obj, field)
            # Atualiza as chaves do dicionário antigo com as novas
            if old_value:
                old_value.update(value)
                setattr(db_obj, field, old_value)
            else:
                 setattr(db_obj, field, value)
        else:
            setattr(db_obj, field, value)
            
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj

def change_password(db: Session, *, user: User, current_password: str, new_password: str) -> bool:
    """Altera a senha do usuário após verificar a senha atual."""
    # Verifica se a senha atual está correta
    if not verify_password(current_password, user.password_hash):
        return False
    
    # Atualiza com a nova senha
    user.password_hash = get_password_hash(new_password)
    db.add(user)
    db.commit()
    db.refresh(user)
    return True

def get_all_users(db: Session) -> list[User]:
    """Busca todos os usuários do banco."""
    return db.query(User).order_by(User.name).all()