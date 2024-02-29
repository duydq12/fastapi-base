import logging
import socket

from typing import Callable, Optional

import decouple

from logstash import TCPLogstashHandler
from starlette import status

FilterFunction = Callable[[logging.LogRecord], bool]


class LogStashHandler(logging.Handler):
    def __init__(
        self,
        logstash_version: int = 1,
        service_name: str = "",
        level: str = "INFO",
        enqueue: bool = True,
        log_filter: Optional[FilterFunction] = None,
    ):
        super().__init__(level)
        self.ext_message = {
            "response_code": status.HTTP_200_OK,
            "server_name": service_name,
            "server_ip": socket.gethostbyname(socket.gethostname()),
        }
        self.enqueue = enqueue
        self._filter = log_filter
        self._host: str = decouple.config("LOGSTASH_HOST")
        self._port: int = decouple.config("LOGSTASH_PORT")

        if not self._host:
            raise ValueError("Invalid Logstash host")

        if not self._port or isinstance(self._port, int):
            raise ValueError("Invalid Logstash port")

        self.tcp_logstash = TCPLogstashHandler(self._host, self._port, version=logstash_version)

    def emit(self, record: logging.LogRecord) -> None:
        if self._filter is not None and self._filter(record):
            return

        record.__dict__.update(self.ext_message)
        self.tcp_logstash.emit(record)
