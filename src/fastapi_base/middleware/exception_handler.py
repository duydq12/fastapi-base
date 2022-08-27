from fastapi import Request
from fastapi.responses import JSONResponse
from loguru import logger

from fastapi_base.exception import BusinessException


async def business_exception_handler(_: Request, exc: BusinessException) -> JSONResponse:
    logger.error(f"{exc.message}\n{exc.data}".rstrip())
    return JSONResponse(
        status_code=exc.status_code,
        content={"code": exc.code, "message": exc.message, "data": exc.data},
    )
