import pytest
from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from fastwings.model import Base as GlobalBase


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
    namespace = {"id": mapped_column(Integer, primary_key=True)}
    TestModel = type(model_class_name, (GlobalBase,), namespace)
    assert TestModel.__tablename__ == expected_table_name


class Customer(GlobalBase):
    """Test model representing a customer for table name and field mapping tests."""
    __tablename__ = "customers"  # Define explicitly to avoid dynamic name issues
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50))
    email: Mapped[str] = mapped_column(String(50))
    password: Mapped[str] = mapped_column(String(100))


class Product(GlobalBase):
    """Test model representing a product for table name and field mapping tests."""
    __tablename__ = "products"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50))
    sku: Mapped[str] = mapped_column(String(20))
    price: Mapped[float]


class Address(GlobalBase):
    __tablename__ = "addresses"
    id: Mapped[int] = mapped_column(primary_key=True)
    street: Mapped[str]
    city: Mapped[str]


class User(GlobalBase):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    addresses = Mapped[list[Address]]


@pytest.mark.parametrize(
    "model, ignore_fields, expected",
    [
        (
            Customer(id=1, name="John Doe", email="john.doe@example.com", password="a_secret_password"),  # noqa S106
            ("is_deleted", "password", "updated_at", "_sa_instance_state"),  # default ignore fields
            {"id": 1, "name": "John Doe", "email": "john.doe@example.com"}
        ),
        (
            Product(id=101, name="Laptop", sku="LPTP-101", price=1200.00),
            ("sku", "price", "_sa_instance_state"),
            {"id": 101, "name": "Laptop"}
        ),
        (
            User(id=1, name="Jane Doe", addresses=[Address(id=201, street="123 Main St", city="Anytown"),
                                                   Address(id=202, street="456 Oak Ave", city="Anytown")]),
            ("is_deleted", "password", "updated_at", "_sa_instance_state"),  # default ignore fields
            {"id": 1, "name": "Jane Doe", "addresses": [{"id": 201, "street": "123 Main St", "city": "Anytown"},
                                                        {"id": 202, "street": "456 Oak Ave", "city": "Anytown"}]}
        )
    ]
)
def test_to_dict_simple_conversion(model, ignore_fields, expected):
    """Tests the basic conversion of a model instance to a dictionary."""
    res_dict = model.to_dict() if not ignore_fields else model.to_dict(ignore_fields)

    assert res_dict == expected
    for field in ignore_fields:
        assert field not in res_dict
