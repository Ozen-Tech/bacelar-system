
import uuid
from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from enum import Enum
from .user import UserPublic
from typing import Optional
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