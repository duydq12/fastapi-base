import pytest
from sqlalchemy import String
from sqlmodel import Field, Relationship

from fastwings.model import BaseModel as GlobalBase


@pytest.mark.parametrize(
    "model_class_name, expected_table_name",
    [
        ("Admin", "admins"),
        ("UserProfile", "user_profiles"),
        ("ProductCategory", "product_categories"),
        ("OAuthCredential", "o_auth_credentials"),
        ("Box", "boxes"),
        ("City", "cities"),
    ],
)
def test_tablename_generation(model_class_name, expected_table_name):
    """Test that __tablename__ is generated correctly from class name (plural, snake_case)."""
    annotations = {"id": int}
    namespace = {
        "__annotations__": annotations,
        "id": Field(primary_key=True)
    }
    TestModel = type(model_class_name, (GlobalBase,), namespace)
    assert TestModel.__tablename__ == expected_table_name


class Customer(GlobalBase, table=True):
    """Test model representing a customer for table name and field mapping tests."""
    id: int = Field(primary_key=True)
    name: str = Field(String(50))
    email: str = Field(String(50))
    password: str = Field(String(100))


class Product(GlobalBase, table=True):
    """Test model representing a product for table name and field mapping tests."""
    id: int = Field(primary_key=True)
    name: str = Field(String(50))
    sku: str = Field(String(20))
    price: float


class User(GlobalBase, table=True):
    id: int = Field(primary_key=True)
    name: str
    addresses: list["Address"] = Relationship(back_populates="user")


class Address(GlobalBase, table=True):
    id: int = Field(primary_key=True)
    street: str
    city: str

    user_id: int = Field(foreign_key="users.id")
    user: "User" = Relationship(back_populates="addresses")


@pytest.mark.parametrize(
    "model, ignore_fields, expected",
    [
        (
            Customer(id=1, name="John Doe", email="john.doe@example.com", password="a_secret_password"),  # noqa S106
            ("is_deleted", "password", "created_at", 'created_by', "updated_at", "updated_by", "_sa_instance_state"),
            # default ignore fields
            {"id": 1, "name": "John Doe", "email": "john.doe@example.com"}
        ),
        (
            Product(id=101, name="Laptop", sku="LPTP-101", price=1200.00),
            (
                "sku", "price", "is_deleted", "created_at", 'created_by', "updated_at", "updated_by",
                "_sa_instance_state"),
            {"id": 101, "name": "Laptop"}
        ),
        (
            User(id=1, name="Jane Doe", addresses=[Address(id=201, street="123 Main St", city="Anytown"),
                                                   Address(id=202, street="456 Oak Ave", city="Anytown")]),
            ("is_deleted", "password", "created_at", 'created_by', "updated_at", "updated_by", "_sa_instance_state"),
            # default ignore fields
            {"id": 1, "name": "Jane Doe", "addresses": [
                {"id": 201, "street": "123 Main St", "city": "Anytown", "user": {}},
                {"id": 202, "street": "456 Oak Ave", "city": "Anytown", "user": {}}]}
        )
    ]
)
def test_to_dict_simple_conversion(model, ignore_fields, expected):
    """Tests the basic conversion of a model instance to a dictionary."""
    res_dict = model.to_dict() if not ignore_fields else model.to_dict(ignore_fields)

    assert res_dict == expected
    for field in ignore_fields:
        assert field not in res_dict
