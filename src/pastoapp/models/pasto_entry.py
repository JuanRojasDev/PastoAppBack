from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import BigInteger, DateTime, Integer, String, Uuid, func
from sqlalchemy.orm import Mapped, mapped_column

from pastoapp.db.base import Base


class PastoEntry(Base):
    __tablename__ = "pasto_entries"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    uuid: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), unique=True, nullable=False, default=uuid.uuid4
    )
    lot_number: Mapped[str] = mapped_column(String(100), nullable=False)
    entry_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    exit_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    deleted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    device_id: Mapped[str | None] = mapped_column(String(128), nullable=True)
    updated_seq: Mapped[int] = mapped_column(
        BigInteger, nullable=False, default=0, server_default="0"
    )
