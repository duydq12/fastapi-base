"""Defines custom exception classes and utilities for error handling in FastAPI applications.

Provides BusinessException for standardized API error responses.

Classes:
    BusinessException: Custom exception for API error responses.
Functions:
    get_traceback: Returns formatted traceback string for an exception.
"""

from __future__ import annotations

import traceback
from typing import Any

from starlette import status

from fastapi_base.config import settings
from fastapi_base.response import ExceptionDetail


def get_traceback(ex: Exception) -> str:
    """Returns formatted traceback string for an exception.

    Args:
        ex (Exception): Exception instance.

    Returns:
        str: Formatted traceback string.
    """
    lines = traceback.format_exception(type(ex), ex, ex.__traceback__)
    return "".join(lines)


class BusinessException(Exception):  # noqa
    """Custom exception for API error responses.

    Attributes:
        status_code (int): HTTP status code for the error.
        code (str): Error code string.
        message (str): Error message string.
        data: Additional error data or traceback.
    """

    def __init__(self, exception: ExceptionDetail, status_code: int = status.HTTP_400_BAD_REQUEST):
        """Initializes BusinessException with details and status code.

        Args:
            exception (ExceptionDetail): Exception detail schema.
            status_code (int, optional): HTTP status code.
        """
        self.status_code = status_code
        self.code = exception.code if exception.code else str(self.status_code)
        self.message = exception.message
        self.data = exception.data

    def __call__(self, *args: Any, **kwargs: Any) -> BusinessException:
        """Updates the exception data with traceback and context if provided.

        If an Exception is passed as the first positional argument and DEBUG_MODE is enabled,
        the traceback is added to the data. Any keyword arguments are added as context.

        Args:
            *args: Positional arguments. If the first argument is an Exception, its traceback is included.
            **kwargs: Additional context data to include in the exception.

        Returns:
            BusinessException: Updated exception instance with data and context.
        """
        self.data = {}
        if args and isinstance(args[0], Exception):
            self.data["traceback"] = get_traceback(args[0]) if settings.DEBUG_MODE else ""

        # Handle additional context data
        if kwargs:
            self.data["context"] = kwargs

        return self

    def as_dict(self) -> dict[str, int | str]:
        """Returns a dictionary representation of the exception.

        Returns:
            Dict[str, Union[int, str]]: Exception details as a dictionary.
        """
        result = {"status_code": self.status_code, "code": self.code, "message": self.message}
        if self.data:
            result["data"] = self.data
        return result
