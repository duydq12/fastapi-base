from typing import Any, Dict, Optional, Tuple, Type, TypeVar

from pydantic import BaseModel, _internal

from fastapi_base.model import Base

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
    def collect_aliases(cls: Type[BaseModel]) -> Dict[str, str]:
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


# metaclass to make all fields in a model optional, useful for PATCH requests
class AllOptionalMeta(_internal._model_construction.ModelMetaclass):
    def __new__(cls, cls_name: str, bases: Tuple[Type[Any], ...], namespace: Dict[str, Any], **kwargs: Any):
        annotations: Dict[str, Any] = namespace.get("__annotations__", {})

        for base in bases:
            for base_ in base.__mro__:
                if base_ is BaseModel:
                    break
                annotations.update(base_.__annotations__)

        for field in annotations:
            if not field.startswith("__"):
                annotations[field] = Optional[annotations[field]]

        namespace["__annotations__"] = annotations
        return super().__new__(cls, cls_name, bases, namespace, **kwargs)


class IgnoreNumpyMeta(_internal._model_construction.ModelMetaclass):
    def __new__(cls, cls_name: str, bases: Tuple[Type[Any], ...], namespace: Dict[str, Any], **kwargs: Any):
        annotations: Dict[str, Any] = namespace.get("__annotations__", {})

        for base in bases:
            for base_ in base.__mro__:
                if base_ is BaseModel:
                    break
                annotations.update(base_.__annotations__)

        for field in annotations:
            if not field.startswith("__") and annotations[field].find("npt.") > 0:
                annotations[field] = None

        namespace["__annotations__"] = annotations
        return super().__new__(cls, cls_name, bases, namespace, **kwargs)
