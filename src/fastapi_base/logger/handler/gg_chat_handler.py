import logging
from json import dumps
from typing import Callable, Optional

import decouple
import requests

GOOGLE_CHAT_WEBHOOK: str = decouple.config("GOOGLE_CHAT_WEBHOOK")
FilterFunction = Callable[[logging.LogRecord], bool]


class GGChatHandler(logging.Handler):
    def __init__(
        self,
        service_name: str = "",
        level: str = "WARNING",
        enqueue: bool = True,
        log_filter: Optional[FilterFunction] = None,
    ):
        super().__init__(level)
        self.service_name = service_name
        self._filter = log_filter
        self.enqueue = enqueue
        if not GOOGLE_CHAT_WEBHOOK:
            raise ValueError("Invalid Google chat webhook url")

    def emit(self, record: logging.LogRecord) -> None:
        if self._filter is not None and self._filter(record):
            return

        requests.post(
            url=GOOGLE_CHAT_WEBHOOK,
            data=dumps({"text": f"{self.service_name.upper()}\n{record.getMessage()}"}),
            headers={"Content-Type": "application/json; charset=UTF-8"},
            timeout=30,
        )
