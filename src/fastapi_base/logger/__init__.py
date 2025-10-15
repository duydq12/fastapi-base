"""Logger module initialization for fastapi_base.

Provides logging configuration and handler utilities for FastAPI applications.

Features:
- Intercepts standard logging and routes to Loguru.
- Provides configure_logger for custom handler setup.
- get_uvicorn_configure_logger for Uvicorn integration.
"""

import logging
from types import FrameType
from typing import Any

from loguru import logger


class InterceptHandler(logging.Handler):
    """Intercepts standard logging and routes messages to Loguru.

    Compatible with standard logging.Handler.
    """

    def emit(self, record: logging.LogRecord) -> None:
        """Emit a log record, forwarding it to Loguru with correct level and exception info."""
        try:
            level: int | str = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        # Find caller from where originated the logged message
        frame: FrameType | None = logging.currentframe()
        depth = 2
        while frame is not None and frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(level, record.getMessage())


def get_uvicorn_configure_logger() -> dict[str, Any]:
    """When running, uvicorn will load the default logging configure, so it is necessary to override the configure."""
    from uvicorn.config import LOGGING_CONFIG

    custom_logging_config = LOGGING_CONFIG.copy()
    custom_loggers = {}
    for logger_name, logger_config in LOGGING_CONFIG["loggers"].items():
        custom_logger_config = logger_config.copy()
        custom_logger_config["handlers"] = []
        custom_logger_config["propagate"] = True
        custom_loggers[logger_name] = custom_logger_config

    custom_logging_config["loggers"] = custom_loggers
    return custom_logging_config


def configure_logger(handlers: list[tuple[str, Any]], root_logger_level: str | int = "INFO") -> None:
    """Configures the root logger and Loguru with provided handlers.

    Removes all other handlers and propagates to root logger.

    Args:
        handlers: List of tuples ("builtin"|"custom", handler instance)
        root_logger_level: Logging level for root logger
    """
    if isinstance(root_logger_level, str):
        root_logger_level = logging.getLevelName(root_logger_level)
    # intercept everything at the root logger
    logging.root.handlers = [InterceptHandler()]
    logging.root.setLevel(root_logger_level)

    # remove every other logger's handlers
    # and propagate to root logger
    for name in logging.root.manager.loggerDict:
        _logger = logging.getLogger(name)
        _logger.handlers = []
        _logger.propagate = True

    logger.remove()
    for handler_type, handler in handlers:
        if handler_type == "builtin":
            logger.add(**dict(handler))
        else:
            logger.add(handler, level=handler.level, enqueue=handler.enqueue)
