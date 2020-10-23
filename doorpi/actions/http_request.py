"""Actions that perform requests to third party servers: http_request"""
import logging
import urllib.parse
from typing import Any, Mapping

import requests

from . import Action, action

LOGGER = logging.getLogger(__name__)

ALLOWED_SCHEMES = {"http", "https"}

@action("http_request")
class HTTPRequestAction(Action):
    """Performs a GET request to the given URL."""
    def __init__(self, *args: str) -> None:
        super().__init__()
        self.__url = ",".join(args)
        url = urllib.parse.urlparse(self.__url)
        if not url.scheme or not url.netloc:
            raise ValueError(f"Invalid URL: {url!r}")

        if url.scheme not in ALLOWED_SCHEMES:
            raise ValueError(f"Invalid scheme: {url.scheme}")

    def __call__(self, event_id: str, extra: Mapping[str, Any]) -> None:
        resp = requests.get(self.__url)
        LOGGER.info(
            "[%s] Server response: %d %s",
            event_id, resp.status_code, resp.reason)

    def __str__(self) -> str:
        return f"HTTP Request to {self.__url}"

    def __repr__(self) -> str:
        return f"http_request:{self.__url}"
