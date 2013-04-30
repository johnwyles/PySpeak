"""
  Commandline
"""

import argparse
import logging

from pyspeak import __version__
from listener import Listener


def execute():
    # Parse command line arguments
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    subparsers = parser.add_subparsers(help='Subcommand for pyspeak to either listen for microphone input (speech-to-text) or text input (text-to-speech)')
    parser_listener = subparsers.add_parser('listen', help='Listen for microphone input (speech-to-text)')
    parser_listener.add_argument('-f', '--filename-prefix', default='pyspeak_file', help='Default prefix location and filename for the temporary file %(prog) uses to store data.  This stores a .wav and .flac file of this prefix (e.g. "./pyspeak_file" => [./pyspeak_file.wav, ./pyspeak_file.flac])')
    parser_listener.add_argument('-s', '--silence-time', type=int, default=2, help='Amount of silence time (in seconds) to listen for before dispatching voice data for recognition')
    parser_listener.add_argument('-t', '--threshold', type=int, default=60, help='Threshold for detecting speech input; depending on your microphone settings you may need to experiment a bit with this value')

    parser_speaker = subparsers.add_parser('speak', help='Listen for text input (text-to-speech')

    parser.add_argument('-l', '--loglevel', default='INFO', choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'], help='Log level for console output')
    parser.add_argument('-v', '--version', help='Get the version number and exit', action='store_true')
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

    listener = Listener(silence_time=arguments.silence_time, threshold=arguments.threshold, filename_prefix=arguments.filename_prefix)
    listener.start()
