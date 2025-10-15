"""Provides custom log filtering for FastAPI applications.

Classes:
    HealthCheckFilter: Filters out health check log messages from output.
"""

import logging


class HealthCheckFilter:
    """Filter that excludes log messages ending with 'health'.

    Used to suppress health check logs from output.
    """
    def __call__(self, record: logging.LogRecord) -> bool:
        """Returns True if the log record should be included, False to filter out.

        Args:
            record: Log record or dict
        Returns:
            bool: True to include, False to exclude
        """
        if isinstance(record, dict):
            return not record["message"].endswith("health")
        if isinstance(record, logging.LogRecord):
            return not record.getMessage().endswith("health")
        return True
