import logging
from typing import Callable

from fastapi import Request, Response
from fastapi.routing import APIRoute


class BaseRoute(APIRoute):
    def get_route_handler(self) -> Callable:
        original_route_handler = super().get_route_handler()

        async def custom_route_handler(request: Request) -> Response:
            request_data = {"headers": {}}
            try:
                try:
                    body_str = await request.json()
                    request_data["request_body"] = body_str
                except Exception:
                    pass
                if request.query_params or request.path_params:
                    request_data = {
                        "query_params": str(request.query_params),
                        "path_params": request.path_params
                    }
                if 'authorization' in request.headers.keys():
                    request_data.get('headers')['authorization'] = request.headers.get('authorization')
                if 'content-type' in request.headers.keys():
                    request_data.get('headers')['content-type'] = request.headers.get('content-type')
            except Exception:
                pass
            if request_data:
                logging.info(request_data)
            response: Response = await original_route_handler(request)
            if hasattr(response, 'body'):
                try:
                    response_data = {"response_data": response.body.decode("utf-8")}
                    logging.info(response_data)
                except Exception:
                    pass
            return response

        return custom_route_handler
