import os
import sys

from logging.config import fileConfig

from alembic import context

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

try:
    # import project DB helpers
    from infrastructure import db as project_db
except Exception:
    project_db = None

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here for 'autogenerate' support
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata
target_metadata = None


def get_url() -> str:
    # Prefer standard DATABASE_URL env var; fallback to project's helper
    url = os.getenv("DATABASE_URL")
    if url:
        return url
    if project_db is not None:
        try:
            return project_db.get_database_url()
        except Exception:
            pass
    raise RuntimeError("Database URL not configured. Set DATABASE_URL or DB_* env vars.")


# If alembic reads the .ini before we run, override sqlalchemy.url with env value
try:
    cfg_url = get_url()
    config.set_main_option('sqlalchemy.url', cfg_url)
except Exception:
    # Leave ini value as-is if no DB config available during static import
    pass


def run_migrations_offline() -> None:
    url = get_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    from sqlalchemy import engine_from_config, pool

    connectable = None
    try:
        # prefer project's engine factory
        if project_db is not None:
            connectable = project_db.get_engine()
    except Exception:
        connectable = None

    if connectable is None:
        connectable = engine_from_config(
            config.get_section(config.config_ini_section),
            prefix="sqlalchemy.",
            poolclass=pool.NullPool,
        )

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
