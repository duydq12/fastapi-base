"""Provides a decorator for measuring and logging function execution time.

Useful for profiling and debugging in FastAPI applications.

Functions:
    timeit: Decorator to measure and log execution time of a function.
"""

import time

from functools import wraps
from typing import Any, Callable, TypeVar

import decouple

from loguru import logger

T = TypeVar("T")
Function = Callable[..., T]
LOG_LEVEL_NO = logger.level(decouple.config("LOG_LEVEL", "DEBUG")).no


def timeit(func: Function) -> Function:
    """Decorator to measure the execution time of a function.

    If log level is DEBUG, logs the execution time.

    Args:
        func: Function to be decorated.

    Returns:
        Function: Wrapped function with timing logic.
    """
    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        if LOG_LEVEL_NO <= 10:
            start_time = time.time()
            result = func(*args, **kwargs)
            process_time = round(time.time() - start_time, 5)
            logger.debug(f"{func.__qualname__} took {process_time} seconds")
            return result
        return func(*args, **kwargs)

    return wrapper
