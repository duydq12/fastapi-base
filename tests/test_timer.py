import time
from io import StringIO

from loguru import logger

from fastwings.config import settings
from fastwings.timer import timeit


def test_timeit_decorator_logs(monkeypatch):
    """Test that the timeit decorator logs execution time when DEBUG_MODE is True."""
    monkeypatch.setattr(settings, "DEBUG_MODE", True, raising=False)
    log_stream = StringIO()
    sink_id = logger.add(log_stream, level="DEBUG")

    @timeit
    def slow_func():
        """Dummy function to simulate a slow operation for timing."""
        time.sleep(0.01)
        return "done"

    result = slow_func()
    logger.remove(sink_id)
    log_contents = log_stream.getvalue()
    assert result == "done"
    assert "slow_func took" in log_contents


def test_timeit_decorator_no_log(monkeypatch):
    """Test that the timeit decorator does not log when DEBUG_MODE is False."""
    monkeypatch.setattr(settings, "DEBUG_MODE", False, raising=False)
    log_stream = StringIO()
    sink_id = logger.add(log_stream, level="DEBUG")

    @timeit
    def fast_func():
        """Dummy function to simulate a fast operation for timing."""
        return "fast"

    result = fast_func()
    logger.remove(sink_id)
    log_contents = log_stream.getvalue()
    assert result == "fast"
    assert "fast_func took" not in log_contents
