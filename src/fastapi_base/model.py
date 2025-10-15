"""Defines the base SQLAlchemy model and utility functions for ORM usage.

Provides automatic table naming and dictionary conversion for model instances.

Classes:
    Base: Base SQLAlchemy model with automatic tablename and dict conversion.
Functions:
    pluralize: Pluralizes English words for table naming.
"""

import re

from typing import Any, Tuple

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


def pluralize(word: str) -> str:
    """Pluralizes an English word, handling regular and irregular cases.

    Args:
        word (str): Singular word to pluralize.

    Returns:
        str: Plural form of the word.
    """
    exceptions = {
        "man": "men",
        "woman": "women",
        "child": "children",
        "tooth": "teeth",
        "foot": "feet",
        "person": "people",
        "mouse": "mice",
        "goose": "geese",
        "ox": "oxen",
        "leaf": "leaves",
        "knife": "knives",
        "life": "lives",
        "elf": "elves",
        "calf": "calves",
        "half": "halves",
        "shelf": "shelves",
        "thief": "thieves",
        "wife": "wives",
        "wolf": "wolves",
        "belief": "beliefs",
    }

    if word in exceptions:
        return exceptions[word]

    if word.endswith("s") or word.endswith("x") or word.endswith("ch") or word.endswith("sh"):
        word = word + "es"
    elif word.endswith("y") and word[-2] not in "aeiou":
        word = word[:-1] + "ies"
    else:
        word = word + "s"

    return word


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

    @declared_attr
    def __tablename__(cls) -> str:
        """Automatically generates table name from class name in plural snake_case.

        Returns:
            str: Table name for the model.
        """
        table_name = cls.__name__
        table_name = pluralize(table_name)
        word_list = re.findall("[A-Z][^A-Z]*", table_name)
        return "_".join(word_list).lower()

    def to_dict(
        self, ignore_fields: Tuple[str] = ("is_deleted", "password", "updated_at", "_sa_instance_state")
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
            if isinstance(v, InstrumentedList):
                # Recursion on joined relationship fields.
                result[k] = [obj.to_dict(ignore_fields) for obj in v]

        return result
