from fastapi_base.config import settings
from fastapi_base.exception import BusinessException, get_traceback
from fastapi_base.response import ExceptionDetail


def test_get_traceback_returns_string():
    """Test that get_traceback returns a string containing exception details."""
    try:
        raise ValueError("test error")
    except Exception as ex:
        tb = get_traceback(ex)
        assert isinstance(tb, str)
        assert "ValueError" in tb
        assert "test error" in tb


def test_business_exception_attributes():
    """Test that BusinessException sets status_code, code, and message attributes."""
    exc = BusinessException(
        status_code=400, exception=ExceptionDetail(code="TEST_ERROR", message="Test error message", data=None)
    )
    assert isinstance(exc, Exception)
    assert exc.status_code == 400
    assert exc.code == "TEST_ERROR"
    assert exc.message == "Test error message"


def test_business_exception_as_dict_basic():
    """Test that BusinessException.as_dict returns correct dict without data."""
    exc = BusinessException(status_code=401, exception=ExceptionDetail(code="AUTH", message="Unauthorized", data=None))
    result = exc.as_dict()
    assert result["status_code"] == 401
    assert result["code"] == "AUTH"
    assert result["message"] == "Unauthorized"
    assert "data" not in result


def test_business_exception_as_dict_with_data():
    """Test that BusinessException.as_dict includes data when present."""
    exc = BusinessException(
        status_code=403, exception=ExceptionDetail(code="FORBIDDEN", message="Forbidden", data={"reason": "no access"})
    )
    result = exc.as_dict()
    assert result["status_code"] == 403
    assert result["code"] == "FORBIDDEN"
    assert result["message"] == "Forbidden"
    assert result["data"] == {"reason": "no access"}


def test_business_exception_call_with_exception(monkeypatch):
    """Test BusinessException call with an exception being raised."""
    monkeypatch.setattr(settings, "DEBUG_MODE", True, raising=False)
    exc_detail = ExceptionDetail(code="ERR", message="msg", data=None)
    exc = BusinessException(exception=exc_detail, status_code=400)
    try:
        raise ValueError("fail")
    except Exception as e:
        exc = exc(e, user="bob", action="test")
    assert "traceback" in exc.data
    assert "ValueError" in exc.data["traceback"]
    assert "context" in exc.data
    assert exc.data["context"] == {"user": "bob", "action": "test"}


def test_business_exception_call_without_exception(monkeypatch):
    """Test BusinessException call without an exception, only context data."""
    monkeypatch.setattr(settings, "DEBUG_MODE", True, raising=False)
    exc_detail = ExceptionDetail(code="ERR2", message="msg2", data=None)
    exc = BusinessException(exception=exc_detail, status_code=401)
    exc = exc(user="alice", action="other")
    assert "traceback" not in exc.data or exc.data["traceback"] == ""
    assert "context" in exc.data
    assert exc.data["context"] == {"user": "alice", "action": "other"}


def test_business_exception_call_traceback_disabled(monkeypatch):
    """Test BusinessException call with traceback disabled in settings."""
    monkeypatch.setattr(settings, "DEBUG_MODE", False, raising=False)
    exc_detail = ExceptionDetail(code="ERR3", message="msg3", data=None)
    exc = BusinessException(exception=exc_detail, status_code=402)
    try:
        raise RuntimeError("fail2")
    except Exception as e:
        exc = exc(e, info="disabled")
    assert exc.data["traceback"] == ""
    assert exc.data["context"] == {"info": "disabled"}
