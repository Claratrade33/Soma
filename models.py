from __future__ import annotations

from datetime import datetime
from sqlalchemy import (
    String, DateTime, Text, Float, Boolean,
    Integer, ForeignKey, func
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from flask_login import UserMixin

# Importa a Base do teu db.py (estilo SQLAlchemy 2.x)
from db import Base


# ---------------------------------------------------------------------------
# Usuário
# ---------------------------------------------------------------------------
class Usuario(Base, UserMixin):
    __tablename__ = "usuarios"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(150), unique=True, index=True, nullable=False)
    # guarda o hash da senha (não a senha crua)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # usa server_default p/ timestamp do banco; fallback com python default
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), default=datetime.utcnow, nullable=False
    )

    # relacionamentos
    credenciais: Mapped[list["UserCredential"]] = relationship(
        back_populates="usuario", cascade="all, delete-orphan", lazy="selectin"
    )
    order_logs: Mapped[list["OrderLog"]] = relationship(
        back_populates="usuario", cascade="all, delete-orphan", lazy="selectin"
    )

    # Flask-Login já pega via UserMixin, mas manter explícito evita susto
    def get_id(self) -> str:  # type: ignore[override]
        return str(self.id)

    def __repr__(self) -> str:
        return f"<Usuario {self.username}>"


# ---------------------------------------------------------------------------
# Credenciais do Usuário (ex.: chaves da exchange criptografadas)
# ---------------------------------------------------------------------------
class UserCredential(Base):
    __tablename__ = "user_credentials"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    # faz sentido ser INT com FK real, não String
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("usuarios.id", ondelete="CASCADE"), index=True, nullable=False
    )

    # qual exchange (binance, bybit, etc.)
    exchange: Mapped[str] = mapped_column(String(32), index=True, nullable=False, default="binance")

    # chaves já criptografadas (ex.: via Fernet) – guarda ciphertext base64
    api_key_enc: Mapped[str] = mapped_column(String(1024), nullable=False)
    api_secret_enc: Mapped[str] = mapped_column(String(1024), nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), default=datetime.utcnow, nullable=False
    )

    # relacionamento reverso
    usuario: Mapped["Usuario"] = relationship(back_populates="credenciais")

    def __repr__(self) -> str:
        return f"<UserCredential user={self.user_id} exchange={self.exchange}>"


# ---------------------------------------------------------------------------
# Log de Ordens (auditoria/histórico de envios e respostas)
# ---------------------------------------------------------------------------
class OrderLog(Base):
    __tablename__ = "order_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("usuarios.id", ondelete="SET NULL"), index=True, nullable=True
    )
    exchange: Mapped[str] = mapped_column(String(32), index=True, nullable=False, default="binance")

    symbol: Mapped[str] = mapped_column(String(32), index=True, nullable=False)
    side: Mapped[str] = mapped_column(String(8), nullable=False)      # BUY/SELL
    tipo: Mapped[str] = mapped_column(String(16), nullable=False)      # MARKET/LIMIT/STOP/TAKE/OCO/etc.

    qty: Mapped[float] = mapped_column(Float, nullable=False)
    price: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)

    status: Mapped[str] = mapped_column(String(32), nullable=False, default="created")
    resp_json: Mapped[str] = mapped_column(Text, nullable=False, default="")

    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), default=datetime.utcnow, nullable=False
    )

    # relacionamento reverso
    usuario: Mapped["Usuario"] = relationship(back_populates="order_logs")

    def __repr__(self) -> str:
        return f"<OrderLog id={self.id} user={self.user_id} {self.symbol} {self.side} {self.tipo} {self.qty}@{self.price}>"