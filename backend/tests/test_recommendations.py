import pytest
from unittest.mock import AsyncMock, patch
from httpx import AsyncClient

pytestmark = pytest.mark.asyncio


async def _get_token(client: AsyncClient, email: str = "recs@example.com") -> str:
    await client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": "password123"},
    )
    login = await client.post(
        "/api/v1/auth/login",
        data={"username": email, "password": "password123"},
    )
    return login.json()["access_token"]


async def test_recommendations_returns_response(client: AsyncClient):
    token = await _get_token(client)

    # Gorse is mocked — it's an external service
    with patch(
        "app.services.gorse_client.GorseClient.get_recommendations",
        new_callable=AsyncMock,
        return_value=[],
    ):
        res = await client.get(
            "/api/v1/recommendations/me",
            headers={"Authorization": f"Bearer {token}"},
        )

    assert res.status_code == 200
    data = res.json()
    assert "results" in data
    assert isinstance(data["results"], list)


async def test_recommendations_requires_auth(client: AsyncClient):
    res = await client.get("/api/v1/recommendations/me")
    assert res.status_code == 401
