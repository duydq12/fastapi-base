from typing import TypeVar, Optional

from fastapi_base.model import Base
from pydantic import BaseModel

SchemaInstance = TypeVar("SchemaInstance", bound=BaseModel)
ModelInstance = TypeVar("ModelInstance", bound=Base)


class BaseRequestSchema(BaseModel):
    class Config:
        orm_mode = True
        arbitrary_types_allowed = True
        validate_assignment = True
        allow_population_by_field_name = True
        use_enum_values = True

    @classmethod
    def collect_aliases(cls: type[BaseModel]) -> dict[str, str]:
        result = {}  # <alias_name>: <real_name> OR <real_name>: <real_name>
        for name, field in cls.model_fields.items():
            if field.alias:
                result.update({field.alias: name})
            else:
                result.update({name: name})
        return result


class Paging(BaseRequestSchema):
    """doc."""

    offset: Optional[int]
    limit: Optional[int]
