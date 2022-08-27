import time

from typing import Any, Callable, Coroutine

from fastapi import Request, Response


async def timer_middleware(request: Request, call_next: Callable[[Request], Coroutine[Any, Any, Response]]) -> Response:
    start_time = time.time()
    response = await call_next(request)
    process_time = round(time.time() - start_time, 5)
    response.headers["x-process-time"] = str(process_time)
    return response
