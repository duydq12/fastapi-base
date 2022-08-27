from fastapi import FastAPI
from fastapi.openapi.docs import (
    get_redoc_html,
    get_swagger_ui_html
)
from fastapi_health import health
from starlette.staticfiles import StaticFiles

from .config.log_config import CustomizeLogger
from .middleware.exception_handler import error_handle_business, process_middleware_common

app = FastAPI(docs_url=None, redoc_url=None)

app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html():
    return get_swagger_ui_html(
        openapi_url=app.openapi_url,
        title=app.title + " - Rabiloo Swagger UI",
        oauth2_redirect_url=app.swagger_ui_oauth2_redirect_url,
        swagger_js_url="/static/swagger-ui-bundle.js",
        swagger_css_url="/static/swagger-ui.css",
    )


@app.get("/redoc", include_in_schema=False)
async def redoc_html():
    return get_redoc_html(
        openapi_url=app.openapi_url,
        title=app.title + " - Rabiloo ReDoc",
        redoc_js_url="/static/redoc.standalone.js",
    )


def healthy_condition():
    return {"service": "online"}


def sick_condition():
    return True


app.add_api_route("/actuator/health", health([healthy_condition, sick_condition]))

logger = CustomizeLogger.make_logger()

app.logger = logger
app.add_exception_handler(Exception, error_handle_business)
app.middleware("http")(process_middleware_common)
