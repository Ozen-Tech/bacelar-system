# app/services/notification_service.py
import uuid
import json
import os
import firebase_admin
from firebase_admin import credentials, messaging
from sqlalchemy.orm import Session
from app.core.config import settings
from app.models.notification.model import Notification

try:
    # Tenta primeiro usar o arquivo de credenciais (desenvolvimento)
    if settings.FIREBASE_CREDENTIALS_PATH and os.path.exists(settings.FIREBASE_CREDENTIALS_PATH):
        cred = credentials.Certificate(settings.FIREBASE_CREDENTIALS_PATH)
        firebase_admin.initialize_app(cred)
        print("✅ Firebase Admin SDK inicializado com arquivo de credenciais.")
    # Se não encontrar o arquivo, tenta usar variável de ambiente (produção)
    elif os.getenv('FIREBASE_CREDENTIALS_JSON'):
        firebase_creds = json.loads(os.getenv('FIREBASE_CREDENTIALS_JSON'))
        cred = credentials.Certificate(firebase_creds)
        firebase_admin.initialize_app(cred)
        print("✅ Firebase Admin SDK inicializado com credenciais JSON da variável de ambiente.")
    else:
        print("⚠️ Firebase não configurado: nem arquivo nem variável de ambiente encontrados.")
except Exception as e:
    print(f"❌ ATENÇÃO: Erro ao inicializar o Firebase Admin SDK: {e}")

def send_push_notification(device_token: str, title: str, body: str, data: dict = None):
    # ... (código existente)
    pass

def get_notifications_by_user(db: Session, *, user_id: uuid.UUID) -> list[Notification]:
    return db.query(Notification).filter(Notification.user_id == user_id).order_by(Notification.created_at.desc()).limit(50).all()

def create_notification(db: Session, *, user_id: uuid.UUID, title: str, body: str) -> Notification:
    """Cria uma nova notificação para um usuário específico"""
    notification = Notification(
        user_id=user_id,
        title=title,
        body=body,
        is_read=False
    )
    db.add(notification)
    db.commit()
    db.refresh(notification)
    return notification

def mark_all_as_read(db: Session, *, user_id: uuid.UUID) -> int:
    num_updated = db.query(Notification).filter(
        Notification.user_id == user_id,
        Notification.is_read == False
    ).update({"is_read": True})
    db.commit()
    return num_updated