# FastAPI Base

[![Testing](https://github.com/duydq12/fastapi-base/actions/workflows/test.yml/badge.svg)](https://github.com/duydq12/fastapi-base/actions/workflows/test.yml)
[![Code coverage](https://codecov.io/gh/duydq12/fastapi-base/branch/main/graph/badge.svg)](https://app.codecov.io/github/duydq12/fastapi-base)
[![Latest Version](https://img.shields.io/pypi/v/fastwings.svg)](https://pypi.org/project/fastwings)
[![Downloads](https://img.shields.io/pypi/dm/fastwings.svg)](https://pypi.org/project/fastwings)
[![Pypi Status](https://img.shields.io/pypi/status/fastwings.svg)](https://pypi.org/project/fastwings)
[![Python Versions](https://img.shields.io/pypi/pyversions/fastwings.svg)](https://pypi.org/project/fastwings)

## About FastAPI Base

[FastAPI Base](https://github.com/duydq12/fastapi-base) is a library based on [FastAPI](https://github.com/tiangolo/fastapi). It provides several modules that help improve web application development using FastAPI

Some module in project
- Logger module
- Authentication module
- Database Connection module
- CRUD module
- Encrypt module
- Common Design Pattern module

## Install
With using the logger with 3rdParty handlers
```
$ pip install fastwings[logger-logstash,logger-ggchat]
```

# Usage
## Config middleware, exception_handler, logger with uvicorn
```
from fastwings.app import app
from fastwings.logger import configure_logger, get_uvicorn_configure_logger
from fastwings.logger.filter import HealthCheckFilter
from fastwings.logger.formatter import DEFAULT_FORMATTER
from fastwings.logger.handler.logstash_handler import LogStashHandler
from fastwings.logger.handler.file_handler import FileHandler
from fastwings.logger.handler.stdout_handler import StdoutHandler
from fastwings.middleware.common_handler import timer_middleware
from fastwings.middleware.exception_handler import business_exception_handler
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.middleware.cors import CORSMiddleware


# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# Add Timer middleware
app.add_middleware(BaseHTTPMiddleware, dispatch=timer_middleware)

# Add Business Exception Handler
app.add_exception_handler(BusinessException, business_exception_handler)

configure_logger(
    handlers=[
        ("builtin", StdoutHandler(log_format=DEFAULT_FORMATTER)),
        ("builtin", FileHandler(log_format=DEFAULT_FORMATTER, log_filter=HealthCheckFilter())),
        ("custom", LogStashHandler(service_name="Test", log_filter=HealthCheckFilter()))
    ]
)


logger = logging.getLogger(__name__)


@app.post('/test')
async def test(
    title: str = Form(...),
    description: str = Form(...),
) -> ResponseObject:
    """ doc """
    logger.info(f"{title}-{description}")
    return ResponseObject(data=f"{title}-{description}")


uvicorn.run(
    app,
    host="0.0.0.0",
    port=3000,
    workers=1,
    reload=False,
    log_config=get_uvicorn_configure_logger()
)
```

## Changelog

Please see [CHANGELOG](CHANGELOG.md) for more information on what has changed recently.

## Contributing

Please see [CONTRIBUTING](.github/CONTRIBUTING.md) for details.

## Security Vulnerabilities

Please review [our security policy](../../security/policy) on how to report security vulnerabilities.

## Credits

- [Dao Quang Duy](https://github.com/duydq12)
- [All Contributors](../../contributors)

## License

The MIT License (MIT). Please see [License File](LICENSE) for more information.
