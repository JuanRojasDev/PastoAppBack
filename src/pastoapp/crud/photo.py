from __future__ import annotations

import base64
import binascii
import os
import uuid
from pathlib import Path

from sqlalchemy import select
from datetime import datetime, timezone
from sqlalchemy.orm import Session

from pastoapp.core.config import settings
from pastoapp.models.photo import PastoEntryPhoto


def _ensure_media_root() -> Path:
    root = Path(settings.media_root)
    root.mkdir(parents=True, exist_ok=True)
    return root


def _write_file(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("wb") as handle:
        handle.write(data)


def _parse_base64(payload: str) -> tuple[bytes, str | None]:
    try:
        if ";base64," in payload:
            meta, encoded = payload.split(",", 1)
            mime_type = None
            if ":" in meta:
                mime_type = meta.split(":", 1)[1].split(";", 1)[0]
            return base64.b64decode(encoded), mime_type
        return base64.b64decode(payload), None
    except binascii.Error as exc:  # pragma: no cover - defensive
        raise ValueError("Invalid base64 payload") from exc


def create_photo_from_base64(
    db: Session, entry_uuid: uuid.UUID, photo_base64: str
) -> PastoEntryPhoto:
    data, mime_type = _parse_base64(photo_base64)
    photo_id = uuid.uuid4()
    storage_key = os.path.join("pasto", str(entry_uuid), f"{photo_id}.bin")
    file_path = _ensure_media_root() / storage_key
    _write_file(file_path, data)

    photo = PastoEntryPhoto(
        id=photo_id,
        entry_uuid=entry_uuid,
        storage_key=storage_key,
        mime_type=mime_type,
        size=len(data),
    )
    db.add(photo)
    db.commit()
    db.refresh(photo)
    return photo


def list_photos(db: Session, entry_uuid: uuid.UUID) -> list[PastoEntryPhoto]:
    stmt = select(PastoEntryPhoto).where(
        PastoEntryPhoto.entry_uuid == entry_uuid, PastoEntryPhoto.deleted_at.is_(None)
    )
    return list(db.scalars(stmt))


def get_photo(db: Session, photo_uuid: uuid.UUID) -> PastoEntryPhoto | None:
    return db.execute(
        select(PastoEntryPhoto).where(PastoEntryPhoto.uuid == photo_uuid)
    ).scalar_one_or_none()


def delete_photo(db: Session, photo: PastoEntryPhoto) -> None:
    photo.deleted_at = datetime.now(tz=timezone.utc)
    db.add(photo)
    db.commit()
