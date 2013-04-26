"""
  Commandline
"""

import argparse
import logging

from pyspeak import __version__
from listener import Listener

def execute():
    # Parse command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('-l', '--loglevel', default='INFO', help='Log level for console output (DEBUG, INFO, WARNING, ERROR, CRITICAL')
    parser.add_argument('-v', '--version', help='Get the version number and exit', const='version', nargs='?')
    arguments = parser.parse_args()

    # Print the version number and exit
    if arguments.version:
        print __name__ + ": " + __version__
        exit(0)

    # Setup logging
    try:
        number_level = getattr(logging, arguments.loglevel.upper(), None)
        if not isinstance(number_level, int):
            raise ValueError('Invalid log level: %s' % number_level)
    except:
        number_level

    logging.basicConfig(format='[%(asctime)s] [%(name)s] [%(levelname)s]: %(message)s', level=number_level, nargs='?')

    listener = Listener()
    listener.start()
