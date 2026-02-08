from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class PhotoRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int = Field(..., alias="id")
    uuid: UUID = Field(..., alias="uuid")
    entry_uuid: UUID = Field(..., alias="entryUuid")
    mime_type: str | None
    size: int | None
    created_at: datetime
    deleted_at: datetime | None
