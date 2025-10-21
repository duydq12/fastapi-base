"""Provides a decorator for measuring and logging function execution time.

Useful for profiling and debugging in FastAPI applications.

Functions:
    timeit: Decorator to measure and log execution time of a function.
"""

from __future__ import annotations

import time
from collections.abc import Callable
from functools import wraps
from typing import Any, TypeVar

from loguru import logger

from fastwings.config import settings

T = TypeVar("T")
Function = Callable[..., T]


def timeit(func: Function[T]) -> Function[T]:
    """Decorator to measure the execution time of a function.

    If log level is DEBUG, logs the execution time.

    Args:
        func: Function to be decorated.

    Returns:
        Function: Wrapped function with timing logic.
    """

    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        if settings.DEBUG_MODE:
            start_time = time.time()
            result = func(*args, **kwargs)
            process_time = round(time.time() - start_time, 5)
            logger.debug(f"{func.__qualname__} took {process_time} seconds")
            return result
        return func(*args, **kwargs)

    return wrapper
