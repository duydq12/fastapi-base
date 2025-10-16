"""Defines response schemas and exception details for API usage.

Provides standard models for API responses and error details.

Classes:
    ExceptionDetail: Schema for detailed exception information returned by the API.
    ResponseObject: Standard API response schema, inherits from ExceptionDetail and adds a timestamp.
"""

import datetime
from typing import Any, Generic, TypeVar

from pydantic import BaseModel, Field

T = TypeVar("T")


class BaseResponse(BaseModel):
    """Schema for detailed exception information returned by the API.

    Attributes:
        code (str): Error code string.
        message (str): Error message string.
    """
    code: str = Field(description="Response Code", default="BE0000")
    message: str = Field(description="Response Message", default="success")


class ExceptionDetail(BaseResponse):
    """Schema for detailed exception information returned by the API.

    Attributes:
        data (Optional[List[Any], Dict[str, Any], str]): Optional detailed data about the error.
    """
    data: list[Any] | dict[str, Any] | str | None = Field(description="Detail Exception Message", default="")


class ResponseObject(BaseResponse, Generic[T]):
    """Standard API response schema, inherits from ExceptionDetail and adds a timestamp.

    Attributes:
        timestamp (str): Response time in format YYYY-MM-DD HH:MM:SS
    """
    data: T
    timestamp: str = Field(default_factory=lambda: datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
