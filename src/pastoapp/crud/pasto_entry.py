from __future__ import annotations

import uuid
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from sqlalchemy import desc, func, select
from sqlalchemy.orm import Session

from pastoapp.models.pasto_entry import PastoEntry
from pastoapp.schemas.pasto_entry import PastoEntryCreate, PastoEntryUpdate


try:
    _BOGOTA_TZ = ZoneInfo("America/Bogota")
except ZoneInfoNotFoundError:
    _BOGOTA_TZ = timezone(timedelta(hours=-5))


def _utcnow() -> datetime:
    return datetime.now(tz=_BOGOTA_TZ)


def get_next_updated_seq(db: Session) -> int:
    current = db.execute(select(func.max(PastoEntry.updated_seq))).scalar()
    return int(current or 0) + 1


def get_max_updated_seq(db: Session) -> int:
    current = db.execute(select(func.max(PastoEntry.updated_seq))).scalar()
    return int(current or 0)


def upsert_entry(db: Session, payload: PastoEntryCreate, device_id: str | None) -> PastoEntry:
    entry_uuid = payload.uuid or uuid.uuid4()
    existing = db.execute(
        select(PastoEntry).where(PastoEntry.uuid == entry_uuid)
    ).scalar_one_or_none()
    now = _utcnow()
    next_seq = get_next_updated_seq(db)

    if existing:
        data = payload.model_dump(exclude_unset=True)
        for key, value in data.items():
            if key in {"photo_base64", "created_at", "id", "uuid"}:
                continue
            setattr(existing, key, value)
        if device_id and not existing.device_id:
            existing.device_id = device_id
        existing.updated_at = now
        existing.updated_seq = next_seq
        db.add(existing)
        db.commit()
        db.refresh(existing)
        return existing

    entry = PastoEntry(
        uuid=entry_uuid,
        lot_number=payload.lot_number,
        entry_time=payload.entry_time,
        exit_time=payload.exit_time,
        created_at=payload.created_at or now,
        updated_at=now,
        device_id=device_id or payload.device_id,
        updated_seq=next_seq,
    )
    db.add(entry)
    db.commit()
    db.refresh(entry)
    return entry


def get_entry(db: Session, entry_uuid: uuid.UUID) -> PastoEntry | None:
    return db.execute(
        select(PastoEntry).where(PastoEntry.uuid == entry_uuid)
    ).scalar_one_or_none()


def list_entries(
    db: Session,
    device_id: str | None,
    updated_since: datetime | None,
    include_deleted: bool,
    limit: int,
    offset: int,
) -> list[PastoEntry]:
    stmt = select(PastoEntry)
    if device_id:
        stmt = stmt.where(PastoEntry.device_id == device_id)
    if updated_since:
        stmt = stmt.where(PastoEntry.updated_at > updated_since)
    if not include_deleted:
        stmt = stmt.where(PastoEntry.deleted_at.is_(None))
    stmt = (
        stmt.order_by(desc(PastoEntry.created_at), desc(PastoEntry.updated_at))
        .offset(offset)
        .limit(limit)
    )
    return list(db.scalars(stmt))


def update_entry(
    db: Session, entry: PastoEntry, payload: PastoEntryUpdate, device_id: str | None
) -> PastoEntry:
    data = payload.model_dump(exclude_unset=True)
    for key, value in data.items():
        if key in {"photo_base64", "created_at", "id", "uuid"}:
            continue
        setattr(entry, key, value)
    if device_id and not entry.device_id:
        entry.device_id = device_id
    entry.updated_at = _utcnow()
    entry.updated_seq = get_next_updated_seq(db)
    db.add(entry)
    db.commit()
    db.refresh(entry)
    return entry


def soft_delete_entry(db: Session, entry: PastoEntry) -> PastoEntry:
    entry.deleted_at = _utcnow()
    entry.updated_at = _utcnow()
    entry.updated_seq = get_next_updated_seq(db)
    db.add(entry)
    db.commit()
    db.refresh(entry)
    return entry


def list_entries_by_cursor(
    db: Session, cursor: int, limit: int, device_id: str | None
) -> list[PastoEntry]:
    stmt = select(PastoEntry).where(PastoEntry.updated_seq > cursor)
    if device_id:
        stmt = stmt.where(PastoEntry.device_id == device_id)
    stmt = stmt.order_by(PastoEntry.updated_seq).limit(limit)
    return list(db.scalars(stmt))
