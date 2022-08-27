import datetime

from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse


class ResponseObject:
    def __init__(self):
        super().__init__()
        self.timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.data = None
        self.message = ""
        self.code = ""
        self.links = None
        self.relationships = None

    def success(self, data=None, message="success", code="0", links=None, relationships=None):
        self.data = data
        self.message = message
        self.code = code
        self.links = links
        self.relationships = relationships
        return self

    def error(self, status_code=400, data=None, message="error", code="1", links=None, relationships=None):
        self.message = message
        self.code = code
        self.data = data
        self.links = links
        self.relationships = relationships
        return JSONResponse(status_code=status_code, content=jsonable_encoder(self))
