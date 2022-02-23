# -*- coding: utf-8 -*-
import doorpi
from doorpi.action.base import SingleAction

import urllib.request
import urllib.error
import urllib.parse
import ssl

import logging
logger = logging.getLogger(__name__)
logger.debug('%s loaded', __name__)


def fire_command(url):
    try:
        if '@' in url:
            nurl = urllib.parse.urlsplit(url)
            username = nurl.username
            password = nurl.password
            url = url.replace(username + ':' + password + '@', '')
            url = url.replace(' ', '%20')

            ssl._create_default_https_context = ssl._create_unverified_context
            p = urllib.request.HTTPPasswordMgrWithDefaultRealm()
            p.add_password(None, url, username, password)
            handler = urllib.request.HTTPBasicAuthHandler(p)
            opener = urllib.request.build_opener(handler)
            urllib.request.install_opener(opener)
        else:
            url = url.replace(' ', '%20')

        logger.debug(('url: {0}').format(url))
        return urllib.request.urlopen(url=url, data=None, timeout=1)
    except urllib.request.HTTPError as exp:
        logger.error(('HTTPError: {0} - {1}').format(exp.code, exp.reason))
    except urllib.request.URLError as exp:
        logger.error(('URLError: {0}').format(exp.reason))
    return False


def get(parameters):
    parsed_parameters = doorpi.DoorPi().parse_string(parameters)
    return UrlCallAction(fire_command, url=parsed_parameters)


class UrlCallAction(SingleAction):
    pass
