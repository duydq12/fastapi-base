from fastapi import HTTPException
from passlib.context import CryptContext
from starlette import status


def verify_password(plain_password, hashed_password):
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    return pwd_context.hash(password)


def check_user_pass(username, password, hashed_username, hashed_password):
    try:
        correct_username = verify_password(username, hashed_username)
        correct_password = verify_password(password, hashed_password)
        if correct_username and correct_password:
            return True
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
