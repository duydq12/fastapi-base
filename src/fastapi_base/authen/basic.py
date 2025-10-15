"""Implements HTTP Basic authentication for FastAPI applications.

Provides password hashing and verification utilities.

Functions:
    verify_password: Verifies a plain password against a hashed password using bcrypt.
    get_password_hash: Hashes a password using bcrypt.
    basic_auth: FastAPI dependency to authenticate user using HTTP Basic credentials.
"""

import decouple
from fastapi import Depends
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from passlib.context import CryptContext

from fastapi_base.error_code import AuthErrorCode

USERNAME_HASH = decouple.config("BASIC_USERNAME")
PASSWORD_HASH = decouple.config("BASIC_PASSWORD")

basic_credential = HTTPBasic()


def verify_password(plain_password, hashed_password):
    """Verifies a plain password against a hashed password using bcrypt.

    Args:
        plain_password (str): The plain text password to verify.
        hashed_password (str): The hashed password to compare against.

    Returns:
        bool: True if the password matches, False otherwise.
    """
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    """Hashes a password using bcrypt.

    Args:
        password (str): The plain text password to hash.

    Returns:
        str: The hashed password.
    """
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    return pwd_context.hash(password)


async def basic_auth(credentials: HTTPBasicCredentials = Depends(basic_credential)) -> None:
    """FastAPI dependency to authenticate user using HTTP Basic credentials.

    Args:
        credentials (HTTPBasicCredentials): Credentials provided by the client.

    Raises:
        BusinessException: If authentication fails due to incorrect username or password.
    """
    try:
        correct_username = verify_password(credentials.username, USERNAME_HASH)
        correct_password = verify_password(credentials.password, PASSWORD_HASH)
        if not (correct_username and correct_password):
            raise AuthErrorCode.INCORRECT_USERNAME_PASSWORD.value
    except Exception:
        raise AuthErrorCode.INCORRECT_USERNAME_PASSWORD.value
