from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from pastoapp.schemas.pasto_entry import PastoEntryCreate, PastoEntryRead


class SyncPushRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    device_id: str | None = Field(default=None, alias="deviceId")
    client_time: datetime | None = Field(default=None, alias="clientTime")
    items: list[PastoEntryCreate] = []
    deleted_ids: list[uuid.UUID] = Field(default_factory=list, alias="deletedIds")


class SyncRejectedItem(BaseModel):
    id: uuid.UUID
    reason: str


class SyncPushResponse(BaseModel):
    accepted: list[uuid.UUID]
    rejected: list[SyncRejectedItem]
    server_time: datetime = Field(..., alias="serverTime")
    new_cursor: int = Field(..., alias="newCursor")


class SyncPullResponse(BaseModel):
    items: list[PastoEntryRead]
    deleted: list[uuid.UUID]
    new_cursor: int = Field(..., alias="newCursor")
