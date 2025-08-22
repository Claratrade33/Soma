from __future__ import annotations
import os
from contextlib import contextmanager
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

# Usa DATABASE_URL do Render; localmente cai para SQLite.
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///data.db")

# Para SQLite em arquivo, precisa desse connect_args.
connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(DATABASE_URL, echo=False, future=True, connect_args=connect_args)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)

class Base(DeclarativeBase):
    pass

@contextmanager
def get_session():
    """Context manager de sessão SQLAlchemy."""
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()

def create_all():
    """Cria as tabelas de acordo com os modelos declarados."""
    # importa para registrar as classes no metadata antes de criar
    from models import Usuario, UserCredential, OrderLog  # noqa: F401
    Base.metadata.create_all(bind=engine)