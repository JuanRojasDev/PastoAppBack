from __future__ import annotations

from fastapi import APIRouter


router = APIRouter()

@router.get("/status")
def status_check() -> dict[str, str]:
    return {"status": "ok"}
