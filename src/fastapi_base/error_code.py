from enum import Enum

from starlette import status

from fastapi_base.exception import BusinessException
from fastapi_base.response import ExceptionDetail


class ServerErrorCode(Enum):
    SERVER_ERROR = BusinessException(
        ExceptionDetail(message="INTERNAL SERVER ERROR", code="SERVER0100"),
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
    )
    DATABASE_ERROR = BusinessException(
        ExceptionDetail(message="DATABASE ERROR", code="SERVER0101"), status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
    )


class AuthErrorCode(Enum):
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
