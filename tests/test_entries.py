from __future__ import annotations

from datetime import datetime, timezone

from httpx import AsyncClient


def _payload() -> dict:
    now = datetime.now(tz=timezone.utc)
    return {
        "uuid": "11111111-1111-1111-1111-111111111111",
        "lotNumber": "L1",
        "entryTime": now.isoformat(),
        "exitTime": now.isoformat(),
        "createdAt": now.isoformat(),
    }


async def test_create_and_list_entries(client: AsyncClient) -> None:
    response = await client.post("/api/pasto/entries", json=_payload())
    assert response.status_code == 201
    data = response.json()
    assert data["lotNumber"] == "L1"
    assert isinstance(data["id"], int)

    response = await client.get("/api/pasto/entries")
    assert response.status_code == 200
    items = response.json()
    assert len(items) == 1
    assert items[0]["uuid"] == "11111111-1111-1111-1111-111111111111"
    assert isinstance(items[0]["id"], int)


async def test_patch_and_delete_entry(client: AsyncClient) -> None:
    response = await client.post("/api/pasto/entries", json=_payload())
    entry_uuid = response.json()["uuid"]

    response = await client.patch(
        f"/api/pasto/entries/{entry_uuid}", json={"lotNumber": "L2"}
    )
    assert response.status_code == 200
    assert response.json()["lotNumber"] == "L2"

    response = await client.delete(f"/api/pasto/entries/{entry_uuid}")
    assert response.status_code == 204

    response = await client.get(f"/api/pasto/entries/{entry_uuid}")
    assert response.status_code == 200
    assert response.json()["deletedAt"] is not None
