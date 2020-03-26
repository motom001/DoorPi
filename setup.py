#!/usr/bin/env python3

import sys
from pathlib import Path

from setuptools import setup, find_packages
from setuptools.command.install import install

from doorpi import metadata


BASE_PATH = Path(__file__).resolve().parent
ETC = "/etc" if sys.prefix == "/usr" else "etc"


# Python version check
if sys.version_info[:2] < (3, 6):
    print("*** ERROR: Current python version is too old", file=sys.stderr)
    print("This application requires Python 3.6 or newer", file=sys.stderr)
    print("Please upgrade your Python installation", file=sys.stderr)
    sys.exit(1)


class InstallHook(install):
    """Hook for ``install`` command that processes template files (*.in)"""
    def run(self):
        datapath = BASE_PATH / "data"
        package = metadata.package.lower()
        substkeys = {
            "package": package,
            "project": metadata.project,
            "prefix": self.prefix,
            "cfgdir": f"{self.prefix if sys.prefix == '/usr' else ''}/etc/{package}"
        }
        for file in datapath.iterdir():
            if file.suffix != ".in": continue
            content = file.read_text()
            for key, val in substkeys.items():
                content = content.replace(f"!!{key}!!", val)
            file.with_suffix("").write_text(content)
        super().run()


setup(
    cmdclass={"install": InstallHook},
    license=metadata.license,
    name=metadata.package,
    version=metadata.version,
    author=metadata.authors[0],
    author_email=metadata.emails[0],
    maintainer=metadata.authors[0],
    maintainer_email=metadata.emails[0],
    url=metadata.url,
    keywords=["intercom", "VoIP", "doorstation", "home automation", "IoT"],
    description=metadata.description,
    long_description=Path("README.rst").read_text(),
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
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
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
            "doorpi = doorpi.main:entry_point",
        ]
    },
    data_files=[
        # default config file
        (f"{ETC}/doorpi", ["data/doorpi.ini"]),
        # init script and systemd service
        (f"{ETC}/init.d", ["data/doorpi.sh"]),
        ("lib/systemd/system", ["data/doorpi.service", "data/doorpi.socket"]),
        # default dialtone
        ("share/doorpi", ["data/dialtone.wav"]),
    ],
)
