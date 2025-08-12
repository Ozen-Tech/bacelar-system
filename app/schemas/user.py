# app/schemas/user.py
import uuid
from pydantic import BaseModel, EmailStr, Field, ConfigDict
from enum import Enum
from typing import Optional

class UserProfile(str, Enum):
    ADMIN = "admin"
    ADVOGADO = "advogado"
    ESTAGIARIO = "estagiario"

class NotificationPreferences(BaseModel):
    email: bool = False
    push: bool = True

class UserBase(BaseModel):
    email: EmailStr
    name: str = Field(..., min_length=3)
    profile: UserProfile = UserProfile.ADVOGADO
    phone: Optional[str] = None
    notification_preferences: Optional[NotificationPreferences] = Field(default_factory=NotificationPreferences)

class UserCreate(UserBase):
    password: str = Field(..., min_length=6)

class UserUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    notification_preferences: Optional[NotificationPreferences] = None

class PasswordChange(BaseModel):
    current_password: str = Field(..., min_length=1)
    new_password: str = Field(..., min_length=6)

class UserPublic(UserBase):
    id: uuid.UUID
    model_config = ConfigDict(from_attributes=True)