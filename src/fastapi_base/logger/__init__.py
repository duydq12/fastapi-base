import logging

from typing import Union

from loguru import logger


class InterceptHandler(logging.Handler):
    """
    Default handler from examples in loguru documentaion.
    See https://loguru.readthedocs.io/en/stable/overview.html#entirely-compatible-with-standard-logging
    """

    def emit(self, record: logging.LogRecord):
        # Get corresponding Loguru level if it exists
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        # Find caller from where originated the logged message
        frame, depth = logging.currentframe(), 2
        while frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(level, record.getMessage())


def get_uvicorn_configure_logger():
    """
    When running, uvicorn will load the default logging configure, so it is necessary to override the configure
    """
    from uvicorn.config import LOGGING_CONFIG

    custom_logging_config = LOGGING_CONFIG.copy()
    custom_loggers = {}
    for logger_name, logger_config in LOGGING_CONFIG["loggers"].items():
        custom_logger_config = logger_config.copy()
        custom_logger_config["handlers"] = []
        custom_logger_config["propagate"] = True
        custom_loggers[logger_name] = custom_logger_config

    custom_logging_config["loggers"] = custom_loggers
    return custom_logging_config


def configure_logger(handlers, root_logger_level: Union[str, int] = "INFO") -> None:
    if isinstance(root_logger_level, str):
        root_logger_level = logging.getLevelName(root_logger_level)
    # intercept everything at the root logger
    logging.root.handlers = [InterceptHandler()]
    logging.root.setLevel(root_logger_level)

    # remove every other logger's handlers
    # and propagate to root logger
    for name in logging.root.manager.loggerDict.keys():
        _logger = logging.getLogger(name)
        _logger.handlers = []
        _logger.propagate = True

    logger.remove()
    for handler_type, handler in handlers:
        if handler_type == "builtin":
            logger.add(**dict(handler))
        else:
            logger.add(handler, level=handler.level, enqueue=handler.enqueue)
