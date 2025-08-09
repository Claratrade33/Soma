from __future__ import annotations
from datetime import datetime
from sqlalchemy import String, DateTime, Text, Float
from sqlalchemy.orm import Mapped, mapped_column
from db import Base

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
    side: Mapped[str] = mapped_column(String(8))
    tipo: Mapped[str] = mapped_column(String(16))  # MARKET/LIMIT/STOP/TAKE/OCO
    qty: Mapped[float] = mapped_column(Float)
    price: Mapped[float] = mapped_column(Float, default=0.0)
    status: Mapped[str] = mapped_column(String(32), default="created")
    resp_json: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)