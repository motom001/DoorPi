# -*- coding: utf-8 -*-
"""Project metadata

Information describing the project.
"""
import os

# The package name, which is also the "UNIX name" for the project.
package = 'DoorPi'
project = "VoIP Door-Intercomstation with Raspberry Pi"
project_no_spaces = project.replace(' ', '')
version = '2.4.0.8'
description = 'provide intercomstation to the doorstation by VoIP'
keywords = ['intercom', 'VoIP', 'doorstation', 'home automation', 'IoT']
authors = ['Thomas Meissner']
authors_emails = emails = ['motom001@gmail.com']
authors_string = ', '.join(authors)
author_strings = []
for name, email in zip(authors, authors_emails):
    author_strings.append('{0} <{1}>'.format(name, email))

supporters = [
    'Phillip Munz <office@businessaccess.info>',
    'Hermann Dötsch <doorpi1@gmail.com>',
    'Dennis Häußler <haeusslerd@outlook.com>',
    'Hubert Nusser <hubsif@gmx.de>',
    'Michael Hauer <frrr@gmx.at>',
    'Andreas Schwarz <doorpi@schwarz-ketsch.de>',
    'Max Rößler <max_kr@gmx.de>',
    'missing someone? -> sorry -> mail me'
]
supporter_string = '\n'.join(supporters)
copyright = "%s, 2014-2015"%authors[0]
license = 'CC BY-NC 4.0'
url = 'https://github.com/motom001/DoorPi'

# created with: http://patorjk.com/software/taag/#p=display&f=Ogre&t=DoorPi
epilog = '''
    ___                  ___ _
   /   \___   ___  _ __ / _ (_)  {project}
  / /\ / _ \ / _ \| '__/ /_)/ |  version:   {version}
 / /_// (_) | (_) | | / ___/| |  license:   {license}
/___,' \___/ \___/|_| \/    |_|  URL:       <{url}>

Authors:    {authors}
Supporter:  {supporters}
'''.format(
        license = license,
        project = project,
        version = version,
        authors = '\n'.join(author_strings),
        supporters = '\n            '.join(supporters),
        url = url)

import tempfile
base_path = tempfile.gettempdir()
if os.access(base_path, os.W_OK):
    print("USE BASE_PATH1: %s"%base_path)
else:
    base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    print("USE BASE_PATH2: %s"%base_path)
