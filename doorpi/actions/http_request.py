"""Actions that perform requests to third party servers: http_request"""

import logging
import requests
import requests.utils

from . import action

LOGGER = logging.getLogger(__name__)

ALLOWED_SCHEMES = {"http", "https"}


@action("http_request")
class HTTPRequestAction:
    """Performs a GET request to the given URL."""

    def __init__(self, *args):
        self.__url = ",".join(args)
        url = requests.utils.urlparse(self.__url)
        if not url.scheme or not url.netloc:
            raise ValueError(f"Invalid URL: {url!r}")

        if url.scheme not in ALLOWED_SCHEMES:
            raise ValueError(f"Invalid scheme: {url.scheme}")

    def __call__(self, event_id, extra):
        resp = requests.get(self.__url)

        LOGGER.info("[%s] Server response: %d %s", event_id, resp.status_code, resp.reason)

    def __str__(self):
        return f"HTTP Request to {self.__url}"

    def __repr__(self):
        return f"http_request:{self.__url}"
