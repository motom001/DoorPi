# -*- coding: utf-8 -*-
# thx to pula @ DoorPi forum
# https://www.doorpi.org/forum/thread/25-http-request/?postID=596#post596

import logging
logger = logging.getLogger(__name__)
logger.debug("%s loaded", __name__)

from doorpi.action.base import SingleAction
import doorpi

import urllib.request, urllib.error, urllib.parse
import ssl
import urllib.parse


def fire_command(url):
    try:
        if "@" in url:
            nurl = urllib.parse.urlsplit(url)
            username = nurl.username
            password = nurl.password
            url = url.replace(username + ':' + password + '@', '')
            url = url.replace(" ", "%20")
            logger.debug('url: %s' % url)
            ssl._create_default_https_context = ssl._create_unverified_context
            p = urllib.request.HTTPPasswordMgrWithDefaultRealm()
            p.add_password(None, url, username, password)
            handler = urllib.request.HTTPBasicAuthHandler(p)
            opener = urllib.request.build_opener(handler)
            urllib.request.install_opener(opener)
            url = url.replace(" ", "%20")
            logger.info('url: %s' % url)
            return urllib.request.urlopen(
                url=url,
                data=None,
                timeout=1
            )
    except urllib.error.HTTPError as exp:
        logger.error('HTTPError: %s - %s' % (exp.code, exp.reason))
    except urllib.error.URLError as exp:
        logger.error('URLError: %s' % exp.reason)
    return False


def get(parameters):
    parsed_parameters = doorpi.DoorPi().parse_string(parameters)
    return UrlCallAction(fire_command, url=parsed_parameters)


class UrlCallAction(SingleAction):
    pass
