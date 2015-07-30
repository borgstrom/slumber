"""
Slumber CLI interface
"""

import argparse
import logging

from slumber.eventloop import EventLoop
from slumber.playback import PlaybackManager

def main():
    """
    Main entry point
    """
    parser = argparse.ArgumentParser(description='Slumber - Sleep better')
    parser.add_argument('--debug', action='store_true',
                        help='Turn on debug logging')
    parser.add_argument('--sounds', '-s', required=True,
                        help='The directory to load sounds from.  It should be organized into numbered directories.')
    args = parser.parse_args()

    if args.debug:
        log_format = '%(asctime)s %(name)-10s %(levelname)-8s %(message)s'
        log_level = logging.DEBUG
    else:
        log_format = '%(asctime)s %(message)s'
        log_level = logging.INFO

    logging.basicConfig(level=log_level, format=log_format)

    log = logging.getLogger('main')

    log.info('Slumber - Starting...')

    loop = EventLoop.current()

    # add sensor collection into the loop
    # XXX TODO

    # create the playback manager
    playback_manager = PlaybackManager(args.sounds)
    playback_manager.start(loop)

    # run our event loop, this will block
    try:
        loop.start()
    except (KeyboardInterrupt, SystemExit):
        pass
