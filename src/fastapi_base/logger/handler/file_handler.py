import logging

from typing import Callable, Optional, Union

from ..formatter import DEFAULT_FORMATTER

FilterFunction = Callable[[logging.LogRecord], bool]


class FileHandler(object):
    def __init__(
        self,
        sink: str = "./logs/app.log",
        level: str = "INFO",
        log_format: Union[str, logging.Formatter] = DEFAULT_FORMATTER,
        log_filter: Optional[FilterFunction] = None,
        colorize: Optional[bool] = None,
        serialize: bool = False,
        backtrace: bool = True,
        diagnose: bool = False,
        enqueue: bool = True,
        catch: bool = False,
        rotation: Union[str, int] = "7 days",
        retention: Union[str, int] = "1 months",
        compression: Optional[Union[str]] = None,
        delay: bool = False,
        mode: str = "a",
        buffering: int = 1,
        encoding: str = "utf8",
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
        self.rotation = rotation
        self.retention = retention
        self.compression = compression
        self.delay = delay
        self.mode = mode
        self.buffering = buffering
        self.encoding = encoding

    def __iter__(self):
        for attribute, value in self.__dict__.items():
            if value is not None:
                yield attribute, value
