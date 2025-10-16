from datetime import datetime

import numpy as np
import numpy.typing as npt
from pydantic import BaseModel, ConfigDict, Field

from fastapi_base.schema import BaseRequestSchema, DateBetween, Paging, all_optional, ignore_numpy_fields


class AliasSchema(BaseRequestSchema):
    """Schema with field aliases for testing alias collection."""
    foo: int = Field(..., alias="bar")
    baz: str


def test_collect_aliases():
    """Test that collect_aliases returns correct mapping of aliases to field names."""
    aliases = AliasSchema.collect_aliases()
    assert aliases["bar"] == "foo"
    assert aliases["baz"] == "baz"


class OptionalSchema(BaseModel):
    """Schema for testing all_optional utility."""
    a: int
    b: str


def test_all_optional():
    """Test that all_optional returns a schema with all fields optional (default None)."""
    opt = all_optional("Opt", OptionalSchema)
    assert opt.model_fields["a"].default is None
    assert opt.model_fields["b"].default is None
    inst = opt()
    assert hasattr(inst, "a")
    assert hasattr(inst, "b")


class DummyNumpySchema(BaseModel):
    """Schema with a numpy array field for testing ignore_numpy_fields utility."""
    a: int
    arr: npt.NDArray[np.float64]
    b: str

    model_config = ConfigDict(arbitrary_types_allowed=True)


def test_ignore_numpy_fields():
    """Test that ignore_numpy_fields removes numpy array fields from the schema."""
    no_numpy = ignore_numpy_fields("NoNumpy", DummyNumpySchema)
    fields = no_numpy.model_fields
    assert "a" in fields
    assert "b" in fields
    assert "arr" not in fields


def test_paging_model():
    """Test that the Paging model has offset and limit attributes."""
    p = Paging()
    assert hasattr(p, "offset")
    assert hasattr(p, "limit")


def test_date_between_model():
    """Test that the DateBetween model correctly initializes from_date and to_date."""
    d = DateBetween(from_date=datetime(2023, 1, 1), to_date=datetime(2023, 1, 31))
    assert d.from_date == datetime(2023, 1, 1)
    assert d.to_date == datetime(2023, 1, 31)
