"""Implements JWT Bearer authentication for FastAPI applications.

Provides functions for encoding, decoding, and validating JWT tokens.

Functions:
    jwt_decode: Decodes and validates a JWT token, raises exceptions for invalid/expired tokens.
    jwt_encode: Encodes user data into a JWT token with expiration.
    bearer_auth: FastAPI dependency to decode JWT from Authorization header.
"""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import TYPE_CHECKING

from fastapi import Depends
from fastapi.security import HTTPBearer
from jose import jwt
from pydantic import ValidationError

from fastwings.config import settings
from fastwings.error.error_code import AuthErrorCode

if TYPE_CHECKING:
    from typing import Any

    from fastapi.security import HTTPAuthorizationCredentials

reusable_oauth2 = HTTPBearer(scheme_name="Authorization")


def jwt_decode(credentials: str) -> dict[str, Any]:
    """Decodes and validates a JWT token string.

    Args:
        credentials (str): JWT token string to decode.

    Returns:
        Dict[str, Any]: Decoded JWT payload.

    Raises:
        BusinessException: If token is expired or invalid.
    """
    try:
        payload: dict[str, Any] = jwt.decode(credentials, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    except jwt.ExpiredSignatureError:
        raise AuthErrorCode.EXPIRED_ACCESS_TOKEN.value from None
    except (jwt.JWTError, ValidationError):
        raise AuthErrorCode.INVALID_ACCESS_TOKEN.value from None
    return payload


def jwt_encode(subject: str, data: dict[str, Any] | None = None, expires_second: int = 0) -> str:
    """Encodes user data into a JWT token with expiration.

    Args:
        subject (str): Subject (usually user identifier).
        data (Dict[str, Any], optional): Additional payload data.
        expires_second (int, optional): Expiration time in seconds.

    Returns:
        str: Encoded JWT token string.
    """
    expire = datetime.utcnow() + timedelta(
        seconds=expires_second or int(settings.ACCESS_TOKEN_EXPIRE_SECONDS),
    )

    to_encode = {"sub": subject, "exp": expire}
    if data:
        to_encode.update(data)

    data_encoded: str = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return data_encoded


async def bearer_auth(
    credentials: HTTPAuthorizationCredentials = Depends(reusable_oauth2)  # noqa: B008
) -> dict[str, Any]:
    """FastAPI dependency to decode JWT from Authorization header.

    Args:
        credentials (HTTPAuthorizationCredentials): Credentials from HTTP Authorization header.

    Returns:
        Dict[str, Any]: Decoded JWT payload.

    Raises:
        BusinessException: If token is expired or invalid.
    """
    payload: dict[str, Any] = jwt_decode(credentials.credentials)
    return payload
