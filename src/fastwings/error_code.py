"""Defines standardized error codes for server and authentication errors.

Provides enums for common API error responses.

Classes:
    ServerErrorCode: Enum of server-related error codes and BusinessException instances.
    AuthErrorCode: Enum of authentication-related error codes and BusinessException instances.
"""

from enum import Enum

from starlette import status

from fastwings.exception import BusinessException
from fastwings.response import ExceptionDetail


class ServerErrorCode(Enum):
    """Enum of server-related error codes for API responses.

    Each value is a BusinessException instance with a specific message and code.
    """
    SERVER_ERROR = BusinessException(
        ExceptionDetail(message="INTERNAL SERVER ERROR", code="SERVER0100"),
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
    )
    DATABASE_ERROR = BusinessException(
        ExceptionDetail(message="DATABASE ERROR", code="SERVER0101"), status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
    )
    FILE_STORAGE_ERROR = BusinessException(
        ExceptionDetail(message="FILE STORAGE ERROR", code="SERVER0102"),
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
    )


class AuthErrorCode(Enum):
    """Enum of authentication-related error codes for API responses.

    Each value is a BusinessException instance with a specific message and code.
    """
    INCORRECT_EMAIL = BusinessException(
        ExceptionDetail(message="INCORRECT EMAIL", code="AUTH0001"),
        status_code=status.HTTP_401_UNAUTHORIZED,
    )
    INCORRECT_PHONE = BusinessException(
        ExceptionDetail(message="INCORRECT PHONE", code="AUTH0002"),
        status_code=status.HTTP_401_UNAUTHORIZED,
    )
    INCORRECT_PASSWORD = BusinessException(
        ExceptionDetail(message="INCORRECT PASSWORD", code="AUTH0003"),
        status_code=status.HTTP_401_UNAUTHORIZED,
    )
    INCORRECT_USERNAME_PASSWORD = BusinessException(
        ExceptionDetail(message="INCORRECT USERNAME OR PASSWORD", code="AUTH0004"),
        status_code=status.HTTP_401_UNAUTHORIZED,
    )
    INVALID_ACCESS_TOKEN = BusinessException(
        ExceptionDetail(message="INVALID ACCESS TOKEN", code="AUTH0005"),
        status_code=status.HTTP_401_UNAUTHORIZED,
    )
    EXPIRED_ACCESS_TOKEN = BusinessException(
        ExceptionDetail(message="EXPIRED ACCESS TOKEN", code="AUTH0006"),
        status_code=status.HTTP_401_UNAUTHORIZED,
    )
    INVALID_REFRESH_TOKEN = BusinessException(
        ExceptionDetail(message="INVALID REFRESH TOKEN", code="AUTH0007"),
        status_code=status.HTTP_400_BAD_REQUEST,
    )
    EXPIRED_REFRESH_TOKEN = BusinessException(
        ExceptionDetail(message="EXPIRED REFRESH TOKEN", code="AUTH0008"),
        status_code=status.HTTP_400_BAD_REQUEST,
    )
    PERMISSION_DENIED = BusinessException(
        ExceptionDetail(message="PERMISSION DENIED", code="AUTH0009"),
        status_code=status.HTTP_403_FORBIDDEN,
    )
