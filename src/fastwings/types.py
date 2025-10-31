from enum import Enum
from typing import Optional

from pydantic import BaseModel


class EIncrementType(str, Enum):
    YEAR = 'year'
    MONTH = 'month'
    DATE = 'date'
    HOUR = 'hour'
    WEEK = 'week'
    MINUTE = 'minute'
    SECOND = 'second'


# Replaces common/casl/constants/casl.enum.ts
class Action(str, Enum):
    MANAGE = 'manage'
    CREATE = 'create'
    READ = 'read'
    UPDATE = 'update'
    DELETE = 'delete'


# Replaces common/enums/index.ts (from user.enum.ts)
class EAuthorRole(str, Enum):
    USER = 'USER'
    ADMIN = 'ADMIN'


class EAuthProvider(str, Enum):
    EMAIL = 'EMAIL'
    GOOGLE = 'GOOGLE'
    # ... other providers


# Replaces common/types/base/jwt-payload.type.ts
class JwtPayload(BaseModel):
    email: Optional[str] = None
    id: str
    provider: EAuthProvider
    device_id: Optional[str] = None
    iat: Optional[int] = None
    authorRole: EAuthorRole
