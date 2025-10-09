import uuid
from datetime import datetime
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
    status: str | None = None,
    due_date_from: str | None = None,
    due_date_to: str | None = None
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
    if due_date_from:
        try:
            from_date = datetime.strptime(due_date_from, "%Y-%m-%d").date()
            query = query.filter(Deadline.due_date >= from_date)
        except ValueError:
            pass  # Ignora datas inválidas
    if due_date_to:
        try:
            to_date = datetime.strptime(due_date_to, "%Y-%m-%d").date()
            query = query.filter(Deadline.due_date <= to_date)
        except ValueError:
            pass  # Ignora datas inválidas

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


def check_duplicate_deadline(
    db: Session,
    *,
    process_number: str | None = None,
    due_date: datetime | None = None,
    task_description: str | None = None,
    tolerance_days: int = 0
) -> Deadline | None:
    """
    Verifica se já existe um prazo duplicado no sistema.

    Critérios de duplicata:
    - Mesmo número de processo (obrigatório se fornecido)
    - Data de vencimento igual ou próxima (dentro da tolerância)
    - Descrição similar (opcional)

    Args:
        db: Sessão do banco de dados
        process_number: Número do processo
        due_date: Data de vencimento
        task_description: Descrição da tarefa
        tolerance_days: Tolerância em dias para considerar datas próximas (padrão: 0 = mesmo dia)

    Returns:
        Deadline existente se encontrar duplicata, None caso contrário
    """
    from datetime import timedelta, datetime as dt

    # Se não tiver número de processo, não conseguimos verificar duplicata de forma confiável
    if not process_number:
        return None

    # Busca prazos com o mesmo número de processo
    query = db.query(Deadline).filter(Deadline.process_number == process_number)

    # Se tiver data de vencimento, filtra por data próxima
    if due_date:
        # Converte para datetime se for date
        if isinstance(due_date, dt):
            due_date_dt = due_date
        else:
            due_date_dt = dt.combine(due_date, dt.min.time())

        # Define o intervalo de datas (data ± tolerância)
        date_from = due_date_dt - timedelta(days=tolerance_days)
        date_to = due_date_dt + timedelta(days=tolerance_days)

        query = query.filter(
            Deadline.due_date >= date_from,
            Deadline.due_date <= date_to
        )

    # Busca o primeiro resultado
    existing_deadline = query.first()

    # Se encontrou e tiver descrição para comparar, verifica similaridade
    if existing_deadline and task_description:
        # Calcula similaridade simples (pode ser melhorado com difflib)
        existing_desc = existing_deadline.task_description.lower().strip()
        new_desc = task_description.lower().strip()

        # Se as descrições são muito diferentes, pode não ser duplicata
        # Mas por segurança, vamos considerar duplicata se processo e data batem
        pass

    return existing_deadline


def create_deadline_bulk(
    db: Session,
    *,
    deadline_in: DeadlineCreate,
    user_id: uuid.UUID,
    skip_notifications: bool = True,
    skip_celery: bool = True
) -> Deadline:
    """
    Cria um prazo sem enviar notificações (otimizado para importação em massa).

    Args:
        db: Sessão do banco de dados
        deadline_in: Dados do prazo a ser criado
        user_id: ID do usuário que está criando
        skip_notifications: Se True, não envia notificações (padrão: True)
        skip_celery: Se True, não dispara tarefas Celery (padrão: True)

    Returns:
        Deadline criado
    """
    from app.tasks import classify_deadline

    # Cria o objeto do prazo
    db_deadline = Deadline(**deadline_in.model_dump())
    db.add(db_deadline)
    db.flush()  # Usa flush para obter o ID do novo prazo antes do commit final

    # Cria o registro de histórico de criação
    history_log = DeadlineHistory(
        deadline_id=db_deadline.id,
        acting_user_id=user_id,
        action_description="Prazo criado via importação.",
        details=deadline_in.model_dump(mode="json")
    )
    db.add(history_log)

    db.commit()
    db.refresh(db_deadline)

    # Notificações e Celery são opcionais para importação em massa
    if not skip_notifications:
        all_active_users = db.query(User).filter(User.is_active == True).all()

        for user in all_active_users:
            if user.id == db_deadline.responsible_user_id:
                notification_service.create_notification(
                    db=db,
                    user_id=user.id,
                    title="Novo prazo atribuído",
                    body=f"Você foi designado como responsável pelo prazo: {db_deadline.task_description}"
                )
            elif user.id != user_id:
                notification_service.create_notification(
                    db=db,
                    user_id=user.id,
                    title="Novo prazo criado",
                    body=f"Um novo prazo foi criado: {db_deadline.task_description}"
                )

    if not skip_celery:
        classify_deadline.delay(str(db_deadline.id))

    return db_deadline
