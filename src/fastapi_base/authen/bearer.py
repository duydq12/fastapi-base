"""Implements JWT Bearer authentication for FastAPI applications.

Provides functions for encoding, decoding, and validating JWT tokens.

Functions:
    jwt_decode: Decodes and validates a JWT token, raises exceptions for invalid/expired tokens.
    jwt_encode: Encodes user data into a JWT token with expiration.
    bearer_auth: FastAPI dependency to decode JWT from Authorization header.
"""

from datetime import datetime, timedelta
from typing import Any, Dict

import decouple

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import jwt
from pydantic import ValidationError

from fastapi_base.error_code import AuthErrorCode

reusable_oauth2 = HTTPBearer(scheme_name="Authorization")

SECRET_KEY = decouple.config("SECRET_KEY")
ALGORITHM = decouple.config("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_SECONDS = decouple.config("ACCESS_TOKEN_EXPIRE_SECONDS", 60)


def jwt_decode(credentials: str) -> Dict[str, Any]:
    """Decodes and validates a JWT token string.

    Args:
        credentials (str): JWT token string to decode.

    Returns:
        Dict[str, Any]: Decoded JWT payload.

    Raises:
        BusinessException: If token is expired or invalid.
    """
    try:
        payload = jwt.decode(credentials, SECRET_KEY, algorithms=[ALGORITHM])
    except jwt.ExpiredSignatureError:
        raise AuthErrorCode.EXPIRED_ACCESS_TOKEN.value
    except (jwt.JWTError, ValidationError):
        raise AuthErrorCode.INVALID_ACCESS_TOKEN.value
    return payload


def jwt_encode(subject: str, data: Dict[str, Any] = None, expires_second: int = 0) -> str:
    """Encodes user data into a JWT token with expiration.

    Args:
        subject (str): Subject (usually user identifier).
        data (Dict[str, Any], optional): Additional payload data.
        expires_second (int, optional): Expiration time in seconds.

    Returns:
        str: Encoded JWT token string.
    """
    expire = datetime.utcnow() + timedelta(
        seconds=expires_second or int(ACCESS_TOKEN_EXPIRE_SECONDS),
    )

    to_encode = {"sub": subject, "exp": expire}
    if data:
        to_encode.update(data)

    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


async def bearer_auth(credentials: HTTPAuthorizationCredentials = Depends(reusable_oauth2)) -> Dict[str, Any]:
    """FastAPI dependency to decode JWT from Authorization header.

    Args:
        credentials (HTTPAuthorizationCredentials): Credentials from HTTP Authorization header.

    Returns:
        Dict[str, Any]: Decoded JWT payload.

    Raises:
        BusinessException: If token is expired or invalid.
    """
    payload: Dict[str, Any] = jwt_decode(credentials.credentials)
    return payload
