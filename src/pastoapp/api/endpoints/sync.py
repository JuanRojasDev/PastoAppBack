from __future__ import annotations

import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, Header, Query
from sqlalchemy.orm import Session

from pastoapp.crud.pasto_entry import (
    get_entry,
    get_max_updated_seq,
    list_entries_by_cursor,
    soft_delete_entry,
    upsert_entry,
)
from pastoapp.db.session import get_db
from pastoapp.schemas.pasto_entry import PastoEntryRead
from pastoapp.schemas.sync import (
    SyncPullResponse,
    SyncPushRequest,
    SyncPushResponse,
    SyncRejectedItem,
)


router = APIRouter(prefix="/sync/pasto")


@router.post("/push", response_model=SyncPushResponse)
def push_pasto_entries(
    payload: SyncPushRequest,
    db: Session = Depends(get_db),
    x_device_id: str | None = Header(default=None, alias="X-Device-Id"),
) -> SyncPushResponse:
    accepted: list[uuid.UUID] = []
    rejected: list[SyncRejectedItem] = []
    device_id = x_device_id or payload.device_id

    for item in payload.items:
        try:
            entry = upsert_entry(db, item, device_id)
            accepted.append(entry.uuid)
        except Exception as exc:  # pragma: no cover - defensive
            rejected.append(
                SyncRejectedItem(id=item.id or uuid.UUID(int=0), reason=str(exc))
            )

    for deleted_id in payload.deleted_ids:
        entry = get_entry(db, deleted_id)
        if entry:
            soft_delete_entry(db, entry)

    latest_seq = get_max_updated_seq(db)

    return SyncPushResponse(
        accepted=accepted,
        rejected=rejected,
        server_time=datetime.now(tz=timezone.utc),
        new_cursor=latest_seq,
    )


@router.get("/pull", response_model=SyncPullResponse)
def pull_pasto_entries(
    db: Session = Depends(get_db),
    x_device_id: str | None = Header(default=None, alias="X-Device-Id"),
    cursor: int = Query(default=0, ge=0),
    limit: int = Query(default=500, ge=1, le=1000),
    device_id: str | None = Query(default=None),
) -> SyncPullResponse:
    resolved_device_id = x_device_id or device_id
    entries = list_entries_by_cursor(db, cursor, limit, resolved_device_id)
    items: list[PastoEntryRead] = []
    deleted: list = []
    max_cursor = cursor
    for entry in entries:
        max_cursor = max(max_cursor, entry.updated_seq)
        if entry.deleted_at:
            deleted.append(entry.id)
        else:
            items.append(entry)

    return SyncPullResponse(items=items, deleted=deleted, new_cursor=max_cursor)
