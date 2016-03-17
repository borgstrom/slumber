"""
Slumber CLI interface
"""

import argparse
import logging
import signal

from slumber.eventloop import EventLoop
from slumber.playback import PlaybackManager

def main():
    """
    Main entry point
    """
    parser = argparse.ArgumentParser(description='Slumber - Sleep better')
    parser.add_argument('--debug', action='store_true',
                        help='Turn on debug logging and USR1 breakpoint')
    parser.add_argument('--sounds', '-s', required=True,
                        help='The directory to load sounds from.  It should be organized into numbered directories.')
    parser.add_argument('--timer', '-t', required=False, type=int,
                        help='Set a sleep timer in minutes.')
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

    if args.debug:
        import code, traceback 

        def debug_interrupt(sig, frame):
            debug_locals = dict(frame=frame)
            debug_locals.update(frame.f_globals)
            debug_locals.update(frame.f_locals)

            console = code.InteractiveConsole(locals=debug_locals)
            console.interact("\n".join([
                "Signal %d received.  Entering Python shell." % sig,
                "-" * 50,
                "Traceback:",
                ''.join(traceback.format_stack(frame))
            ]))

        signal.signal(signal.SIGUSR1, debug_interrupt)

    # set a sleep timer in minutes, minimalist
    if args.timer:
        # use SystemExit since that's already caught for debug
        def stexit(sig, frame):
          raise SystemExit
        signal.signal(signal.SIGALRM, stexit)
        signal.alarm(args.timer * 60)

    loop = EventLoop.current()

    # create the playback manager
    playback_manager = PlaybackManager(loop, args.sounds)
    loop.add_callback(playback_manager.start)

    # run our event loop, this will block
    try:
        loop.start()
    except (KeyboardInterrupt, SystemExit):
        loop.stop()

if __name__ == '__main__':
    main()

