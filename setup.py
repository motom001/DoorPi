#!/usr/bin/python
# -*- coding: utf-8 -*-

import imp
import os
import sys


try:
    import pip
    from pip.req import parse_requirements
    from setuptools import setup, find_packages
    # import wheel
except ImportError as exp:
    print("DoorPi-Error 1000 -> %s" % exp)
    sys.exit(1)


def main():
    base_path = os.path.dirname(os.path.abspath(__file__))
    install_requirements = parse_requirements(
        os.path.join(base_path, 'requirements.txt'),
        session=pip.download.PipSession()
    )
    requirements = [str(req.req) for req in install_requirements]
    metadata = imp.load_source('metadata', os.path.join(base_path, 'doorpi', 'resources', 'metadata', '__init__.py'))
    with open(os.path.join(base_path, 'README.rst')) as f:
        content_readme = f.read()
    with open(os.path.join(base_path, 'changelog.txt')) as f:
        content_changelog = f.read()

    setup_dict = dict(
        # <http://pythonhosted.org/setuptools/setuptools.html>
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
        long_description=content_readme + content_changelog,
        package_data={
            # If any package contains *.txt or *.rst files, include them:
            '': ['*.txt', '*.rst'],
            # And include any *.msg files found in the 'hello' package, too:
            'hello': ['*.msg'],
        },
        # Find a list of classifiers here:
        # <http://pypi.python.org/pypi?%3Aaction=list_classifiers>
        classifiers=metadata.classifiers,
        packages=find_packages(exclude=['contrib', 'docs', 'tests*']),
        install_requires=requirements,
        platforms=["any"],
        use_2to3=True,
        zip_safe=False,  # don't use eggs
        entry_points={
            'console_scripts': [
                'doorpi_cli = doorpi.main:entry_point'
            ]
        }
    )
    return setup(**setup_dict)

if __name__ == '__main__':
    raise SystemExit(
        main()
    )
