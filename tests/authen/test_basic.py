"""Unit tests for HTTP Basic authentication in fastapi_base.authen.basic.

Covers successful and failed authentication scenarios.
"""
from unittest.mock import patch

import pytest
from fastapi.security import HTTPBasicCredentials

from fastapi_base.authen import basic
from fastapi_base.error_code import AuthErrorCode
from fastapi_base.exception import BusinessException


@pytest.mark.asyncio
@patch("fastapi_base.authen.basic.verify_password")
async def test_basic_auth_success(mock_verify_password):
    """Tests successful basic authentication.

    Asserts that no exception is raised and password verification is called.
    """
    mock_verify_password.return_value = True
    credentials = HTTPBasicCredentials(username="test", password="password") # noqa: S106
    await basic.basic_auth(credentials)
    assert mock_verify_password.call_count == 2


@pytest.mark.asyncio
@patch("fastapi_base.authen.basic.verify_password")
async def test_basic_auth_failure(mock_verify_password):
    """Tests failed basic authentication.

    Asserts that BusinessException is raised with correct error code and message.
    """
    mock_verify_password.return_value = False
    credentials = HTTPBasicCredentials(username="wrong", password="user")  # noqa: S106
    with pytest.raises(BusinessException) as excinfo:
        await basic.basic_auth(credentials)
    exception_value = excinfo.value
    expected_error = AuthErrorCode.INCORRECT_USERNAME_PASSWORD.value
    assert exception_value.status_code == expected_error.status_code
    assert exception_value.message == expected_error.message
    assert exception_value.code == expected_error.code
