# -*- coding: utf-8 -*-
"""Project metadata

Information describing the project.
"""

# The package name, which is also the "UNIX name" for the project.
package = 'doorpi'
project = "VoIP Door-Intercomstation with Raspberry Pi (optional PiFace)"
project_no_spaces = project.replace(' ', '')
version = '1.0.3'
description = 'provide intercomstation to the doorstation by VoIP'
authors = ['Thomas Meissner']
authors_string = ', '.join(authors)
emails = ['thomas@meissner.me']
license = 'open'
copyright = '2014 ' + authors_string
url = 'http://meissner.me/'
author_strings = []
for name, email in zip(authors, emails):
    author_strings.append('Author: {0} <{1}>'.format(name, email))
epilog = '''
{project} {version}

{authors}
URL: <{url}>
'''.format(
        project=project,
        version=version,
        authors='\n'.join(author_strings),
        url=url)