import pytest
from httpx import AsyncClient
from decimal import Decimal
import uuid
from datetime import datetime

async def get_token(client: AsyncClient):
    await client.post("/auth/register", json={"email": "exp@x.com", "password": "p123456"})
    r = await client.post("/auth/login", json={"email": "exp@x.com", "password": "p123456"})
    return r.json()["access_token"]

async def test_create_and_list_expenses(client: AsyncClient):
    token = await get_token(client)
    headers = {"Authorization": f"Bearer {token}"}
    client_id = str(uuid.uuid4())
    payload = {
        "amount": "250.50",
        "category": "food",
        "description": "lunch",
        "date": datetime.utcnow().isoformat(),
        "client_id": client_id
    }
    r = await client.post("/expenses", json=payload, headers=headers)
    assert r.status_code == 201
    created = r.json()
    # retry same request with same client_id -> should return same expense (idempotent)
    r2 = await client.post("/expenses", json=payload, headers=headers)
    assert r2.status_code == 201
    assert r2.json()["id"] == created["id"]

    # add another
    payload2 = payload.copy()
    payload2["client_id"] = str(uuid.uuid4())
    payload2["amount"] = "100.00"
    payload2["category"] = "travel"
    await client.post("/expenses", json=payload2, headers=headers)

    # list all
    r3 = await client.get("/expenses", headers=headers)
    assert r3.status_code == 200
    data = r3.json()
    assert data["count"] == 2
    assert Decimal(data["total"]) >= Decimal("350.50")

    # filter by category
    r4 = await client.get("/expenses?category=food", headers=headers)
    assert r4.status_code == 200
    assert r4.json()["count"] == 1

    # sort newest first
    r5 = await client.get("/expenses?sort=date_desc", headers=headers)
    assert r5.status_code == 200
