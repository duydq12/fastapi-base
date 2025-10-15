"""Logger Formatter Module.

This module provides default log formatting for the fastapi_base logger package.

Attributes:
    DEFAULT_FORMATTER (str): The default log format string used for log output.
        Format includes log level, timestamp, process ID, logger name, function name, and message.
        Example output:
            INFO     2025-10-15 12:34:56.789 - 12345 - my_logger:my_func - This is a log message
"""

DEFAULT_FORMATTER = (
    "<level>{level: <8}</level> <green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> "
    "- <green>{process}</green> "
    "- <cyan>{name}</cyan>:<cyan>{function}</cyan> "
    "- <level>{message}</level>"
)
