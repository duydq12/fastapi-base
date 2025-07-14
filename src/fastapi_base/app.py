from fastapi import FastAPI
from fastapi_health import health

app = FastAPI()


def healthy_condition():
    return {"service": "online"}


def sick_condition():
    return True


app.add_api_route("/health", health([healthy_condition, sick_condition]))
