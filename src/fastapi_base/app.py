"""Main FastAPI application setup.

Defines the FastAPI app instance and health check endpoints.

Functions:
    healthy_condition: Returns service status for health check.
    sick_condition: Returns True for health check (placeholder).
"""

from fastapi import FastAPI
from fastapi_health import health

app = FastAPI()


def healthy_condition() -> dict[str, str]:
    """Returns service status for health check endpoint.

    Returns:
        dict: Service status information.
    """
    return {"service": "online"}


def sick_condition() -> bool:
    """Returns True for health check endpoint (placeholder for additional checks).

    Returns:
        bool: Always True.
    """
    return True


app.add_api_route("/health", health([healthy_condition, sick_condition]))
