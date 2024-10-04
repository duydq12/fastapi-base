from fastapi import FastAPI
from fastapi_health import health

print(
    r"""
 _____            ____ _____ _      ____   ____
|  __ \     /\   |  _ \_   _| |    / __ \ / __ \
| |__) |   /  \  | |_) || | | |   | |  | | |  | |
|  _  /   / /\ \ |  _ < | | | |   | |  | | |  | |
| | \ \  / ____ \| |_) || |_| |___| |__| | |__| |
|_|  \_\/_/    \_\____/_____|______\____/ \____/
"""
)

app = FastAPI()


def healthy_condition():
    return {"service": "online"}


def sick_condition():
    return True


app.add_api_route("/health", health([healthy_condition, sick_condition]))
