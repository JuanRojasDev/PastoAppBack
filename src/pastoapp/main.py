from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from pastoapp.api.router import api_router
from pastoapp.core.config import settings
from pastoapp.core.logging import setup_logging


setup_logging(settings.log_level)

app = FastAPI(title="PastoAppBack", version="1.0.0")

cors_origins = settings.cors_origins_list()
if cors_origins:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

app.include_router(api_router, prefix="/api")
