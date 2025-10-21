"""Exception handler middleware for FastAPI applications.

Provides handlers for custom exceptions, such as BusinessException.

Functions:
    business_exception_handler: Handles BusinessException errors and returns structured JSON response.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from fastapi.responses import JSONResponse
from loguru import logger

from fastwings.exception import BusinessException

if TYPE_CHECKING:
    from fastapi import Request


async def business_exception_handler(_: Request, exc: BusinessException) -> JSONResponse:
    """Handles BusinessException errors, logs details, and returns a structured JSON response.

    Args:
        _ (Request): Incoming FastAPI request object (unused).
        exc (BusinessException): The business exception instance.

    Returns:
        JSONResponse: Response containing error code, message, and data, with CORS headers.
    """
    logger.error(f"{exc.message}\n{exc.data}".rstrip())
    headers = {"Access-Control-Allow-Origin": "*", "Access-Control-Allow-Credentials": "true"}

    return JSONResponse(
        status_code=exc.status_code,
        content={"code": exc.code, "message": exc.message, "data": exc.data},
        headers=headers,
    )
