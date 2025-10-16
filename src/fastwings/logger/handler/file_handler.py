"""FileHandler for logging to files in FastAPI applications.

Stores configuration for file-based logging, including format, rotation, retention, and filtering options.
"""

import logging
from collections.abc import Callable, Iterator

from ..formatter import DEFAULT_FORMATTER

FilterFunction = Callable[[logging.LogRecord], bool]


class FileHandler:
    """Handler for logging to files with rotation, retention, and filtering options."""
    def __init__(
        self,
        sink: str = "./logs/app.log",
        level: str = "INFO",
        log_format: str | logging.Formatter = DEFAULT_FORMATTER,
        log_filter: FilterFunction | None = None,
        colorize: bool | None = None,
        serialize: bool = False,
        backtrace: bool = True,
        diagnose: bool = False,
        enqueue: bool = True,
        catch: bool = False,
        rotation: str | int = "7 days",
        retention: str | int = "1 months",
        compression: str | None = None,
        delay: bool = False,
        mode: str = "a",
        buffering: int = 1,
        encoding: str = "utf8",
    ):
        """Initialize FileHandler configuration.

        Args:
            sink: Log file path
            level: Log level
            log_format: Format string or Formatter
            log_filter: Optional filter function
            colorize: Enable colored log output
            serialize: Output logs in JSON format
            backtrace: Show full traceback in logs
            diagnose: Enable loguru diagnostics
            enqueue: Use multiprocessing-safe logging
            catch: Catch and log exceptions in logging
            rotation: Log file rotation policy
            retention: Log file retention policy
            compression: Compression for rotated log files
            delay: Delay file opening until first write
            mode: File open mode (e.g., 'a' for append)
            buffering: File buffering policy
            encoding: File encoding
        """
        self.sink = sink
        self.level = level
        self.format = log_format
        self.filter = log_filter
        self.colorize = colorize
        self.serialize = serialize
        self.backtrace = backtrace
        self.diagnose = diagnose
        self.enqueue = enqueue
        self.catch = catch
        self.rotation = rotation
        self.retention = retention
        self.compression = compression
        self.delay = delay
        self.mode = mode
        self.buffering = buffering
        self.encoding = encoding

    def __iter__(self) -> Iterator[tuple[str, object]]:
        """Iterate over non-None attributes for handler configuration."""
        for attribute, value in self.__dict__.items():
            if value is not None:
                yield attribute, value
