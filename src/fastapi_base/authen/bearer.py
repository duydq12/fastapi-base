"""Security file."""

import os

from datetime import datetime, timedelta
from typing import Any, Dict

from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import jwt
from pydantic import ValidationError
from starlette import status

reusable_oauth2 = HTTPBearer(scheme_name="Authorization")

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_SECONDS = os.getenv("ACCESS_TOKEN_EXPIRE_SECONDS", 60)


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
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Expired Access Token",
            headers={"Authenticate": "Basic username:password"},
        )
    except (jwt.JWTError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"Authenticate": "Basic username:password"},
        )
    return payload
