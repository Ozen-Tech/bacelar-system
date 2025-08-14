import uuid
from sqlalchemy.orm import Session
from app.models.deadline.model import Deadline
from app.models.history.model import DeadlineHistory
from app.models.user.model import User
from app.schemas.deadline import DeadlineCreate, DeadlineUpdate
from app.schemas.user import UserProfile
from app.services import notification_service


def get_deadline_by_id(db: Session, deadline_id: uuid.UUID) -> Deadline | None:
    return db.query(Deadline).filter(Deadline.id == deadline_id).first()

def get_all_deadlines(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    search: str | None = None,
    type: str | None = None,
    responsible_id: uuid.UUID | None = None,
    classification: str | None = None,
    status: str | None = None
) -> list[Deadline]:
    query = db.query(Deadline)
    if search:
        query = query.filter(Deadline.process_number.ilike(f"%{search}%"))
    if type:
        query = query.filter(Deadline.type == type)
    if responsible_id:
        query = query.filter(Deadline.responsible_user_id == responsible_id)
    if classification:
        query = query.filter(Deadline.classification == classification)
    if status:
        query = query.filter(Deadline.status == status)
        
    return query.order_by(Deadline.due_date.asc()).offset(skip).limit(limit).all()

def create_deadline(db: Session, *, deadline_in: DeadlineCreate, user_id: uuid.UUID) -> Deadline:

    from app.tasks import classify_deadline

    # Cria o objeto do prazo
    db_deadline = Deadline(**deadline_in.model_dump())
    db.add(db_deadline)
    db.flush() # Usa flush para obter o ID do novo prazo antes do commit final

    # Cria o registro de histórico de criação
    history_log = DeadlineHistory(
        deadline_id=db_deadline.id,
        acting_user_id=user_id,
        action_description="Prazo criado.",
        details=deadline_in.model_dump(mode="json")
    )
    db.add(history_log)
    
    db.commit()
    db.refresh(db_deadline)

    # --- 2. CRIAR NOTIFICAÇÕES ---
    # Notificar TODOS os usuários ativos sobre o novo prazo
    all_active_users = db.query(User).filter(User.is_active == True).all()
    
    for user in all_active_users:
        # Personalizar a mensagem baseada no papel do usuário
        if user.id == db_deadline.responsible_user_id:
            # Usuário responsável pelo prazo
            notification_service.create_notification(
                db=db,
                user_id=user.id,
                title="Novo prazo atribuído",
                body=f"Você foi designado como responsável pelo prazo: {db_deadline.task_description}"
            )
        elif user.id == user_id:
            # Usuário que criou o prazo - não notificar para evitar spam
            continue
        else:
            # Todos os outros usuários ativos
            notification_service.create_notification(
                db=db,
                user_id=user.id,
                title="Novo prazo criado",
                body=f"Um novo prazo foi criado: {db_deadline.task_description}"
            )

    # --- 3. DISPARE A TAREFA EM SEGUNDO PLANO ---
    # '.delay()' é o comando que envia a tarefa para a fila do Celery.
    # Passamos apenas o ID, que é um dado simples e serializável.
    classify_deadline.delay(str(db_deadline.id))

    return db_deadline

def update_deadline(
    db: Session, *, db_obj: Deadline, obj_in: DeadlineUpdate, user_id: uuid.UUID
) -> Deadline:
    from app.tasks import classify_deadline

    update_data = obj_in.model_dump(exclude_unset=True)
    history_details = {}
    
    # Itera sobre os dados de atualização para construir o objeto de histórico
    for field, value in update_data.items():
        old_value = getattr(db_obj, field)
        if old_value != value:
            history_details[field] = {"de": str(old_value), "para": str(value)}
            setattr(db_obj, field, value)
    
    # Se houve alguma alteração, cria um log de histórico
    if history_details:
        history_log = DeadlineHistory(
            deadline_id=db_obj.id,
            acting_user_id=user_id,
            action_description="Prazo atualizado.",
            details=history_details,
        )
        db.add(history_log)
        
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)

    classify_deadline.delay(str(db_obj.id))

    return db_obj

def delete_deadline(db: Session, *, db_obj: Deadline):
    # Aqui optamos pela exclusão física, mas uma exclusão lógica (mudar status) também é válida
    db.delete(db_obj)
    db.commit()
    return db_obj