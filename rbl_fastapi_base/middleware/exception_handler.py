import logging
import time

from fastapi import Request

from ..base.business_exception import BusinessException
from ..base.response_object import ResponseObject


async def error_handle_business(rq, ee):
    if isinstance(ee, BusinessException):
        http_code = ee.http_code
        code = ee.code
        message = ee.message
        return ResponseObject().error(status_code=http_code, code=code, message=message)
    raise ee


async def process_middleware_common(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["x-process-time"] = str(process_time)
    response_header = {"request_header": request.headers.__dict__, 'response_headers': response.headers.__dict__}
    if hasattr(request, 'url'):
        return response
    logging.info(response_header)
    return response
