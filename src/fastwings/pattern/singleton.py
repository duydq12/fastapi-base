"""Module singleton.py.

Provides a Singleton metaclass to ensure only one instance exists for each class using it.

Classes:
    Singleton: Metaclass that enforces the singleton pattern for classes.
"""

from typing import Any


class Singleton(type):
    """Singleton metaclass: Ensures only one instance per class using this metaclass."""
    _instances: dict[Any, Any] = {}

    def __call__(cls, *args: Any, **kwargs: Any) -> Any:
        """Returns the single instance of the class, creating it if necessary.

        Args:
            *args: Positional arguments for class instantiation.
            **kwargs: Keyword arguments for class instantiation.

        Returns:
            object: The singleton instance of the class.
        """
        if cls not in cls._instances:
            cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]
