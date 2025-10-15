"""Unit tests for FastAPI app endpoints in fastapi_base.

Covers health check endpoint and response validation.
"""
import pytest
from httpx import ASGITransport, AsyncClient

from fastapi_base.app import app


@pytest.mark.asyncio
async def test_health_check():
    """Tests the /health endpoint for service status.

    Asserts that the response status is 200 and service is online.
    """
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert "service" in data
    assert data["service"] == "online"
