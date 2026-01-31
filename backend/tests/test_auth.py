import pytest
from httpx import AsyncClient

async def test_register_and_login(client: AsyncClient):
    # register
    r = await client.post("/auth/register", json={"email": "test@example.com", "password": "strongpass"})
    assert r.status_code == 201
    data = r.json()
    assert data["email"] == "test@example.com"
    # login
    r2 = await client.post("/auth/login", json={"email": "test@example.com", "password": "strongpass"})
    assert r2.status_code == 200
    token_data = r2.json()
    assert "access_token" in token_data
    assert token_data["token_type"] == "bearer"
