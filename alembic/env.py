# alembic/env.py (COM A CORREÇÃO FINAL - fileConfig COMENTADO)
import os
import sys
from logging.config import fileConfig

# Adiciona a pasta raiz ao caminho para resolver 'ModuleNotFoundError'
sys.path.insert(0, os.path.realpath(os.path.join(os.path.dirname(__file__), '..')))

from sqlalchemy import engine_from_config
from sqlalchemy import pool
from alembic import context
from dotenv import load_dotenv

load_dotenv()

# --- Modelos SQLAlchemy precisam ser importados aqui para o autogenerate ---
from app.db.base_class import Base
from app.db import base 
from app.models.user.model import User
from app.models.deadline.model import Deadline
from app.models.history.model import DeadlineHistory
target_metadata = Base.metadata
# -------------------------------------------------------------------------

# Objeto de configuração do Alembic
config = context.config

# --- CORREÇÃO DEFINITIVA ---
# Comentamos a linha abaixo para evitar erros de KeyError.
# Esta linha é responsável por configurar o logging, que não é
# essencial para a geração de migrações.
# if config.config_file_name is not None:
#     fileConfig(config.config_file_name)

# --- CORREÇÃO DA URL DO BANCO ---
# Diz ao Alembic para usar a DATABASE_URL do nosso arquivo .env
config.set_main_option('sqlalchemy.url', os.getenv('DATABASE_URL'))


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()