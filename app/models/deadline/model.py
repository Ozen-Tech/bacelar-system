import uuid
from sqlalchemy import Column, String, DateTime, Text, Enum as SQLAlchemyEnum, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base_class import Base
from app.schemas.deadline import DeadlineStatus, DeadlineClassification

class Deadline(Base):
    __tablename__ = "deadlines"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    process_number = Column(String(100), index=True)
    parties = Column(Text, nullable=True) # Partes envolvidas no processo
    type = Column(String(100), index=True, nullable=True)

    task_description = Column(Text, nullable=False)
    due_date = Column(DateTime(timezone=True), nullable=False, index=True)
    
    status = Column(SQLAlchemyEnum(DeadlineStatus), nullable=False, default=DeadlineStatus.PENDENTE, index=True)
    classification = Column(SQLAlchemyEnum(DeadlineClassification), nullable=False, default=DeadlineClassification.NORMAL)
    
    
    responsible_user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    responsible = relationship("User", back_populates="deadlines")
    
    history = relationship("DeadlineHistory", back_populates="deadline", cascade="all, delete-orphan")
    attachments = relationship("Attachment", back_populates="deadline", cascade="all, delete-orphan")

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())