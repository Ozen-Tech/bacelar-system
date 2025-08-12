import uuid
from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional
from .user import UserPublic

class AttachmentBase(BaseModel):
    filename: str
    original_filename: str
    file_size: int
    content_type: str

class AttachmentCreate(AttachmentBase):
    file_path: str
    deadline_id: uuid.UUID
    uploaded_by_id: uuid.UUID

class AttachmentPublic(AttachmentBase):
    id: uuid.UUID
    deadline_id: uuid.UUID
    uploaded_by: Optional[UserPublic] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    model_config = ConfigDict(from_attributes=True)