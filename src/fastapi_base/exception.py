from __future__ import annotations

import traceback

from typing import Dict, Union

import decouple

from starlette import status

from fastapi_base.response import ExceptionDetail

ENV = decouple.config("ENV", "DEV")


def get_traceback(ex: Exception) -> str:
    lines = traceback.format_exception(type(ex), ex, ex.__traceback__)
    return "".join(lines)


class BusinessException(Exception):  # noqa
    def __init__(self, exception: ExceptionDetail, status_code: int = status.HTTP_400_BAD_REQUEST):
        self.status_code = status_code
        self.code = exception.code if exception.code else str(self.status_code)
        self.message = exception.message
        self.data = exception.data

    def __call__(self, exception: Exception) -> BusinessException:
        self.data = get_traceback(exception) if ENV == "DEV" else ""
        return self

    def as_dict(self) -> Dict[str, Union[int, str]]:
        return {"status_code": self.status_code, "code": self.code, "message": self.message}
