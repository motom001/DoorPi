# -*- coding: utf-8 -*-

from ez_setup import use_setuptools
use_setuptools()

try:
    from setuptools import setup, find_packages
    packages = find_packages(exclude=['contrib', 'docs', 'tests*'])
except ImportError:
    from distutils.core import setup
    packages = ['doorpi', 'doorpi.status', 'doorpi.action', 'doorpi.keyboard', 'doorpi.conf', 'doorpi.media', 'doorpi.sipphone', 'doorpi.status.requirements_lib', 'doorpi.status.webserver_lib', 'doorpi.status.status_lib', 'doorpi.action.SingleActions', 'doorpi.sipphone.linphone_lib', 'doorpi.sipphone.pjsua_lib']

import imp, os, uuid
from pip.req import parse_requirements

base_path = os.path.dirname(os.path.abspath(__file__))
metadata = imp.load_source('metadata', os.path.join(base_path, 'doorpi', 'metadata.py'))
install_reqs = parse_requirements(os.path.join(base_path, 'requirements.txt'), session=uuid.uuid1())
reqs = [str(req.req) for req in install_reqs]

def read(filename):
    with open(os.path.join(os.path.dirname(__file__), filename)) as f:
        return f.read()

setup_dict = dict(
    license = metadata.license,
    name = metadata.package,
    version = metadata.version,
    author = metadata.authors[0],
    author_email = metadata.emails[0],
    maintainer = metadata.authors[0],
    maintainer_email = metadata.emails[0],
    url = metadata.url,
    keywords = metadata.keywords,
    description = metadata.description,
    long_description = read('README.rst'),
    # Find a list of classifiers here:
    # <http://pypi.python.org/pypi?%3Aaction=list_classifiers>
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: End Users/Desktop',
        'Intended Audience :: Information Technology',
        'Intended Audience :: System Administrators',
        'License :: Free for non-commercial use',
        'Natural Language :: German',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: Implementation :: PyPy',
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
    packages = packages,
    install_requires = reqs,
    platforms = ["any"],
    use_2to3 = True,
    zip_safe = False,  # don't use eggs
    entry_points = {
        'console_scripts': [
            'doorpi_cli = doorpi.main:entry_point'
        ],
        # if you have a gui, use this
        # 'gui_scripts': [
        #     'doorpi_gui = doorpi.gui:entry_point'
        # ]
    }

# <http://pythonhosted.org/setuptools/setuptools.html>
)
def main():
    setup(**setup_dict)

if __name__ == '__main__':
    main()
