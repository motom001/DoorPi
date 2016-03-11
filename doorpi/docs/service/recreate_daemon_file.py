#!/usr/bin/python
# -*- coding: utf-8 -*-

import doorpi.metadata as metadata
import os
import urllib2

print("start to create daemon file now...")


def parse_string(raw_string):
    for meta_key in dir(metadata):
        if not meta_key.startswith('__'):
            raw_string = raw_string.replace('!!%s!!' % meta_key,  str(getattr(metadata, meta_key)))
    return raw_string


def main():
    url = 'https://raw.githubusercontent.com/motom001/DoorPi/master/'+metadata.daemon_name_template
    daemon_filename = os.path.join(metadata.daemon_folder, metadata.daemon_name)
    print("start down download and parse new daemon file:")
    print("URL:  "+url)
    print("FILE: "+daemon_filename)
    with open(daemon_filename, "w") as daemon_file:
        for line in urllib2.urlopen(url):
            daemon_file.write(parse_string(line))
        print("download successfully - change chmod to 0755 now")
        os.chmod(daemon_filename, 0755)
        print "finished"

if __name__ == '__main__':
    main()
