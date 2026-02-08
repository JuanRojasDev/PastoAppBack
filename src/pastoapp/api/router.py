from __future__ import annotations

from fastapi import APIRouter

from pastoapp.api.endpoints import health, pasto_entries, photos, sync


api_router = APIRouter()
api_router.include_router(health.router, tags=["health"])
api_router.include_router(pasto_entries.router, tags=["pasto"])
api_router.include_router(sync.router, tags=["sync"])
api_router.include_router(photos.router, tags=["photos"])
