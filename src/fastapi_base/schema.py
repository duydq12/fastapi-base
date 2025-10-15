"""Defines base schemas, metaclasses, and data types for API requests and responses.

Provides utilities for schema aliasing, paging, and date range handling.

Classes:
    BaseRequestSchema: Base schema for API requests, supports field aliasing.
    Paging: Schema for paginated API requests.
    AllOptionalMeta: Metaclass to make all fields optional (for PATCH requests).
    IgnoreNumpyMeta: Metaclass to ignore numpy fields in a model.
    DateBetween: Schema for passing a date range between two dates.
Functions:
    collect_aliases: Collects aliases for fields in a schema.
"""

from datetime import datetime
from typing import Any, Dict, Optional, Tuple, Type, TypeVar, Union

from pydantic import BaseModel, _internal
from pydantic.v1 import validator

from fastapi_base.model import Base

SchemaInstance = TypeVar("SchemaInstance", bound=BaseModel)
ModelInstance = TypeVar("ModelInstance", bound=Base)


class BaseRequestSchema(BaseModel):
    """Base schema for API requests, supports configuration and field aliasing."""
    class Config:
        """Pydantic configuration for BaseRequestSchema.

        Enables attribute population, assignment validation, enum value usage, and allows arbitrary types.
        """
        from_attributes = True
        arbitrary_types_allowed = True
        validate_assignment = True
        populate_by_name = True
        use_enum_values = True

    @classmethod
    def collect_aliases(cls: Type[BaseModel]) -> Dict[str, str]:
        """Collects aliases for fields in the schema.

        Returns:
            Dictionary mapping alias names to real field names.
        """
        result = {}  # <alias_name>: <real_name> OR <real_name>: <real_name>
        for name, field in cls.model_fields.items():
            if field.alias:
                result.update({field.alias: name})
            else:
                result.update({name: name})
        return result


class Paging(BaseRequestSchema):
    """Paging schema for API requests.

    Attributes:
        offset: Start position.
        limit: Number of records to return.
    """
    offset: Optional[int]
    limit: Optional[int]


class AllOptionalMeta(_internal._model_construction.ModelMetaclass):
    """Metaclass to make all fields in a model optional, useful for PATCH requests."""
    def __new__(cls, cls_name: str, bases: Tuple[Type[Any], ...], namespace: Dict[str, Any], **kwargs: Any):
        """Create a new class with all fields set as optional.

        Args:
            cls_name: Name of the class being created.
            bases: Base classes.
            namespace: Class namespace dictionary.
            **kwargs: Additional keyword arguments.

        Returns:
            type: The newly constructed class with all fields optional.
        """
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
    """Metaclass to ignore fields of numpy type in a model."""
    def __new__(cls, cls_name: str, bases: Tuple[Type[Any], ...], namespace: Dict[str, Any], **kwargs: Any):
        """Create a new class with numpy fields ignored (set to None).

        Args:
            cls_name: Name of the class being created.
            bases: Base classes.
            namespace: Class namespace dictionary.
            **kwargs: Additional keyword arguments.

        Returns:
            type: The newly constructed class with numpy fields ignored.
        """
        annotations: Dict[str, Any] = namespace.get("__annotations__", {})

        for base in bases:
            for base_ in base.__mro__:
                if base_ is BaseModel:
                    break
                annotations.update(base_.__annotations__)

        for field in annotations:
            if not field.startswith("__") and (
                str(annotations[field]).find("npt.") > 0 or str(annotations[field]).find("numpy.") > 0
            ):
                annotations[field] = None

        namespace["__annotations__"] = annotations
        return super().__new__(cls, cls_name, bases, namespace, **kwargs)


class DateBetween(BaseModel):
    """Schema for passing a date range between two dates.

    Attributes:
        from_date: Start date.
        to_date: End date.
    """
    from_date: datetime
    to_date: datetime

    @validator("from_date", "to_date", pre=True)
    def parse_date(cls, value: Union[str, datetime]) -> datetime:
        """Parse date from string or datetime object.

        Args:
            value: Date value as string or datetime.

        Returns:
            datetime: Parsed datetime object.
        """
        if isinstance(value, str):
            return datetime.strptime(value, "%Y-%m-%d %H:%M:%S")
        return value
