"""
This contains the slumber event loop code
"""

import datetime
import functools
import logging
import sys
import time
import types

def coroutine(func):
    """
    This is a decorator used in conjunction with the EventLoop to make callback based code easier to read & write

    It is based off of the syntax that tornado uses::

        @coroutine
        def myfunction():
            yield do_something_right_now()
            yield do_domething_during_the_next_loop()

    Anytime you yield in a function that is called by the event loop, the function will suspend and resume at the
    next loop, allowing for neater code that shares the CPU better.
    """
    loop = EventLoop.current()

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # call the function, this will create a generator object due to the yield statements
        generator = func(*args, **kwargs)

        if not isinstance(generator, types.GeneratorType):
            log = logging.getLogger("coroutine")
            log.error("The function %s is decorated as a coroutine but does not produce a generator", func)
            return generator

        # this is used to iterate through the generator via the event loop
        def drain_generator():
            try:
                if sys.version_info[0] < 3:
                    generator.next()
                else:
                    next(generator)
            except StopIteration:
                # end of the generator
                pass
            else:
                # re-call ourselves during the next loop
                loop.add_callback(drain_generator)

        # make the initial call
        loop.add_callback(drain_generator)
    return wrapper

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
        self.shutdown_callbacks = []

    def start(self):
        """
        Start running the event loop.  This will block.
        """
        self.log.info('Starting event loop')
        self.running = True

        while self.running:
            idle = True
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
                try:
                    callback()
                except Exception:
                    self.log.exception("Failed to run callback")

                # we ran a callback, we're not idle
                # this will re-execute the loop without a sleep to allow for "real-time" interleaving of tasks
                idle = False

            # yield cpu when we're idle
            if idle:
                time.sleep(self.sleep)

    def stop(self):
        """
        Stop the event loop
        """
        self.running = False
        for callback in self.shutdown_callbacks:
            try:
                callback()
            except Exception:
                self.log.exception("Failed to run shutdown callback")

    def add_callback(self, callback, deadline=None):
        """
        Add a callback to be run during the next loop iteration

        :param: callback:  A callable
        :param: deadline:  If specified it should be a datetime object in the future, describing
                           when the callback should run.  It will be compared against
                           datetime.datetime.now()

                           You can also specify a dictionary which will be used as kwargs for
                           datetime.timedelta and added to now.
        """
        if isinstance(deadline, dict):
            deadline = datetime.datetime.now() + datetime.timedelta(**deadline)

        self.callbacks.append((callback, deadline))

    def add_shutdown_callback(self, callback):
        """
        Add a callback to the shutdown callbacks

        :param callback: A callable
        """
        self.shutdown_callbacks.append(callback)
