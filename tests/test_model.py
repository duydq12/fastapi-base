"""Unit tests for pluralize utility function in fastapi_base.model.

Covers regular and irregular pluralization cases.
"""
import pytest

from fastapi_base.model import pluralize


@pytest.mark.parametrize(
    "word, expected",
    [
        ("cat", "cats"),
        ("bus", "buses"),
        ("box", "boxes"),
        ("church", "churches"),
        ("dish", "dishes"),
        ("city", "cities"),
        ("man", "men"),
        ("woman", "women"),
        ("child", "children"),
        ("person", "people"),
        ("leaf", "leaves"),
        ("belief", "beliefs"),
    ],
)
def test_pluralize(word, expected):
    """Tests the pluralize function with various words.

    Asserts that the output matches the expected plural form.
    """
    assert pluralize(word) == expected
