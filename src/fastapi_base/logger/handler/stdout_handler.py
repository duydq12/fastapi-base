"""StdoutHandler for logging to standard output in FastAPI applications.

Stores configuration for stdout-based logging, including format, filtering, and options.
"""

import logging
import sys

from typing import Callable, Optional, TextIO, Union

from ..formatter import DEFAULT_FORMATTER

FilterFunction = Callable[[logging.LogRecord], bool]


class StdoutHandler:
    """Handler for logging to standard output (stdout).

    Supports configuration for log format, filtering, and Loguru options.
    """
    def __init__(
        self,
        sink: TextIO = sys.stdout,
        level: str = "INFO",
        log_format: Union[str, logging.Formatter] = DEFAULT_FORMATTER,
        log_filter: Optional[FilterFunction] = None,
        colorize: Optional[bool] = None,
        serialize: bool = False,
        backtrace: bool = True,
        diagnose: bool = False,
        enqueue: bool = False,
        catch: bool = False,
    ):
        """Initialize StdoutHandler configuration.

        Args:
            sink: Output stream (default: sys.stdout)
            level: Log level
            log_format: Format string or Formatter
            log_filter: Optional filter function
            colorize: Enable colored log output
            serialize: Output logs in JSON format
            backtrace: Show full traceback in logs
            diagnose: Enable loguru diagnostics
            enqueue: Use multiprocessing-safe logging
            catch: Catch and log exceptions in logging
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

    def __iter__(self):
        """Iterate over non-None attributes for handler configuration."""
        for attribute, value in self.__dict__.items():
            if value is not None:
                yield attribute, value
