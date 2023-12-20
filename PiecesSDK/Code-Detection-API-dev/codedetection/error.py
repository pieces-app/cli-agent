import json


class CodeDetectionError(BaseException):
    """
    CodeDetectionError is an abstract class that contains basics of every error in API.
    """

    def __init__(self, message=None, status_code=None):
        super(CodeDetectionError, self).__init__(message)

        self.message = message
        self.status_code = status_code

    def __str__(self):
        return json.dumps({
            "status code": self.status_code,
            "message": self.message
        }, indent=4)


class InvalidRequestError(CodeDetectionError):
    pass


class AuthenticationError(CodeDetectionError):
    pass


class PermissionError(CodeDetectionError):
    pass


class RateLimitError(CodeDetectionError):
    pass
