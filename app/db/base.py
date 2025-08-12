# app/db/base.py
# Este arquivo serve para que o Alembic possa encontrar todos os modelos.

from app.db.base_class import Base
from app.models.user.model import User
from app.models.deadline.model import Deadline
from app.models.history.model import DeadlineHistory
from app.models.notification.model import Notification
from app.models.attachment.model import Attachment
