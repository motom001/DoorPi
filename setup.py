#!/usr/bin/env python3

import os
import sys

from doorpi import metadata
from setuptools import setup, find_packages
from setuptools.command.install import install


base_path = os.path.dirname(os.path.abspath(__file__))
etc = "/etc" if sys.prefix == "/usr" else "etc"
os.chdir(base_path)


# Python version check
if sys.version_info[:2] < (3, 6):
    print("*** ERROR: Current python version is too old", file=sys.stderr)
    print("This application requires Python 3.6 or newer", file=sys.stderr)
    print("Please upgrade your Python installation", file=sys.stderr)
    sys.exit(1)


def read(filename):
    with open(os.path.join(base_path, filename)) as f:
        file_content = f.read()
    return file_content


# Hook install command to process template files (*.in)
class installhook(install):
    def run(self):
        package = metadata.package.lower()
        substkeys = {
            "package": package,
            "project": metadata.project,
            "prefix": self.prefix,
            "cfgdir": f"/etc/{package}" if sys.prefix == "/usr" else f"{self.prefix}/etc/{package}"
        }
        substfiles = [f for f in os.listdir("data") if f.endswith(".in")]
        for f in substfiles:
            with open(os.path.join(base_path, "data", f[:-3]), "w") as outfile, \
                    open(os.path.join(base_path, "data", f), "r") as tplfile:
                content = tplfile.read()
                for k, v in substkeys.items():
                    content = content.replace(f"!!{k}!!", v)
                outfile.write(content)
        super().run()


setup(
    cmdclass={"install": installhook},
    license=metadata.license,
    name=metadata.package,
    version=metadata.version,
    author=metadata.authors[0],
    author_email=metadata.emails[0],
    maintainer=metadata.authors[0],
    maintainer_email=metadata.emails[0],
    url=metadata.url,
    keywords=metadata.keywords,
    description=metadata.description,
    long_description=read("README.rst"),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "Intended Audience :: End Users/Desktop",
        "Intended Audience :: Information Technology",
        "Intended Audience :: System Administrators",
        "License :: Free for non-commercial use",
        "Natural Language :: German",
        "Natural Language :: English",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3 :: Only",
        "Topic :: Communications :: Internet Phone",
        "Topic :: Communications :: Telephony",
        "Topic :: Home Automation",
        "Topic :: Multimedia :: Sound/Audio :: Capture/Recording",
        "Topic :: Multimedia :: Video :: Capture",
        "Topic :: Security",
        "Topic :: System :: Hardware",
        "Topic :: Utilities",
    ],
    packages=find_packages(exclude=["contrib", "docs", "tests*"]),
    install_requires=["requests >= 2.7.0"],
    extras_require={
        "camera": ["picamera >= 1.10"],
        "files_pseudokb": ["watchdog >= 0.8.3"],
        "gpio": ["RPi.GPIO >= 0.5.11"],
        "piface": ["pifacecommon >= 4.1.2", "pifacedigitalio >= 3.0.5"],
        "rfid": ["pyserial >= 2.7"],
        "webdoc": ["docutils >= 0.14"],
    },
    platforms=["any"],
    use_2to3=False,
    zip_safe=False,  # don't use eggs
    entry_points={
        "console_scripts": [
            "doorpi_cli = doorpi.main:entry_point"
        ]
    },
    data_files=[
        # default config file
        (f"{etc}/doorpi", ["data/doorpi.ini"]),
        # init script and systemd service
        (f"{etc}/init.d", ["data/doorpi.sh"]),
        ("lib/systemd/system", ["data/doorpi.service", "data/doorpi.socket"]),
        # default dialtone
        ("share/doorpi", ["data/dialtone.wav"]),
    ],
)
