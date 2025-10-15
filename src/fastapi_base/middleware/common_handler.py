"""Middleware utilities for FastAPI applications.

This module provides common middleware functions such as:
- timer_middleware: Adds request processing time to response headers.

Functions:
    timer_middleware: Middleware to measure and add request processing time to response headers.
"""

import time

from typing import Any, Callable, Coroutine

from fastapi import Request, Response


async def timer_middleware(request: Request, call_next: Callable[[Request], Coroutine[Any, Any, Response]]) -> Response:
    """Middleware to measure and add the request processing time to the response headers.

    Args:
        request (Request): Incoming FastAPI request object.
        call_next (Callable): Function to process the next middleware/request handler.

    Returns:
        Response: FastAPI response object with 'x-process-time' header.
    """
    start_time = time.time()
    response = await call_next(request)
    process_time = round(time.time() - start_time, 5)
    response.headers["x-process-time"] = str(process_time)
    return response
