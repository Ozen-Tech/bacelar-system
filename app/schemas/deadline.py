import uuid
from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from enum import Enum
from .user import UserPublic
from typing import Optional, List
from .history import DeadlineHistoryPublic
from .attachment import AttachmentPublic

class DeadlineStatus(str, Enum):
    PENDENTE = "pendente"
    CONCLUIDO = "concluido"
    CANCELADO = "cancelado"

class DeadlineClassification(str, Enum):
    NORMAL = "normal"
    CRITICO = "critico"
    FATAL = "fatal"

class DeadlineBase(BaseModel):
    task_description: str = Field(..., min_length=5)
    due_date: datetime
    process_number: Optional[str] = None
    type: Optional[str] = None
    parties: Optional[str] = None
    status: DeadlineStatus = DeadlineStatus.PENDENTE
    responsible_user_id: Optional[uuid.UUID] = None

class DeadlineCreate(DeadlineBase):
    pass

class DeadlineUpdate(BaseModel):
    task_description: Optional[str] = None
    due_date: Optional[datetime] = None
    process_number: Optional[str] = None
    type: Optional[str] = None
    parties: Optional[str] = None
    status: Optional[DeadlineStatus] = None
    responsible_user_id: Optional[uuid.UUID] = None

class DeadlinePublic(DeadlineBase):
    id: uuid.UUID
    classification: DeadlineClassification
    responsible: Optional[UserPublic] = None
    history: list[DeadlineHistoryPublic] = []
    attachments: list[AttachmentPublic] = []
    created_at: datetime
    updated_at: Optional[datetime] = None
    model_config = ConfigDict(from_attributes=True)

# Schemas para importação em massa
class BulkDeadlineError(BaseModel):
    """Erro ao processar um deadline específico na importação em massa"""
    index: int = Field(..., description="Índice do deadline na lista (começando em 0)")
    task_description: Optional[str] = Field(None, description="Descrição da tarefa que falhou")
    error: str = Field(..., description="Descrição do erro")

class BulkDeadlineSkipped(BaseModel):
    """Deadline que foi pulado por já existir no banco de dados"""
    index: int = Field(..., description="Índice do deadline na lista (começando em 0)")
    task_description: str = Field(..., description="Descrição da tarefa")
    process_number: Optional[str] = Field(None, description="Número do processo")
    due_date: datetime = Field(..., description="Data de vencimento")
    reason: str = Field(default="Prazo duplicado já existe no banco de dados", description="Motivo de ter sido pulado")
    existing_deadline_id: Optional[uuid.UUID] = Field(None, description="ID do prazo existente no banco")

class BulkImportResponse(BaseModel):
    """Resposta da importação em massa de deadlines"""
    total_received: int = Field(..., description="Total de deadlines recebidos")
    imported_count: int = Field(..., description="Quantidade importada com sucesso")
    skipped_count: int = Field(default=0, description="Quantidade de duplicatas puladas")
    error_count: int = Field(..., description="Quantidade de erros")
    deadlines: List[DeadlinePublic] = Field(default_factory=list, description="Deadlines criados com sucesso")
    skipped: List[BulkDeadlineSkipped] = Field(default_factory=list, description="Deadlines pulados (duplicatas)")
    errors: List[BulkDeadlineError] = Field(default_factory=list, description="Lista de erros encontrados")

class BulkDeadlineCreate(BaseModel):
    """Request para criação em massa de deadlines"""
    deadlines: List[DeadlineCreate] = Field(..., min_items=1, max_items=500, description="Lista de deadlines a serem criados (máximo 500 por requisição)")
    skip_duplicates: bool = Field(default=True, description="Se True, pula deadlines duplicados (recomendado). Usa processo + data + descrição como chave")
    skip_notifications: bool = Field(default=True, description="Se True, não envia notificações (recomendado para grandes volumes)")
    skip_celery: bool = Field(default=True, description="Se True, não dispara tarefas de classificação automática (recomendado para grandes volumes)")