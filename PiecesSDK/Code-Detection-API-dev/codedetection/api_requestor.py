import requests

import codedetection
from codedetection.error import *


class APIRequestor:
    """
    APIRequestor is an abstract class that contains basics of every feature in API.
    """

    @classmethod
    def _make_request(cls, inputs: list) -> dict:
        response = requests.post(
            url=f"{codedetection.api_base}tlp?apikey={codedetection.api_key}",
            headers={"Content-Type": "text/plain"},
            data=json.dumps({
                "iterable": [
                    {"value": x} for x in inputs
                ]
            })
        )

        if 200 <= response.status_code < 300:
            return json.loads(response.content)
        else:
            return cls._handle_errors(message=response.text, status_code=response.status_code)

    @classmethod
    def _format_output(cls, output) -> str:
        return json.dumps(output, indent=4)

    @classmethod
    def _handle_errors(cls, message, status_code):
        if status_code == 429:
            raise RateLimitError(message=message, status_code=status_code)
        elif status_code in [400, 404, 415]:
            raise InvalidRequestError(message=message, status_code=status_code)
        elif status_code == 401:
            raise AuthenticationError(message=message, status_code=status_code)
        elif status_code == 403:
            raise PermissionError(message=message, status_code=status_code)
        else:
            raise CodeDetectionError(message=message, status_code=status_code)
