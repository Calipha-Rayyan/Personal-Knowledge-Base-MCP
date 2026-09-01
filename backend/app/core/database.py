from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from app.core.config import settings

# backend/app/core/database.py -> parents[2] == backend/
# Resolving to an absolute path means the app finds the SAME database file
# regardless of which directory a command is run from (uvicorn, pytest,
# a standalone script, etc). Previously a relative path like
# "sqlite:///./knowledge_base.db" silently created a new EMPTY database
# whenever the working directory didn't match, which caused confusing
# "table doesn't exist" errors.
BACKEND_DIR = Path(__file__).resolve().parents[2]


def _resolve_database_url(url: str) -> str:
    if not url.startswith("sqlite:///"):
        # Not SQLite (e.g. a future Postgres URL) — use as-is.
        return url

    path_part = url[len("sqlite:///"):]

    if path_part == ":memory:" or path_part.startswith(":memory:"):
        return url

    path = Path(path_part)
    if path.is_absolute():
        return url

    absolute_path = (BACKEND_DIR / path).resolve()
    return f"sqlite:///{absolute_path}"


DATABASE_URL = _resolve_database_url(settings.database_url)

connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(
    DATABASE_URL,
    connect_args=connect_args,
)


SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)


class Base(DeclarativeBase):
    pass


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()