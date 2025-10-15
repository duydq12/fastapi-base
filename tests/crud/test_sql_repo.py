"""Unit tests for SQLRepository (synchronous CRUD) in fastapi_base.

Covers create, read, update, and soft delete operations using a mock SQLAlchemy model and session.
"""
import uuid

from pydantic import BaseModel
from sqlalchemy import UUID as UUID_SQL
from sqlalchemy import Boolean, String
from sqlalchemy.orm import Mapped, mapped_column

from fastapi_base.crud.sql_repo import SQLRepository
from fastapi_base.model import Base


class MockModel(Base):
    """Mock SQLAlchemy model for testing SQLRepository.

    Table: mock_items
    Fields:
        - id: UUID primary key
        - name: string
        - is_deleted: boolean (soft delete flag)
    """
    __tablename__ = "mock_items"
    id: Mapped[uuid.UUID] = mapped_column(UUID_SQL, primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False, server_default="false")

class MockCreateSchema(BaseModel):
    """Pydantic schema for creating a MockModel object."""
    name: str

class MockUpdateSchema(BaseModel):
    """Pydantic schema for updating a MockModel object."""
    name: str

# --- Tests ---
def test_get_object(mock_db_session):
    """Tests retrieving an object by ID using SQLRepository.get().

    Asserts that the returned object matches the mock and is not None.
    """
    mock_item = MockModel(name="test_item", id=uuid.uuid4())
    mock_db_session.query.return_value.filter.return_value.first.return_value = mock_item

    repo = SQLRepository(MockModel)
    obj_id = uuid.uuid4()
    result = repo.get(mock_db_session, obj_id)

    mock_db_session.query.assert_called_with(MockModel)
    assert result is not None
    assert result.name == "test_item"

def test_create_object(mock_db_session):
    """Tests creating an object using SQLRepository.create().

    Asserts that the created object has the expected name and session methods are called.
    """
    repo = SQLRepository(MockModel)
    create_schema = MockCreateSchema(name="new_item")

    db_obj = repo.create(mock_db_session, obj_in=create_schema)

    mock_db_session.add.assert_called_once()
    mock_db_session.commit.assert_called_once()
    mock_db_session.refresh.assert_called_once()
    assert db_obj.name == "new_item"

def test_update_object(mock_db_session):
    """Tests updating an object using SQLRepository.update().

    Asserts that the update method is called with correct data and session is committed.
    """
    repo = SQLRepository(MockModel)
    update_schema = MockUpdateSchema(name="updated_item")
    obj_id = uuid.uuid4()

    repo.update(mock_db_session, obj_id=obj_id, obj_in=update_schema)

    mock_db_session.query.return_value.filter.return_value.update.assert_called_with({"name": "updated_item"})
    mock_db_session.commit.assert_called_once()

def test_delete_object(mock_db_session):
    """Tests 'soft' deleting an object using SQLRepository.delete().

    Asserts that the is_deleted flag is set and session is committed.
    """
    repo = SQLRepository(MockModel)
    obj_id = uuid.uuid4()

    repo.delete(mock_db_session, obj_id=obj_id)

    mock_db_session.query.return_value.filter.return_value.update.assert_called_with({"is_deleted": True})
    mock_db_session.commit.assert_called_once()
