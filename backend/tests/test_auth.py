import pytest
from httpx import AsyncClient

pytestmark = pytest.mark.asyncio


async def test_register(client: AsyncClient):
    res = await client.post(
        "/api/v1/auth/register",
        json={"email": "test@example.com", "password": "password123", "full_name": "Test User"},
    )
    assert res.status_code == 201
    data = res.json()
    assert data["email"] == "test@example.com"
    assert "password" not in data


async def test_login(client: AsyncClient):
    await client.post(
        "/api/v1/auth/register",
        json={"email": "login@example.com", "password": "password123"},
    )
    res = await client.post(
        "/api/v1/auth/login",
        data={"username": "login@example.com", "password": "password123"},
    )
    assert res.status_code == 200
    assert "access_token" in res.json()


async def test_login_wrong_password(client: AsyncClient):
    res = await client.post(
        "/api/v1/auth/login",
        data={"username": "login@example.com", "password": "wrong"},
    )
    assert res.status_code == 401


async def test_me(client: AsyncClient):
    await client.post(
        "/api/v1/auth/register",
        json={"email": "me@example.com", "password": "password123"},
    )
    login = await client.post(
        "/api/v1/auth/login",
        data={"username": "me@example.com", "password": "password123"},
    )
    token = login.json()["access_token"]
    res = await client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 200
    assert res.json()["email"] == "me@example.com"
