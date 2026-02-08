# PastoAppBack

Backend REST API en FastAPI para PastoAppBack (sin usuarios ni autenticación).

## Requisitos
- Python 3.11+
- PostgreSQL 16+

## Configuración
Crear un archivo .env a partir de .env.example y ajustar valores.

### Variables de entorno
- DATABASE_URL
- CORS_ORIGINS
- LOG_LEVEL
- MEDIA_ROOT

## Ejecutar en Windows (venv)
1) Crear entorno virtual:
   - python -m venv .venv
2) Activar:
   - .venv\Scripts\activate
3) Instalar dependencias:
   - pip install -e .
   - pip install -e .[dev]
4) Migraciones:
   - alembic upgrade head
5) Levantar API:
   - uvicorn pastoapp.main:app --reload

## Ejecutar con Docker
1) Crear .env (opcional si usas docker-compose)
2) Levantar servicios:
   - docker compose up --build
3) Migraciones (en otro terminal):
   - docker compose exec api alembic upgrade head

## Endpoints
- GET /api/status
- CRUD /api/pasto/entries
- POST /api/sync/pasto/push
- GET /api/sync/pasto/pull
- POST /api/pasto/entries/{entry_id}/photos
- GET /api/pasto/entries/{entry_id}/photos
- GET /api/photos/{photo_id}/content

## Contrato (PastoEntry)
El backend expone ambos identificadores:
- id (int)
- uuid (UUID)

Campos principales (camelCase):
- lotNumber (string)
- entryTime (ISO datetime)
- exitTime (ISO datetime)
- createdAt (ISO datetime)
- photoBase64 (opcional, base64)

Header opcional:
- X-Device-Id (prioridad sobre body deviceId)

Campos adicionales en respuestas:
- updatedAt, deletedAt, updatedSeq, deviceId

Los endpoints consultan por uuid:
- /api/pasto/entries/{entry_uuid}
- /api/photos/{photo_uuid}

## Sync (offline-first)
### Push
POST /api/sync/pasto/push
Body:
{
   "deviceId": "...",
   "clientTime": "...",
   "items": [ { ...PastoEntry... } ],
   "deletedIds": ["uuid", ...]
}

### Pull
GET /api/sync/pasto/pull?cursor=0&limit=500
Respuesta:
{
   "items": [ ...PastoEntry... ],
   "deleted": ["uuid", ...],
   "newCursor": 123
}

## Tests
- pytest

## Estructura
- src/pastoapp: aplicación
- alembic: migraciones
- tests: pruebas

## Calidad
- ruff check .
- black .