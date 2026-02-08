from __future__ import annotations

import uuid
from pathlib import Path

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from pastoapp.core.config import settings
from pastoapp.crud.photo import (
    delete_photo as delete_photo_record,
    get_photo,
    list_photos,
)
from pastoapp.db.session import get_db
from pastoapp.models.photo import PastoEntryPhoto
from pastoapp.schemas.photo import PhotoRead


router = APIRouter()


@router.post("/pasto/entries/{entry_uuid}/photos", response_model=PhotoRead, status_code=status.HTTP_201_CREATED)
def upload_photo(
    entry_uuid: uuid.UUID,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
) -> PhotoRead:
    contents = file.file.read()
    if not contents:
        raise HTTPException(status_code=400, detail="Empty file")

    photo_id = uuid.uuid4()
    storage_key = f"pasto/{entry_uuid}/{photo_id}.bin"
    file_path = Path(settings.media_root) / storage_key
    file_path.parent.mkdir(parents=True, exist_ok=True)
    file_path.write_bytes(contents)

    photo = PastoEntryPhoto(
        id=photo_id,
        entry_uuid=entry_uuid,
        storage_key=storage_key,
        mime_type=file.content_type,
        size=len(contents),
    )
    db.add(photo)
    db.commit()
    db.refresh(photo)
    return photo


@router.get("/pasto/entries/{entry_uuid}/photos", response_model=list[PhotoRead])
def list_entry_photos(entry_uuid: uuid.UUID, db: Session = Depends(get_db)) -> list[PhotoRead]:
    return list_photos(db, entry_uuid)


@router.get("/photos/{photo_uuid}/content")
def get_photo_content(photo_uuid: uuid.UUID, db: Session = Depends(get_db)) -> FileResponse:
    photo = get_photo(db, photo_uuid)
    if not photo or photo.deleted_at:
        raise HTTPException(status_code=404, detail="Photo not found")
    file_path = Path(settings.media_root) / photo.storage_key
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Photo content not found")
    return FileResponse(file_path, media_type=photo.mime_type or "application/octet-stream")


@router.delete("/photos/{photo_uuid}", status_code=status.HTTP_204_NO_CONTENT)
def delete_photo(photo_uuid: uuid.UUID, db: Session = Depends(get_db)) -> None:
    photo = get_photo(db, photo_uuid)
    if not photo:
        raise HTTPException(status_code=404, detail="Photo not found")
    delete_photo_record(db, photo)
    return None
