"""GGChatHandler for sending log messages to Google Chat via webhook.

Posts log records to a Google Chat room using the configured webhook URL.
"""

import logging
from collections.abc import Callable
from json import dumps

import requests

from fastapi_base.config import settings

FilterFunction = Callable[[logging.LogRecord], bool]


class GGChatHandler(logging.Handler):
    """Handler for sending log messages to Google Chat via webhook."""

    def __init__(
        self,
        service_name: str = "",
        level: str = "WARNING",
        enqueue: bool = True,
        log_filter: FilterFunction | None = None,
    ):
        """Initialize GGChatHandler configuration.

        Args:
            service_name: Name of the service for log context
            level: Log level
            enqueue: If True, logs are enqueued for async processing
            log_filter: Optional filter function
        """
        super().__init__(level)
        self.service_name = service_name
        self.enqueue = enqueue
        self._filter = log_filter
        self._webhook: str = settings.GOOGLE_CHAT_WEBHOOK

        if not self._webhook:
            raise ValueError("Invalid Google chat webhook url")

    def emit(self, record: logging.LogRecord) -> None:
        """Send a log record to Google Chat via webhook.

        Args:
            record: Log record to send
        """
        if self._filter is not None and self._filter(record):
            return

        requests.post(
            url=self._webhook,
            data=dumps({"text": f"{self.service_name.upper()}\n{record.getMessage()}"}),
            headers={"Content-Type": "application/json; charset=UTF-8"},
            timeout=30,
        )
