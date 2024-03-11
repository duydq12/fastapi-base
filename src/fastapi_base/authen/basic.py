import decouple

from fastapi import Depends, HTTPException
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from passlib.context import CryptContext
from starlette import status

USERNAME_HASH = decouple.config("BASIC_USERNAME")
PASSWORD_HASH = decouple.config("BASIC_PASSWORD")

basic_credential = HTTPBasic()


def verify_password(plain_password, hashed_password):
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    return pwd_context.hash(password)


async def basic_auth(credentials: HTTPBasicCredentials = Depends(basic_credential)) -> None:
    try:
        correct_username = verify_password(credentials.username, USERNAME_HASH)
        correct_password = verify_password(credentials.password, PASSWORD_HASH)
        if not (correct_username and correct_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"Authenticate": "Basic username:password"},
            )
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"Authenticate": "Basic username:password"},
        )
