import logging
import socket

from typing import Callable, Optional

import decouple

from logstash import TCPLogstashHandler
from starlette import status

LOGSTASH_HOST: str = decouple.config("LOGSTASH_HOST")
LOGSTASH_PORT: int = decouple.config("LOGSTASH_PORT")
FilterFunction = Callable[[logging.LogRecord], bool]


class LogStashHandler(logging.Handler):
    def __init__(
        self,
        logstash_version: int = 1,
        service_name: str = "",
        level: str = "INFO",
        log_filter: Optional[FilterFunction] = None,
    ):
        super().__init__(level)
        self.tcp_logstash = TCPLogstashHandler(LOGSTASH_HOST, LOGSTASH_PORT, version=logstash_version)
        self.ext_message = {
            "response_code": status.HTTP_200_OK,
            "server_name": service_name,
            "server_ip": socket.gethostbyname(socket.gethostname()),
        }
        self._filter = log_filter
        if not LOGSTASH_HOST:
            raise ValueError("Invalid Logstash host")

        if not LOGSTASH_PORT or isinstance(LOGSTASH_PORT, int):
            raise ValueError("Invalid Logstash port")

    def emit(self, record: logging.LogRecord) -> None:
        if self._filter is not None and self._filter(record):
            return

        record.__dict__.update(self.ext_message)
        self.tcp_logstash.emit(record)
