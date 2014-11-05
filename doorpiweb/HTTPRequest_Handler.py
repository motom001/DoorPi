#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
logger = logging.getLogger(__name__)
logger.debug("%s loaded", __name__)

import os.path

import BaseHTTPServer
import doorpiweb
import metadata
import cgi

def do_status(socket, status_code):
    socket.send_response(status_code)
    socket.end_headers()
    www = doorpiweb.DoorPiWeb().get_config().get_string('DoorPiWeb', 'www', '/home/pi/DooPiWeb/www')
    requested_file = www + '/error/' + str(status_code) + '.html'
    for line in doorpiweb.DoorPiWeb().get_content(socket, requested_file):
        socket.wfile.write(line)
    return False

def is_searched_resource(resource):
    if not os.path.isfile(resource): return False
    if not os.access(resource, os.R_OK): return False
    if os.path.isdir(resource): return False
    return True

class DoorPiWeb_HTTPRequestHandler(BaseHTTPServer.BaseHTTPRequestHandler):
    #def log_message(self, format, *args):
    #    logger.debug("%s - %s", self.address_string(),format%args)

    def do_HEAD(s):
        s.send_response(200)
        s.send_header("Content-type", "text/html")
        s.end_headers()

    def do_POST(self):
        ctype, pdict = cgi.parse_header(self.headers.getheader('content-type'))

        if ctype == 'multipart/form-data':
            postvars = cgi.parse_multipart(self.rfile, pdict)
        elif ctype == 'application/x-www-form-urlencoded':
            length = int(self.headers.getheader('content-length'))
            postvars = cgi.parse_qs(self.rfile.read(length), keep_blank_values=1)
        else:
            postvars = {}

        logger.debug(postvars)
        self.do_GET()

    def do_GET(s):
        """Respond to a GET request."""

        www = doorpiweb.DoorPiWeb().get_config().get_string('DoorPiWeb', 'www', '/home/pi/DooPiWeb/www')
        index_file = doorpiweb.DoorPiWeb().get_config().get_string('DoorPiWeb', 'indexfile', 'index.html')

        # Sonderlocke favicon.ico
        if s.path.endswith("favicon.ico"):
            for line in doorpiweb.DoorPiWeb().get_content(s, www + s.path):
                s.wfile.write(line)
            return

        requested_file = ''

        if (is_searched_resource(www + s.path)):
            requested_file = www + s.path
        elif (is_searched_resource(www + s.path + '/')):
            requested_file = www + s.path + '/'
        elif (is_searched_resource(www + s.path + index_file)):
            requested_file = www + s.path + index_file
        elif (is_searched_resource(www + s.path + '/' + index_file)):
            requested_file = www + s.path + '/' + index_file
        else:
            logger.warning('requested file not exists or is not readable: %s', requested_file)
            do_status(s, 404)
            return

        logger.info("requested_file isfile and readable: %s",requested_file)

        s.send_response(200)
        s.send_header("Content-type", "text/html")
        s.end_headers()

        for line in doorpiweb.DoorPiWeb().get_content(s, requested_file):
            s.wfile.write(line)