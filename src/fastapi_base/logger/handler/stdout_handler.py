import logging
import sys

from typing import Callable, Optional, TextIO, Union

from ..formatter import DEFAULT_FORMATTER

FilterFunction = Callable[[logging.LogRecord], bool]


class StdoutHandler(object):
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
        enqueue: bool = True,
        catch: bool = False,
    ):
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
        for attribute, value in self.__dict__.items():
            if value is not None:
                yield attribute, value
