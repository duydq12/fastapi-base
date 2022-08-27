import logging


class HealthCheckFilter(object):
    def __call__(self, record: logging.LogRecord) -> bool:
        if isinstance(record, dict):
            return not record["message"].endswith("health")
        if isinstance(record, logging.LogRecord):
            return not record.getMessage().endswith("health")
        return True
