import sys
from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context

from App import Application

if not Application(Application.ApplicationType.Client):
    sys.exit(1)

from App.Core.DB import Connection
from App.Core.DB.Model import Base
from App.Core.Utils.Models import Models
from App.helpers import app

cfg = context.config

if cfg.config_file_name is not None:
    fileConfig(cfg.config_file_name)

Models.load_models()

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    context.configure(
        url=cfg.get_main_option("sqlalchemy.url"),
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    connectable = engine_from_config(
        cfg.get_section(cfg.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as c:
        context.configure(connection=c, target_metadata=target_metadata)

        with context.begin_transaction():
            context.run_migrations()


connection: Connection = app().get("db")

cfg.set_main_option('sqlalchemy.url', connection.driver().creds())

run_migrations_offline() if context.is_offline_mode() else run_migrations_online()
