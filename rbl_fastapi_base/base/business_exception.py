class BusinessException(Exception):
    def __init__(self, http_code: int = 400, code: str = "", message: str = ""):
        self.http_code = http_code
        self.code = code if code else str(self.http_code)
        self.message = message
