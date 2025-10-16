"""Unit tests for HTTP Basic authentication in fastapi_base.authen.basic.

Covers successful and failed authentication scenarios.
"""

import pytest
from fastapi.security import HTTPBasicCredentials

from fastapi_base.authen import basic
from fastapi_base.config import settings
from fastapi_base.error_code import AuthErrorCode
from fastapi_base.exception import BusinessException

HASH_USERNAME = "$2b$12$ZSmiD7O4XwgqLK48pVB5tuofZxPPW0g8FbC28P7CUVuwMWkMpcGK2"  # noqa: S105
HASH_PASSWORD = "$2b$12$uao1W/hWmZ7Ta8ftA6vvBe..L8f7lw9t/KaWX5BkEbbVQyoQ7Nx7K"  # noqa: S105


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "username, password, hash_username, hash_password, error",
    [
        ("test", "password", HASH_USERNAME, HASH_PASSWORD, None),
        ("wrong", "user", HASH_USERNAME, HASH_PASSWORD, AuthErrorCode.INCORRECT_USERNAME_PASSWORD.value),
    ]
)
@pytest.mark.asyncio
async def test_basic_auth_success(username, password, hash_username, hash_password, error, monkeypatch):
    """Tests successful basic authentication.

    Asserts that no exception is raised and password verification is called.
    """
    monkeypatch.setattr(settings, "BASIC_USERNAME", hash_username, raising=False)
    monkeypatch.setattr(settings, "BASIC_PASSWORD", hash_password, raising=False)
    credentials = HTTPBasicCredentials(username=username, password=password)
    if error:
        with pytest.raises(BusinessException) as excinfo:
            await basic.basic_auth(credentials)
            assert excinfo.value.status_code == error.status_code
            assert excinfo.value.message == error.message
            assert excinfo.value.code == error.code
    else:
        await basic.basic_auth(credentials)
