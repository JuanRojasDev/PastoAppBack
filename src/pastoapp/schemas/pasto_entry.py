from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, model_validator


class PastoEntryBase(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    id: int | str | None = Field(default=None, alias="id")
    uuid: UUID | None = Field(default=None, alias="uuid")
    lot_number: str = Field(..., alias="lotNumber")
    entry_time: datetime = Field(..., alias="entryTime")
    exit_time: datetime = Field(..., alias="exitTime")
    created_at: datetime | None = Field(default=None, alias="createdAt")
    device_id: str | None = Field(default=None, alias="deviceId")
    photo_base64: str | None = Field(default=None, alias="photoBase64")


class PastoEntryCreate(PastoEntryBase):
    @model_validator(mode="after")
    def map_legacy_id(self) -> "PastoEntryCreate":
        if self.uuid is None and isinstance(self.id, str):
            try:
                self.uuid = UUID(self.id)
            except ValueError:
                pass
        return self


class PastoEntryUpdate(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    id: int | str | None = Field(default=None, alias="id")
    uuid: UUID | None = Field(default=None, alias="uuid")
    lot_number: str | None = Field(default=None, alias="lotNumber")
    entry_time: datetime | None = Field(default=None, alias="entryTime")
    exit_time: datetime | None = Field(default=None, alias="exitTime")
    created_at: datetime | None = Field(default=None, alias="createdAt")
    device_id: str | None = Field(default=None, alias="deviceId")
    photo_base64: str | None = Field(default=None, alias="photoBase64")


class PastoEntryRead(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: int
    uuid: UUID
    lot_number: str = Field(..., alias="lotNumber")
    entry_time: datetime = Field(..., alias="entryTime")
    exit_time: datetime = Field(..., alias="exitTime")
    created_at: datetime = Field(..., alias="createdAt")
    updated_at: datetime = Field(..., alias="updatedAt")
    deleted_at: datetime | None = Field(default=None, alias="deletedAt")
    device_id: str | None = Field(default=None, alias="deviceId")
    updated_seq: int | None = Field(default=None, alias="updatedSeq")
