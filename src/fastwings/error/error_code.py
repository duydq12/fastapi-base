"""Defines standardized error codes for server and authentication errors.

Provides enums for common API error responses.

Classes:
    ServerErrorCode: Enum of server-related error codes and BusinessException instances.
    AuthErrorCode: Enum of authentication-related error codes and BusinessException instances.
"""

from starlette import status

from fastwings.error.error_message import ErrorMessages
from fastwings.exception import BusinessException
from fastwings.response import ExceptionDetail


class BaseSystemError:
    UN_AUTHORIZATION = BusinessException(
        ExceptionDetail(message=ErrorMessages.unauthorized, code="AUTHORIZATION"),
        status_code=status.HTTP_401_UNAUTHORIZED,
    )
    NOT_ENOUGH_PERMISSION = BusinessException(
        ExceptionDetail(message=ErrorMessages.not_enough_permission, code="NOT_ENOUGH_PERMISSION"),
        status_code=status.HTTP_403_FORBIDDEN,
    )
    ACCESS_TOKEN_EXPIRED = BusinessException(
        ExceptionDetail(message=ErrorMessages.expired_target("Access token"), code="ACCESS_TOKEN_EXPIRED"),
        status_code=status.HTTP_401_UNAUTHORIZED,
    )
    INVALID_ACCESS_TOKEN = BusinessException(
        ExceptionDetail(message=ErrorMessages.invalid_record("access token"), code="INVALID_ACCESS_TOKEN"),
        status_code=status.HTTP_401_UNAUTHORIZED,
    )


class BaseServicerError:
    # CONTROL
    CREATE_FAILED = BusinessException(
        ExceptionDetail(message=ErrorMessages.Base.create_entity_failed(), code="CREATE_FAILED"),
        status_code=status.HTTP_400_BAD_REQUEST
    )
    UPDATE_FAILED = BusinessException(
        ExceptionDetail(message=ErrorMessages.Base.update_entity_failed(), code="UPDATE_FAILED"),
        status_code=status.HTTP_400_BAD_REQUEST
    )
    SOFT_DELETE_FAILED = BusinessException(
        ExceptionDetail(message=ErrorMessages.Base.soft_delete_failed(), code="SOFT_DELETE_FAILED"),
        status_code=status.HTTP_400_BAD_REQUEST
    )
    HARD_DELETE_FAILED = BusinessException(
        ExceptionDetail(message=ErrorMessages.Base.hard_delete_failed(), code="HARD_DELETE_FAILED"),
        status_code=status.HTTP_400_BAD_REQUEST
    )
    RESTORE_FAILED = BusinessException(
        ExceptionDetail(message=ErrorMessages.Base.restore_failed(), code="RESTORE_FAILED"),
        status_code=status.HTTP_400_BAD_REQUEST
    )
    DEACTIVATE_FAILED = BusinessException(
        ExceptionDetail(message=ErrorMessages.Base.deactivate_failed(), code="DEACTIVATE_FAILED"),
        status_code=status.HTTP_400_BAD_REQUEST
    )
    ACTIVE_FAILED = BusinessException(
        ExceptionDetail(message=ErrorMessages.Base.active_failed(), code="ACTIVE_FAILED"),
        status_code=status.HTTP_400_BAD_REQUEST
    )
    UPDATE_CONFLICT = BusinessException(
        ExceptionDetail(message=ErrorMessages.Base.update_conflict(), code="UPDATE_CONFLICT"),
        status_code=status.HTTP_400_BAD_REQUEST
    )

    # VALIDATE
    NOT_FOUND = BusinessException(
        ExceptionDetail(message=ErrorMessages.Base.not_found_record(), code="NOT_FOUND"),
        status_code=status.HTTP_400_BAD_REQUEST
    )
    DUPLICATE_RECORD = BusinessException(
        ExceptionDetail(message=ErrorMessages.Base.duplicate_record(), code="DUPLICATE_RECORD"),
        status_code=status.HTTP_400_BAD_REQUEST
    )
    NOT_ACTIVE_RECORD = BusinessException(
        ExceptionDetail(message=ErrorMessages.Base.not_active_record(), code="NOT_ACTIVE_RECORD"),
        status_code=status.HTTP_400_BAD_REQUEST
    )
    SOFT_DELETE_RECORD = BusinessException(
        ExceptionDetail(message=ErrorMessages.Base.soft_delete_record(), code="SOFT_DELETE_RECORD"),
        status_code=status.HTTP_400_BAD_REQUEST
    )


# class AuthErrorCode(Enum):
#     """Enum of authentication-related error codes for API responses.
#
#     Each value is a BusinessException instance with a specific message and code.
#     """
#     INCORRECT_EMAIL = BusinessException(
#         ExceptionDetail(message="INCORRECT EMAIL", code="AUTH0001"),
#         status_code=status.HTTP_401_UNAUTHORIZED,
#     )
#     INCORRECT_PHONE = BusinessException(
#         ExceptionDetail(message="INCORRECT PHONE", code="AUTH0002"),
#         status_code=status.HTTP_401_UNAUTHORIZED,
#     )
#     INCORRECT_PASSWORD = BusinessException(
#         ExceptionDetail(message="INCORRECT PASSWORD", code="AUTH0003"),
#         status_code=status.HTTP_401_UNAUTHORIZED,
#     )
#     INCORRECT_USERNAME_PASSWORD = BusinessException(
#         ExceptionDetail(message="INCORRECT USERNAME OR PASSWORD", code="AUTH0004"),
#         status_code=status.HTTP_401_UNAUTHORIZED,
#     )
#     INVALID_ACCESS_TOKEN = BusinessException(
#         ExceptionDetail(message="INVALID ACCESS TOKEN", code="AUTH0005"),
#         status_code=status.HTTP_401_UNAUTHORIZED,
#     )
#     EXPIRED_ACCESS_TOKEN = BusinessException(
#         ExceptionDetail(message="EXPIRED ACCESS TOKEN", code="AUTH0006"),
#         status_code=status.HTTP_401_UNAUTHORIZED,
#     )
#     INVALID_REFRESH_TOKEN = BusinessException(
#         ExceptionDetail(message="INVALID REFRESH TOKEN", code="AUTH0007"),
#         status_code=status.HTTP_400_BAD_REQUEST,
#     )
#     EXPIRED_REFRESH_TOKEN = BusinessException(
#         ExceptionDetail(message="EXPIRED REFRESH TOKEN", code="AUTH0008"),
#         status_code=status.HTTP_400_BAD_REQUEST,
#     )
#     PERMISSION_DENIED = BusinessException(
#         ExceptionDetail(message="PERMISSION DENIED", code="AUTH0009"),
#         status_code=status.HTTP_403_FORBIDDEN,
#     )
