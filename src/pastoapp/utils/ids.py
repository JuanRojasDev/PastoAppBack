from __future__ import annotations

import uuid


def new_uuid() -> uuid.UUID:
    return uuid.uuid4()
