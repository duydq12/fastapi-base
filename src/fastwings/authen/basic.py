"""Implements HTTP Basic authentication for FastAPI applications.

Provides password hashing and verification utilities.

Functions:
    verify_password: Verifies a plain password against a hashed password using bcrypt.
    get_password_hash: Hashes a password using bcrypt.
    basic_auth: FastAPI dependency to authenticate user using HTTP Basic credentials.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from fastapi import Depends
from fastapi.security import HTTPBasic
from passlib.context import CryptContext

from fastwings.config import settings
from fastwings.error_code import AuthErrorCode

if TYPE_CHECKING:
    from fastapi.security import HTTPBasicCredentials

basic_credential = HTTPBasic()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifies a plain password against a hashed password using bcrypt.

    Args:
        plain_password (str): The plain text password to verify.
        hashed_password (str): The hashed password to compare against.

    Returns:
        bool: True if the password matches, False otherwise.
    """
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    is_matched: bool = pwd_context.verify(plain_password, hashed_password)
    return is_matched


def get_password_hash(password: str) -> str:
    """Hashes a password using bcrypt.

    Args:
        password (str): The plain text password to hash.

    Returns:
        str: The hashed password.
    """
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    pwd_hash: str = pwd_context.hash(password)
    return pwd_hash


async def basic_auth(credentials: HTTPBasicCredentials = Depends(basic_credential)) -> None:  # noqa: B008
    """FastAPI dependency to authenticate user using HTTP Basic credentials.

    Args:
        credentials (HTTPBasicCredentials): Credentials provided by the client.

    Raises:
        BusinessException: If authentication fails due to incorrect username or password.
    """
    try:
        if not settings.BASIC_USERNAME or not settings.BASIC_PASSWORD:
            raise AuthErrorCode.INCORRECT_USERNAME_PASSWORD.value from None
        correct_username = verify_password(credentials.username, settings.BASIC_USERNAME)
        correct_password = verify_password(credentials.password, settings.BASIC_PASSWORD)
        if not (correct_username and correct_password):
            raise AuthErrorCode.INCORRECT_USERNAME_PASSWORD.value from None
    except Exception:
        raise AuthErrorCode.INCORRECT_USERNAME_PASSWORD.value from None
