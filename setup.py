# -*- coding: utf-8 -*-

import imp
import os
import uuid
import sys

base_path = os.path.dirname(os.path.abspath(__file__))
metadata = imp.load_source('metadata', os.path.join(base_path, 'doorpi', 'metadata.py'))

def read(filename, parse_file_content=False, new_filename=None):
    with open(os.path.join(base_path, filename)) as f:
        file_content = f.read()
    if parse_file_content:
        for meta_key in dir(metadata):
            if not meta_key.startswith('__'):
                file_content = file_content.replace('!!%s!!' % meta_key,  str(getattr(metadata, meta_key)))
    if new_filename:
        with open(os.path.join(base_path, new_filename), 'w') as f:
            f.write(file_content)
        return new_filename
    return file_content


def return_parsed_filename(old_filename, new_filename, make_it_executeable=True):
    new_filename = os.path.join(base_path, new_filename)
    with open(new_filename, 'w') as f:
        f.write(read(old_filename, True))
    if make_it_executeable:
        os.chmod(new_filename, 0755)
    return new_filename

# Check for pip, setuptools and wheel
try:
    import pip
    import setuptools
    import wheel
    pip.main(['install', '--upgrade', 'pip', 'setuptools', 'wheel'])
except ImportError:
    print("install missing pip now")
    from get_pip import main as check_for_pip
    old_args = sys.argv
    sys.argv = [sys.argv[0]]
    try:
        check_for_pip()
    except SystemExit as e:
        if e.code == 0:
            os.execv(sys.executable, [sys.executable] + old_args)
        else:
            print("install pip failed with error code %s" % e.code)
            sys.exit(e.code)

from setuptools import setup, find_packages
from pip.req import parse_requirements
install_reqs = parse_requirements(os.path.join(base_path, 'requirements.txt'), session=uuid.uuid1())
reqs = [str(req.req) for req in install_reqs]

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
    long_description=read('README.rst'),
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
        # 'Programming Language :: Python :: 3.3',
        # 'Programming Language :: Python :: Implementation :: PyPy',
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
    install_requires=reqs,
    platforms=["any"],
    use_2to3=False,
    zip_safe=False,  # don't use eggs
    entry_points={
        'console_scripts': [
            'doorpi_cli = doorpi.main:entry_point'
        ],
        # if you have a gui, use this
        # 'gui_scripts': [
        #     'doorpi_gui = doorpi.gui:entry_point'
        # ]
    }

)
if os.name == 'posix':
    setup_dict.update(dict(
        data_files=[(
            metadata.daemon_folder, [
                return_parsed_filename(metadata.daemon_name_template, metadata.daemon_name_template_parsed)
            ]
         )]
    ))

def main():
    setup(**setup_dict)

if __name__ == '__main__':
    main()
