#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
logger = logging.getLogger(__name__)
logger.debug("%s loaded", __name__)

import os.path
import urlparse

import BaseHTTPServer
import cgi

import doorpi
from action.base import SingleAction

def run_webservice(ip = '', port = 8080):
    logger.debug('starting webservice')
    server_address = (ip, port)
    httpd = BaseHTTPServer.HTTPServer(server_address, WebService)

    doorpi.DoorPi().event_handler.register_action('OnTimeMinute', SingleAction(httpd.shutdown))
    doorpi.DoorPi().event_handler.register_action('OnShutdown', SingleAction(httpd.shutdown))

    while doorpi.DoorPi().shutdown is False:
        logger.debug('waiting for next request')
        httpd.handle_request()
    return

class WebService(BaseHTTPServer.BaseHTTPRequestHandler):

    ip = ''
    port = 8080

    @staticmethod
    def run_webserver():
        logger.debug('starting webservice')
        server_address = (WebService.ip, WebService.port)
        print "server_address: %s %s" % (server_address)
        httpd = BaseHTTPServer.HTTPServer(server_address, WebService)
        httpd.serve_forever()
        return True

    def do_HEAD(self):
        logger.info('do_HEAD')
        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.end_headers()

    def do_GET(self):
        #self.send_header("Content-type", "application/json")
        #self.send_response(200)
        #self.end_headers()
        self.wfile.write(doorpi.DoorPi().status.json_beautified)
        return
    def do_GET_status(self):
        logger.info('do_GET')
        parsed_path = urlparse.urlparse(self.path)
        message_parts = [
                'CLIENT VALUES:',
                'client_address=%s (%s)' % (self.client_address,
                                            self.address_string()),
                'command=%s' % self.command,
                'path=%s' % self.path,
                'real path=%s' % parsed_path.path,
                'query=%s' % parsed_path.query,
                'request_version=%s' % self.request_version,
                '',
                'SERVER VALUES:',
                'server_version=%s' % self.server_version,
                'sys_version=%s' % self.sys_version,
                'protocol_version=%s' % self.protocol_version,
                '',
                'HEADERS RECEIVED:',
        ]
        for name, value in sorted(self.headers.items()):
            message_parts.append('%s=%s' % (name, value.rstrip()))
        message_parts.append('')
        message = '\r\n'.join(message_parts)
        self.send_response(200)
        self.end_headers()
        self.wfile.write(message)
        return
