#!/usr/bin/env python
# -*- coding: utf-8 -*-


import argparse
import sys
import metadata

def main(argv):
    """Program entry point.

    :param argv: command-line arguments
    :type argv: :class:`list`
    """
    author_strings = []
    for name, email in zip(metadata.authors, metadata.emails):
        author_strings.append('Author: {0} <{1}>'.format(name, email))

    epilog = '''
{project} {version}

{authors}
URL: <{url}>
'''.format(
        project=metadata.project,
        version=metadata.version,
        authors='\n'.join(author_strings),
        url=metadata.url)

    arg_parser = argparse.ArgumentParser(
        prog=argv[0],
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=metadata.description,
        epilog=epilog)
    arg_parser.add_argument(
        '-V', '--version',
        action='version',
        version='{0} {1}'.format(metadata.project, metadata.version))
    arg_parser.add_argument(
        '--configfile',
        help='configfile for DoorPi - optional --create_demo_config',
        type=file,
        required=True,
        dest='configfile'
    )

    parsed_arguments =  arg_parser.parse_args(args=argv[1:])
    logger.info(epilog)

    try:
        import doorpi
    except ImportError as exc:
        logger.critical("Error: failed to import settings module ({})".format(exc))
        return 1
    else:
        doorpi.DoorPi()
        doorpi.DoorPi().prepare(configfile = parsed_arguments.configfile)
        doorpi.DoorPi().run()
        doorpi.DoorPi().destroy()
    return 0

def entry_point():
    """Zero-argument entry point for use with setuptools/distribute."""
    raise SystemExit(main(sys.argv))

def init_logger():
    import logging
    import logging.handlers

    LOG_FILENAME = '/var/log/doorpi/doorpi.log'
    LOG_FORMAT = '%(asctime)s [%(levelname)s]  \t[%(name)s] %(message)s'
    logging.basicConfig(
        filename = LOG_FILENAME,
        level = logging.DEBUG,
        format = LOG_FORMAT
    #    datefmt = '%m/%d/%Y %I:%M:%S %p'
    )
    # define a Handler which writes INFO messages or higher to the sys.stderr
    console = logging.StreamHandler()
    console.setLevel(logging.DEBUG) # TODO: only INFO or ERROR?
    console.setFormatter(logging.Formatter(LOG_FORMAT))

    logrotating = logging.handlers.RotatingFileHandler(
              LOG_FILENAME, maxBytes=5000, backupCount=5)

    # add the handler to the root logger
    logging.getLogger('').addHandler(console)
    logging.getLogger('').addHandler(logrotating)

    return logging.getLogger(__name__)

if __name__ == '__main__':
    logger = init_logger()
    entry_point()
