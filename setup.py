#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
from doorpi import metadata
from setuptools import setup, find_packages
from setuptools.command.install import install as _install

base_path = os.path.dirname(os.path.abspath(__file__))

def read(filename):
    with open(os.path.join(base_path, filename)) as f:
        file_content = f.read()
    return file_content

# Hook `install' command to process template files (*.in)
class install(_install):
    def run(self):
        substkeys={
            'package': metadata.package.lower(),
            'project': metadata.project,
            'prefix': self.prefix,
        }
        substfiles=[f for f in os.listdir('.') if f.endswith('.in')]
        for f in substfiles:
            with open(os.path.join(base_path, f[:-3]), "w") as outfile, open(os.path.join(base_path, f), "r") as tplfile:
                content = tplfile.read()
                for k, v in substkeys.items():
                    content = content.replace('!!%s!!'%k, v)
                outfile.write(content)
        _install.run(self)

setup(
    cmdclass={'install': install},
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
    long_description=read('README.rst'),
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: End Users/Desktop',
        'Intended Audience :: Information Technology',
        'Intended Audience :: System Administrators',
        'License :: Free for non-commercial use',
        'Natural Language :: German',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Topic :: Documentation',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: System :: Installation/Setup',
        'Topic :: System :: Software Distribution',
        'Topic :: Communications :: Internet Phone',
        'Topic :: Communications :: Telephony',
        'Topic :: Multimedia :: Sound/Audio :: Capture/Recording',
        'Topic :: Multimedia :: Video :: Capture',
        'Topic :: Multimedia :: Video :: Conversion',
        'Topic :: Security',
        'Topic :: System :: Emulators',
        'Topic :: System :: Filesystems',
        'Topic :: System :: Hardware',
        'Topic :: Utilities'
    ],
    packages=find_packages(exclude=['contrib', 'docs', 'tests*']),
    install_requires=['requests >= 2.7.0'],
    extras_require={
        'gpio': ['RPi.GPIO >= 0.5.11'],
        'webdoc': ['docutils >= 0.14'],
        'camera': ['picamera >= 1.10'],
        'piface': ['pifacecommon >= 4.1.2', 'pifacedigitalio >= 3.0.5'],
        'rfid': ['pyserial >= 2.7'],
        'files_pseudokb': ['watchdog >= 0.8.3'],
    },
    platforms=["any"],
    use_2to3=False,
    zip_safe=False,  # don't use eggs
    entry_points={
        'console_scripts': [
            'doorpi_cli = doorpi.main:entry_point'
        ]
    },
    data_files=[
        # default config file
        ('/etc/doorpi', ['doorpi.ini']),
        # init script and systemd service
        ('/etc/init.d', ['doorpi.sh']),
        ('/usr/lib/systemd/system', ['doorpi.service', 'doorpi.socket']),
    ],
)
