"""Unit tests for Singleton design pattern in fastapi_base.pattern.

Verifies that only one instance is created and shared.
"""
from fastapi_base.pattern import Singleton


def test_singleton_pattern():
    """Tests that the Singleton metaclass works correctly.

    Asserts that multiple instances are the same and share state.
    """
    class MyService(metaclass=Singleton):
        def __init__(self):
            self.value = 1

    instance1 = MyService()
    instance2 = MyService()
    assert instance1 is instance2
    instance1.value = 100
    assert instance2.value == 100
