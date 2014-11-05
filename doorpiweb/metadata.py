# -*- coding: utf-8 -*-
"""Project metadata

Information describing the project.
"""

# The package name, which is also the "UNIX name" for the project.
package = 'doorpiweb'
project = "Webinterface to install, configure and control doorpi"
project_no_spaces = project.replace(' ', '')
version = '1.0.0'
description = project
authors = ['Thomas Meissner']
authors_string = ', '.join(authors)
emails = ['thomas@meissner.me']
license = 'open'
copyright = '2014 ' + authors_string
url = 'http://meissner.me/'
project_url = 'https://github.com/motom001/DoorPiWeb'

author_list = []
for name, email in zip(authors, emails):
    author_list.append('Author: {0} <{1}>'.format(name, email))
epilog = '''
{project} {version}

{authors}
URL: <{url}>
'''.format(
        project=project,
        version=version,
        authors='\n'.join(authors_string),
        url=url)

html_epilog = '''
<a href="{project_url}">{package} ({project}) {version}</a>
<p>© 2014 by {authors}</p>
'''.format(
        project_url = project_url,
        package = package,
        project = project,
        version = version,
        authors = ', '.join(author_list))