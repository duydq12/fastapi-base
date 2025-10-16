"""Unit tests for FastAPI middleware and exception handlers in fastwings.

Covers timer middleware and custom business exception handler.
"""
import pytest
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient
from starlette.middleware.base import BaseHTTPMiddleware

from fastwings.exception import BusinessException
from fastwings.middleware.common_handler import timer_middleware
from fastwings.middleware.exception_handler import business_exception_handler
from fastwings.response import ExceptionDetail

# --- Setup for timer_middleware ---
app_timer = FastAPI()
app_timer.add_middleware(BaseHTTPMiddleware, dispatch=timer_middleware)


@app_timer.get("/")
async def root():
    """Test endpoint for timer middleware."""
    return {"message": "Hello"}


# --- Setup for exception_handler ---
app_exc = FastAPI()
app_exc.add_exception_handler(BusinessException, business_exception_handler)


@app_exc.get("/error")
async def raise_error():
    """Test endpoint for business exception handler."""
    raise BusinessException(
        status_code=400,
        exception=ExceptionDetail(code="TEST001", message="Test Error")
    )


@pytest.mark.asyncio
async def test_timer_middleware_adds_header():
    """Test that timer middleware adds the 'x-process-time' header to responses."""
    async with AsyncClient(transport=ASGITransport(app=app_timer), base_url="http://test") as ac:
        response = await ac.get("/")
    assert response.status_code == 200
    assert "x-process-time" in response.headers
    assert float(response.headers["x-process-time"]) > 0


@pytest.mark.asyncio
async def test_business_exception_handler_returns_json():
    """Test that business exception handler returns correct JSON response."""
    async with AsyncClient(transport=ASGITransport(app=app_exc), base_url="http://test") as ac:
        response = await ac.get("/error")
    assert response.status_code == 400
    data = response.json()
    assert data["code"] == "TEST001"
    assert data["message"] == "Test Error"
