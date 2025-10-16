"""Unit tests for JWT Bearer authentication in fastapi_base.authen.bearer.

Covers JWT encoding, decoding, expired and invalid token handling.
"""
import time

import pytest

from fastapi_base.authen import bearer
from fastapi_base.error_code import AuthErrorCode


class TestBearerAuth:
    def test_jwt_encode_decode_success(self):
        """Tests successful JWT encoding and decoding.

        Asserts that the payload matches the input data.
        """
        subject = "testuser"
        data = {"role": "admin"}
        token = bearer.jwt_encode(subject=subject, data=data, expires_second=60)
        assert isinstance(token, str)
        payload = bearer.jwt_decode(token)
        assert payload["sub"] == subject
        assert payload["role"] == "admin"

    def test_jwt_decode_expired_token(self):
        """Tests decoding an expired JWT token.

        Asserts that the correct exception is raised for expiration.
        """
        subject = "testuser_expired"
        token = bearer.jwt_encode(subject=subject, expires_second=-1)
        time.sleep(1)
        with pytest.raises(Exception) as excinfo:
            bearer.jwt_decode(token)
        assert excinfo.value == AuthErrorCode.EXPIRED_ACCESS_TOKEN.value

    def test_jwt_decode_invalid_token(self):
        """Tests decoding an invalid JWT token.

        Asserts that the correct exception is raised for invalid token.
        """
        invalid_token = "this.is.not.a.valid.token"  # noqa: S105
        with pytest.raises(Exception) as excinfo:
            bearer.jwt_decode(invalid_token)
        assert excinfo.value == AuthErrorCode.INVALID_ACCESS_TOKEN.value
