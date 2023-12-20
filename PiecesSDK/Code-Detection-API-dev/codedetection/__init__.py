import os

from codedetection.api_resources import (
    Classifier,
    CodeVsText,
    Tokenizer,
    TLP
)
from codedetection.error import (
    RateLimitError,
    InvalidRequestError,
    AuthenticationError,
    PermissionError,
    CodeDetectionError
)

api_base = "https://api.runtime.dev/"
api_key = os.environ.get("CODEDETECTION_API_KEY")
organization = os.environ.get("CODEDETECTION_ORGANIZATION")

__all__ = [
    "Classifier",
    "CodeVsText",
    "Tokenizer",
    "TLP",
    "RateLimitError",
    "InvalidRequestError",
    "AuthenticationError",
    "PermissionError",
    "CodeDetectionError",
    "api_base",
    "api_key",
    "organization"
]
