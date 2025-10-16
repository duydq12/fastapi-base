"""Defines the base SQLAlchemy model and utility functions for ORM usage.

Provides automatic table naming and dictionary conversion for model instances.

Classes:
    Base: Base SQLAlchemy model with automatic tablename and dict conversion.
"""

import re
from typing import Any

import inflect
from sqlalchemy import MetaData
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm.collections import InstrumentedList

NAMING_CONVENTION = {
    "ix": "ix_%(column_0_label)s",  # Index
    "uq": "uq_%(table_name)s_%(column_0_name)s",  # UniqueConstraint
    "ck": "ck_%(table_name)s_%(constraint_name)s",  # Check
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",  # ForeignKey
    "pk": "pk_%(table_name)s",  # PrimaryKey
}
p = inflect.engine()


class Base(AsyncAttrs, DeclarativeBase):
    """Base SQLAlchemy model for ORM usage.

    Provides automatic tablename generation and dict conversion.

    Attributes:
        id: Primary key field.
        is_deleted: Soft delete flag.
        metadata: SQLAlchemy metadata with naming conventions.
    """
    id: Any  # noqa
    is_deleted: Any

    metadata = MetaData(naming_convention=NAMING_CONVENTION)

    @declared_attr  # type: ignore
    def __tablename__(cls) -> str:
        """Automatically generates table name from class name in plural snake_case.

        Returns:
            str: Table name for the model.
        """
        words = re.findall("[A-Z][^A-Z]*", cls.__name__)
        if len(words) == 1:
            return p.plural(words[0].lower())
        elif len(words) > 1:
            return "_".join(words[:-1]).lower() + "_" + p.plural(words[-1].lower())
        return cls.__name__.lower()

    def to_dict(
        self, ignore_fields: tuple[str, ...] = ("is_deleted", "password", "updated_at", "_sa_instance_state")
    ) -> dict[str, Any]:
        """Recursively converts DB object instance to python dictionary.

        Args:
            ignore_fields (Tuple[str]): Fields to exclude from the result.

        Returns:
            dict[str, Any]: Dictionary representation of the model instance.
        """
        result = self.__dict__
        for field in ignore_fields:
            if field in result:
                del result[field]

        for k, v in result.items():
            if isinstance(v, (InstrumentedList, list)):
                # Recursion on joined relationship fields.
                result[k] = [obj.to_dict(ignore_fields) for obj in v]

        return result
