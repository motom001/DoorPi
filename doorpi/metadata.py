"""Project metadata
# pylint: disable=invalid-name

Information describing the project.
"""

# The package name, which is also the "UNIX name" for the project.
package = "DoorPi"
project = "VoIP Door-Intercomstation with Raspberry Pi"
version = "3.0beta3"
description = "Provide intercom station to the door station via VoIP"
authors = ["Wüstengecko", "Thomas Meissner"]
emails = ["1579756+Wuestengecko@users.noreply.github.com", "motom001@gmail.com"]

supporters = (
    "Phillip Munz <office@businessaccess.info>",
    "Hermann Dötsch <doorpi1@gmail.com>",
    "Dennis Häußler <haeusslerd@outlook.com>",
    "Hubert Nusser <hubsif@gmx.de>",
    "Michael Hauer <frrr@gmx.at>",
    "Andreas Schwarz <doorpi@schwarz-ketsch.de>",
    "Max Rößler <max_kr@gmx.de>",
    "missing someone? -> sorry -> mail me"
)
copyright = "%s, 2014-2015" % authors[0]
license = "CC BY-NC 4.0"
url = "https://github.com/motom001/DoorPi"

# created with: http://patorjk.com/software/taag/#p=display&f=Ogre&t=DoorPi
epilog = r"""
    ___                  ___ _
   /   \___   ___  _ __ / _ (_)  {project}
  / /\ / _ \ / _ \| '__/ /_)/ |  version:   {version}
 / /_// (_) | (_) | | / ___/| |  license:   {license}
/___,' \___/ \___/|_| \/    |_|  URL:       <{url}>

Authors:    {authors}
Supporter:  {supporters}
""".format(
    license=license,
    project=project,
    version=version,
    authors="\n            ".join(f"{name} <{email}>" for name, email in zip(authors, emails)),
    supporters="\n            ".join(supporters),
    url=url)

pidfile = "/run/{0}/{0}.pid".format(package.lower())
