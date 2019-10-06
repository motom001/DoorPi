import logging
import requests
import requests.utils
from requests.exceptions import RequestException

import doorpi
from . import Action


logger = logging.getLogger(__name__)

ALLOWED_SCHEMES = ["http", "https"]


class HTTPRequestAction(Action):
    def __init__(self, *args):
        self.__url = ",".join(args)
        url = requests.utils.urlparse(self.__url)
        if not url.scheme or not url.netloc:
            raise ValueError(f"Invalid URL: {url!r}")

        if url.scheme not in ALLOWED_SCHEMES:
            raise ValueError(f"Invalid scheme: {url.scheme}")

    def __call__(self, event_id, extra):
        r = requests.get(self.__url)

        logger.info("[%s] Server response: %d %s", event_id, r.status_code, r.reason)

    def __str__(self):
        return f"HTTP Request to {self.__url}"

    def __repr__(self):
        return f"{__name__.split('.')[-1]}:{self.__url}"


instantiate = HTTPRequestAction
