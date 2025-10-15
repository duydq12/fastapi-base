"""Defines response schemas and exception details for API usage.

Provides standard models for API responses and error details.

Classes:
    ExceptionDetail: Schema for detailed exception information returned by the API.
    ResponseObject: Standard API response schema, inherits from ExceptionDetail and adds a timestamp.
"""

import datetime
from typing import Any

from pydantic import BaseModel, Field, validator


class ExceptionDetail(BaseModel):
    """Schema for detailed exception information returned by the API.

    Attributes:
        code (str): Error code string.
        message (str): Error message string.
        data (Optional[List[Any], Dict[str, Any], str]): Optional detailed data about the error.
    """
    code: str = Field(description="Exception Code", default="BE0000")
    message: str = Field(description="Exception Message", default="success")
    data: list[Any] | dict[str, Any] | str | None = Field(description="Detail Exception Message", default="")


class ResponseObject(ExceptionDetail):
    """Standard API response schema, inherits from ExceptionDetail and adds a timestamp.

    Attributes:
        timestamp (str): Response time in format YYYY-MM-DD HH:MM:SS
    """
    timestamp: str = ""

    @validator("timestamp", always=True)
    def set_timestamp(cls, v: str) -> str:
        """Sets the timestamp field to the current time if not provided.

        Args:
            v (str): Provided timestamp value.

        Returns:
            str: Timestamp string in format YYYY-MM-DD HH:MM:SS
        """
        return v or datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
