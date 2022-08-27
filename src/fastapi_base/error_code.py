from enum import Enum

from fastapi_base.exception import BusinessException
from fastapi_base.response import ExceptionDetail
from starlette import status


class ServerErrorCode(Enum):
    SERVER_ERROR = BusinessException(ExceptionDetail(message="INTERNAL SERVER ERROR", code="SERVER0100"),
                                     status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
    DATABASE_ERROR = BusinessException(ExceptionDetail(message="DATABASE ERROR", code="SERVER0101"),
                                       status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
