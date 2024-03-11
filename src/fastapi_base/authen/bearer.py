"""Security file."""

from datetime import datetime, timedelta
from typing import Any, Dict

import decouple

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import jwt
from pydantic import ValidationError

from fastapi_base.error_code import AuthErrorCode

reusable_oauth2 = HTTPBearer(scheme_name="Authorization")

SECRET_KEY = decouple.config("SECRET_KEY")
ALGORITHM = decouple.config("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_SECONDS = decouple.config("ACCESS_TOKEN_EXPIRE_SECONDS", 60)


def jwt_decode(credentials: str) -> Dict[str, Any]:
    payload = jwt.decode(credentials, SECRET_KEY, algorithms=ALGORITHM)
    return payload


def jwt_encode(subject: str, data: Dict[str, Any] = None, expires_second: int = 0) -> str:
    """Create token when login with user."""
    expire = datetime.utcnow() + timedelta(
        seconds=expires_second or int(ACCESS_TOKEN_EXPIRE_SECONDS),
    )

    to_encode = {"sub": subject, "exp": expire}
    if data:
        to_encode.update(data)

    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


async def bearer_auth(credentials: HTTPAuthorizationCredentials = Depends(reusable_oauth2)) -> Dict[str, Any]:
    """Decode jwt token."""
    try:
        payload: Dict[str, Any] = jwt_decode(credentials.credentials)
    except jwt.ExpiredSignatureError:
        raise AuthErrorCode.EXPIRED_ACCESS_TOKEN.value
    except (jwt.JWTError, ValidationError):
        raise AuthErrorCode.INVALID_ACCESS_TOKEN.value
    return payload
