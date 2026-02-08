from __future__ import annotations

import uuid
from datetime import datetime

from fastapi import APIRouter, Depends, Header, HTTPException, Query, status
from sqlalchemy.orm import Session

from pastoapp.crud.pasto_entry import (
    get_entry,
    list_entries,
    soft_delete_entry,
    upsert_entry,
    update_entry,
)
from pastoapp.crud.photo import create_photo_from_base64
from pastoapp.db.session import get_db
from pastoapp.schemas.pasto_entry import PastoEntryCreate, PastoEntryRead, PastoEntryUpdate


router = APIRouter(prefix="/pasto/entries")


def _device_id_from_header(device_id: str | None) -> str | None:
    return device_id


@router.post("", response_model=PastoEntryRead, status_code=status.HTTP_201_CREATED)
def create_pasto_entry(
    payload: PastoEntryCreate,
    db: Session = Depends(get_db),
    x_device_id: str | None = Header(default=None, alias="X-Device-Id"),
) -> PastoEntryRead:
    device_id = _device_id_from_header(x_device_id) or payload.device_id
    entry = upsert_entry(db, payload, device_id)
    if payload.photo_base64:
        try:
            create_photo_from_base64(db, entry.uuid, payload.photo_base64)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid photoBase64")
    return entry


@router.get("", response_model=list[PastoEntryRead])
def list_pasto_entries(
    db: Session = Depends(get_db),
    x_device_id: str | None = Header(default=None, alias="X-Device-Id"),
    device_id: str | None = Query(default=None),
    updated_since: datetime | None = Query(default=None, alias="updated_since"),
    include_deleted: bool = Query(default=False),
    limit: int = Query(default=100, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
) -> list[PastoEntryRead]:
    resolved_device_id = x_device_id or device_id
    return list_entries(
        db=db,
        device_id=resolved_device_id,
        updated_since=updated_since,
        include_deleted=include_deleted,
        limit=limit,
        offset=offset,
    )


@router.get("/{entry_uuid}", response_model=PastoEntryRead)
def get_pasto_entry(
    entry_uuid: uuid.UUID, db: Session = Depends(get_db)
) -> PastoEntryRead:
    entry = get_entry(db, entry_uuid)
    if not entry:
        raise HTTPException(status_code=404, detail="Pasto entry not found")
    return entry


@router.patch("/{entry_uuid}", response_model=PastoEntryRead)
def patch_pasto_entry(
    entry_uuid: uuid.UUID,
    payload: PastoEntryUpdate,
    db: Session = Depends(get_db),
    x_device_id: str | None = Header(default=None, alias="X-Device-Id"),
) -> PastoEntryRead:
    entry = get_entry(db, entry_uuid)
    if not entry:
        raise HTTPException(status_code=404, detail="Pasto entry not found")
    device_id = x_device_id or payload.device_id
    updated = update_entry(db, entry, payload, device_id)
    if payload.photo_base64:
        try:
            create_photo_from_base64(db, updated.uuid, payload.photo_base64)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid photoBase64")
    return updated


@router.delete("/{entry_uuid}", status_code=status.HTTP_204_NO_CONTENT)
def delete_pasto_entry(entry_uuid: uuid.UUID, db: Session = Depends(get_db)) -> None:
    entry = get_entry(db, entry_uuid)
    if not entry:
        raise HTTPException(status_code=404, detail="Pasto entry not found")
    soft_delete_entry(db, entry)
    return None
