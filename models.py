from __future__ import annotations
from datetime import datetime
from sqlalchemy import String, DateTime, Text, Float, Boolean
from sqlalchemy.orm import Mapped, mapped_column
from flask_login import UserMixin
from db import Base

class Usuario(Base, UserMixin):
    __tablename__ = "usuarios"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(150), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Flask-Login já usa get_id do UserMixin, mas manter explícito não atrapalha.
    def get_id(self) -> str:  # type: ignore[override]
        return str(self.id)

class UserCredential(Base):
    __tablename__ = "user_credentials"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[str] = mapped_column(String(128), index=True)
    exchange: Mapped[str] = mapped_column(String(32), index=True)
    api_key_enc: Mapped[str] = mapped_column(String(1024))
    api_secret_enc: Mapped[str] = mapped_column(String(1024))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

class OrderLog(Base):
    __tablename__ = "order_logs"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[str] = mapped_column(String(128), index=True)
    exchange: Mapped[str] = mapped_column(String(32), index=True)
    symbol: Mapped[str] = mapped_column(String(32), index=True)
    side: Mapped[str] = mapped_column(String(8))     # BUY / SELL
    tipo: Mapped[str] = mapped_column(String(16))    # MARKET / LIMIT / etc
    qty: Mapped[float] = mapped_column(Float)
    price: Mapped[float] = mapped_column(Float, default=0.0)
    status: Mapped[str] = mapped_column(String(32), default="created")
    resp_json: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)