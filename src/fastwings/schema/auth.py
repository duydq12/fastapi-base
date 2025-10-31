# common/schemas/auth.py
from pydantic import BaseModel, EmailStr, Field
from typing import Optional
import re

from ..types import EAuthorRole, EOperatingSystem
from ..exceptions import error_message

# Regex from base-password.dto.ts
PASSWORD_REGEX = r"^(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$"
PASSWORD_ERROR_MSG = error_message.get("password", {}).get(
    "passwordErrType", "Invalid password format"
)

class BaseEmailSchema(BaseModel):
    """
    Equivalent to: base-email.dto.ts
    """
    email: EmailStr

class BasePasswordSchema(BaseModel):
    """
    Equivalent to: base-password.dto.ts
    """
    password: str = Field(
        min_length=8,
        pattern=PASSWORD_REGEX,
        description=PASSWORD_ERROR_MSG
    )

class BaseUpdatePasswordSchema(BaseModel):
    """
    Equivalent to: base-update-password.dto.ts
    """
    old_password: str
    new_password: str = Field(
        min_length=8,
        pattern=PASSWORD_REGEX,
        description=PASSWORD_ERROR_MSG
    )

class BaseLoginSchema(BaseModel):
    """
    Equivalent to: base-login.dto.ts
    """
    device_id: Optional[str] = None
    os: Optional[EOperatingSystem] = None
    device_token: Optional[str] = None

class BaseAuthorRoleSchema(BaseModel):
    """
    Equivalent to: base-author-role.dto.ts
    """
    author_role: EAuthorRole