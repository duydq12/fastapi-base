import datetime

from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field, validator


class ExceptionDetail(BaseModel):
    code: str = Field(description="Exception Code", default="BE0000")
    message: str = Field(description="Exception Message", default="success")
    data: Optional[Union[List[Any], Dict[str, Any], str]] = Field(description="Detail Exception Message", default="")


class ResponseObject(ExceptionDetail):
    timestamp: str = ""

    @validator("timestamp", always=True)
    def set_timestamp(cls, v: str) -> str:
        return v or datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
