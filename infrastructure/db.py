"""Database helpers for the project.

Provides a minimal wrapper to obtain a SQLAlchemy engine or a psycopg2
connection. Import-time failures are guarded so the repository can be
imported in environments that don't have DB dependencies installed.
"""
from __future__ import annotations

import os
from typing import Optional

try:
    from sqlalchemy import create_engine
except Exception:
    create_engine = None

try:
    import psycopg2
except Exception:
    psycopg2 = None


def get_database_url() -> str:
    host = os.getenv("DB_HOST", "localhost")
    name = os.getenv("DB_NAME", "evor")
    user = os.getenv("DB_USER", "postgres")
    password = os.getenv("DB_PASSWORD", "")
    # Prefer explicit DATABASE_URL if provided
    env = os.getenv("DATABASE_URL")
    if env:
        return env
    return f"postgresql+psycopg2://{user}:{password}@{host}/{name}"


def get_engine(echo: bool = False):
    """Return a SQLAlchemy engine. Raises informative ImportError if SQLAlchemy
    is not available.
    """
    if create_engine is None:
        raise ImportError("sqlalchemy is required to create an engine. Install it or use psycopg2 directly.")
    url = get_database_url()
    return create_engine(url, echo=echo)


def get_psycopg2_conn():
    """Return a raw psycopg2 connection. Raises ImportError if psycopg2 not installed."""
    if psycopg2 is None:
        raise ImportError("psycopg2 is required for raw DB connections")
    host = os.getenv("DB_HOST", "localhost")
    dbname = os.getenv("DB_NAME", "evor")
    user = os.getenv("DB_USER", "postgres")
    password = os.getenv("DB_PASSWORD", "")
    return psycopg2.connect(host=host, dbname=dbname, user=user, password=password)
