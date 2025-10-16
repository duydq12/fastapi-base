import json
import logging
import tempfile

import pytest

from fastapi_base.config import settings
from fastapi_base.logger import InterceptHandler, get_uvicorn_configure_logger
from fastapi_base.logger.filter import HealthCheckFilter
from fastapi_base.logger.formatter.json_formatter import JSONFormatter
from fastapi_base.logger.handler.file_handler import FileHandler
from fastapi_base.logger.handler.gg_chat_handler import GGChatHandler
from fastapi_base.logger.handler.logstash_handler import LogStashHandler
from fastapi_base.logger.handler.stdout_handler import StdoutHandler


def test_intercept_handler_routing(caplog):
    """Test that InterceptHandler routes log messages correctly to Loguru via caplog."""
    handler = InterceptHandler()
    log = logging.getLogger("test_logger")
    log.handlers = [handler]
    log.setLevel(logging.INFO)
    with caplog.at_level(logging.INFO):
        log.info("Intercepted log message")
    # Loguru should receive the message
    assert any("Intercepted log message" in r for r in caplog.messages)


def test_get_uvicorn_configure_logger_structure():
    """Test that get_uvicorn_configure_logger returns a valid logger config structure."""
    config = get_uvicorn_configure_logger()
    assert isinstance(config, dict)
    assert "loggers" in config
    for _, logger_config in config["loggers"].items():
        assert "handlers" in logger_config
        assert logger_config["handlers"] == []
        assert logger_config["propagate"] is True


def test_health_check_filter():
    """Test that HealthCheckFilter correctly filters health check log records."""
    f = HealthCheckFilter()
    record = logging.LogRecord("test", logging.INFO, "", 0, "/health", (), None)
    assert not f(record)
    record2 = logging.LogRecord("test", logging.INFO, "", 0, "normal log", (), None)
    assert f(record2)
    dict_record = {"message": "/health"}
    assert not f(dict_record)
    dict_record2 = {"message": "other"}
    assert f(dict_record2)


def test_json_formatter_basic():
    """Test the basic functionality of the JSONFormatter."""
    formatter = JSONFormatter()
    record = logging.LogRecord("test", logging.INFO, "", 0, "json log", (), None)
    output = formatter.format(record)
    assert isinstance(output, str)
    data = json.loads(output)
    assert data["message"] == "json log"
    assert "timestamp" in data


def test_file_handler_init():
    """Test that the FileHandler is initialized with the correct parameters."""
    with tempfile.NamedTemporaryFile() as tmpfile:
        handler = FileHandler(sink=tmpfile.name, level="DEBUG")
        assert handler.sink == tmpfile.name
        assert handler.level == "DEBUG"
        assert hasattr(handler, "rotation")
        assert hasattr(handler, "retention")


def test_gg_chat_handler_webhook(monkeypatch):
    """Test GGChatHandler initialization and webhook configuration."""
    monkeypatch.setattr(settings, "GOOGLE_CHAT_WEBHOOK", "http://dummy-webhook")
    handler = GGChatHandler(service_name="svc", level="ERROR")
    assert handler.service_name == "svc"
    assert handler.level == 40
    assert handler._webhook == "http://dummy-webhook"
    # Test ValueError for missing webhook
    monkeypatch.setattr(settings, "GOOGLE_CHAT_WEBHOOK", "")
    with pytest.raises(ValueError):
        GGChatHandler()


def test_logstash_handler_init(mocker):
    """Test LogStashHandler initialization with mocked network settings."""
    # Mock socket and settings to avoid real network and config dependency
    mocker.patch("socket.gethostbyname", return_value="127.0.0.1")
    mocker.patch("socket.gethostname", return_value="localhost")
    mocker.patch.object(settings, "LOGSTASH_HOST", "dummyhost")
    mocker.patch.object(settings, "LOGSTASH_PORT", 5959)
    handler = LogStashHandler(service_name="svc", level="ERROR")
    assert handler._host == "dummyhost"
    assert handler._port == 5959
    assert handler.ext_message["server_name"] == "svc"
    assert handler.ext_message["server_ip"] == "127.0.0.1"


def test_stdout_handler_init():
    """Test that the StdoutHandler is initialized with the correct log level."""
    handler = StdoutHandler(level="INFO")
    assert handler.level == "INFO"
