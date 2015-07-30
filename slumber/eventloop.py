"""
This contains the slumber event loop code
"""

import datetime
import functools
import logging
import time

def coroutine(loop=None):
    """
    This is a decorator used in conjunction with the EventLoop to make callback based code easier to read & write

    It is based off of the syntax that tornado uses::

        @coroutine
        def myfunction():
            do_something_right_now()
            yield do_domething_during_the_next_loop()

    Anytime you yield in a function that is called by the event loop, the function will suspend and resume at the
    next loop, allowing for neater code that shares the CPU better.
    """
    if loop is None:
        loop = EventLoop.current()

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # call the function, this will create a generator object due to the yield statements
            generator = func(*args, **kwargs)

            # this is used to iterate through the generator via the event loop
            def drain_generator():
                try:
                    generator.next()
                except StopIteration:
                    # end of the generator
                    pass
                else:
                    # re-call ourselves during the next loop
                    loop.add_callback(drain_generator)

            # make the initial call
            loop.add_callback(drain_generator)
        return wrapper
    return decorator


class EventLoop(object):
    """
    Slumber Event Loop

    Usage::

        from slubmer.eventloop import EventLoop

        loop = EventLoop.current()
        ...
    """

    _instance = None

    @classmethod
    def current(cls):
        """
        Explicit singleton to get an instance of the EventLoop
        """
        if cls._instance is None:
            cls._instance = cls()

        return cls._instance

    def __init__(self, sleep=0.01):
        """
        Setup the event loop.

        :param: sleep: The number of seconds to sleep between each event idle loop iteration
        """
        self.log = logging.getLogger('eventloop')
        self.running = True
        self.sleep = sleep
        self.callbacks = []

    def start(self):
        """
        Start running the event loop.  This will block.
        """
        self.log.info('Starting event loop')
        self.running = True
        while self.running:
            # grab the callbacks from 'self' and then reset self.callbacks to a new empty list
            # we do this to ensure that the callbacks cannot be modified while we iterate over them
            # and also to allow us to simply add our deferred callbacks back onto the stack
            callbacks = self.callbacks
            self.callbacks = []

            for callback, deadline in callbacks:
                if deadline is not None:
                    # deadline should be a datetime object
                    if datetime.datetime.now() < deadline:
                        # the deadline has not come yet, place this callback back onto the stack
                        self.callbacks.append((callback, deadline))
                        continue

                # invoke the callback
                callback()

            # yield cpu
            time.sleep(self.sleep)

    def stop(self):
        """
        Stop the event loop
        """
        self.running = False

    def add_callback(self, callback, deadline=None):
        """
        Add a callback to be run during the next loop iteration

        :param: callback:  A code reference to run
        :param: deadline:  If specified it should be a datetime object in the future, describing
                           when the callback should run.  It will be compared against
                           datetime.datetime.now()

                           You can also specify a dictionary which will be used as kwargs for
                           datetime.timedelta and added to now.
        """
        if isinstance(deadline, dict):
            deadline = datetime.datetime.now() + datetime.timedelta(**deadline)

        self.callbacks.append((callback, deadline))
