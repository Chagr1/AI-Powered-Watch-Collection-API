import os
import sys
from pathlib import Path
from logging.config import fileConfig

# 1. FORCE LOAD .ENV AND OVERRIDE EXISTING SYSTEM VARIABLES
BASE_DIR = Path(__file__).resolve().parents[1]
ENV_FILE_PATH = BASE_DIR / ".env"

from dotenv import load_dotenv
load_dotenv(dotenv_path=ENV_FILE_PATH, override=True)

from sqlalchemy import engine_from_config
from sqlalchemy import pool
from alembic import context

sys.path.append(str(BASE_DIR))
from app.database.database import Base
from app.models.user import UserDB
from app.models.watch import WatchDB

# 2. BYPASS PYDANTIC SETTINGS AND FETCH DIRECTLY FROM OS
DATABASE_URL = os.getenv("DATABASE_URL")

config = context.config
config.set_main_option("sqlalchemy.url", DATABASE_URL)

print(f"\n!!! ALEMBIC IS CONNECTING TO !!! -> {DATABASE_URL}\n")

# ... (The rest of the file remains the same: if config.config_file_name is not None: ...)

# ... (The rest of the file remains the same: if config.config_file_name is not None: ...)

# ... (The rest of the file remains the same: if config.config_file_name is not None: ...)

# Interpret the config file for Python logging.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
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
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
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