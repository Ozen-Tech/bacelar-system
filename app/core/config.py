# app/core/config.py
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

class Settings(BaseSettings):
    # Database
    DATABASE_URL: str
    
    # Security
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 10080  # 7 dias como padrão
    
    # Admin
    SUPERUSER_EMAIL: str
    SUPERUSER_PASSWORD: str
    
    # Celery (agora opcionais para não quebrar se Redis não estiver configurado)
    CELERY_BROKER_URL: Optional[str] = None
    CELERY_RESULT_BACKEND: Optional[str] = None
    
    # Redis (se você estiver usando Redis separado do Celery)
    REDIS_URL: Optional[str] = None
    
    # Frontend
    FRONTEND_URL: str
    
    # Firebase
    FIREBASE_CREDENTIALS_PATH: Optional[str] = None
    FIREBASE_CREDENTIALS_JSON: Optional[str] = None
    
    # APIs Externas (opcionais)
    OPENAI_API_KEY: Optional[str] = None
    GOOGLE_API_KEY: Optional[str] = None
    
    # Environment - ADICIONADO para não quebrar o startup
    ENVIRONMENT: str = "production"
    
    # Configuração do Pydantic V2
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding='utf-8',
        extra='ignore'  # Ignora variáveis extras do Railway
    )

settings = Settings()

# Log de inicialização (útil para debug no Railway)
print("🔧 Configurações carregadas:")
print(f"   📍 Environment: {settings.ENVIRONMENT}")
print(f"   🗄️  Database: {'✅ Configurado' if settings.DATABASE_URL else '❌ Faltando'}")
print(f"   🔴 Redis/Celery: {'✅ Configurado' if settings.CELERY_BROKER_URL else '⚠️  Não configurado (opcional)'}")
print(f"   🌐 Frontend: {settings.FRONTEND_URL if settings.FRONTEND_URL else '⚠️  Não configurado'}")
print(f"   🔥 Firebase: {'✅ Configurado' if settings.FIREBASE_CREDENTIALS_JSON or settings.FIREBASE_CREDENTIALS_PATH else '⚠️  Não configurado (opcional)'}")