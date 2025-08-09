from __future__ import annotations
from datetime import datetime
from sqlalchemy import String, DateTime, Float, Boolean, Text
from sqlalchemy.orm import Mapped, mapped_column
from db import Base

class UserCredential(Base):
    __tablename__ = "user_credentials"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[str] = mapped_column(String(128), index=True)
    exchange: Mapped[str] = mapped_column(String(32), index=True)  # 'binance'
    api_key_enc: Mapped[str] = mapped_column(String(1024))
    api_secret_enc: Mapped[str] = mapped_column(String(1024))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

class OrderHistory(Base):
    __tablename__ = "order_history"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[str] = mapped_column(String(128), index=True)
    mode: Mapped[str] = mapped_column(String(32), index=True)  # 'paper' | 'binance_testnet' | 'binance'
    symbol: Mapped[str] = mapped_column(String(32), index=True)
    side: Mapped[str] = mapped_column(String(8))               # BUY/SELL
    type: Mapped[str] = mapped_column(String(32))              # MARKET/LIMIT/STOP_LIMIT/TAKE_PROFIT/OCO
    qty: Mapped[float] = mapped_column(Float)
    price: Mapped[float] = mapped_column(Float, default=0.0)   # limit ou preço de execução
    stop_price: Mapped[float] = mapped_column(Float, default=0.0)
    take_price: Mapped[float] = mapped_column(Float, default=0.0)
    oco: Mapped[bool] = mapped_column(Boolean, default=False)
    status: Mapped[str] = mapped_column(String(32), default="filled")  # filled/open/canceled
    exchange_order_id: Mapped[str] = mapped_column(String(128), default="")
    note: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

class PaperAccount(Base):
    __tablename__ = "paper_accounts"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[str] = mapped_column(String(128), unique=True, index=True)
    balances_json: Mapped[str] = mapped_column(Text, default="{}")  # {"USDT": 10000.0, "BTC": 0.0}
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)