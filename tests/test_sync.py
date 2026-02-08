from __future__ import annotations

from datetime import datetime, timezone

from httpx import AsyncClient


def _entry_payload(entry_uuid: str, lot: str) -> dict:
    now = datetime.now(tz=timezone.utc)
    return {
        "uuid": entry_uuid,
        "lotNumber": lot,
        "entryTime": now.isoformat(),
        "exitTime": now.isoformat(),
        "createdAt": now.isoformat(),
    }


async def test_sync_push_pull(client: AsyncClient) -> None:
    payload = {
        "deviceId": "device-1",
        "items": [
            _entry_payload("aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa", "L1"),
            _entry_payload("bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb", "L2"),
        ],
        "deletedIds": [],
    }

    response = await client.post("/api/sync/pasto/push", json=payload)
    assert response.status_code == 200
    cursor = response.json()["newCursor"]
    assert cursor >= 1

    response = await client.get("/api/sync/pasto/pull", params={"cursor": 0})
    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) == 2
    assert data["newCursor"] >= cursor

    delete_payload = {
        "deviceId": "device-1",
        "items": [],
        "deletedIds": ["aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa"],
    }
    response = await client.post("/api/sync/pasto/push", json=delete_payload)
    assert response.status_code == 200

    response = await client.get(
        "/api/sync/pasto/pull", params={"cursor": data["newCursor"]}
    )
    assert response.status_code == 200
    pull_data = response.json()
    assert "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa" in pull_data["deleted"]
