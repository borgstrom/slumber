import datetime

from unittest import TestCase

from slumber.eventloop import EventLoop, coroutine

class EventLoopTests(TestCase):
    def setUp(self):
        self.coroutine_results = []

    @coroutine
    def add_coroutine_results(self):
        yield self.coroutine_results.append(1)
        yield self.coroutine_results.append(2)
        yield self.coroutine_results.append(3)

    def test_coroutine(self):
        """
        Test the @coroutine decorator
        """
        loop = EventLoop.current()

        # run the coroutine
        self.add_coroutine_results()

        # since the loop isn't running the results will still be empty
        self.assertEqual(self.coroutine_results, [])

        # run the loop, stopping it in 0.25 seconds
        loop.add_callback(loop.stop, {'seconds': 0.25})
        loop.start()

        # our results will now be populated
        self.assertEqual(self.coroutine_results, [1, 2, 3])

    def test_add_callback(self):
        """
        Test the add_callback function
        """
        loop = EventLoop.current()

        def the_callback():
            pass

        loop.add_callback(the_callback)
        self.assertEqual(loop.callbacks[0], (the_callback, None))

        # when we're testing the dictionary method of creating a deadline we need to drop the microseconds
        # component when we're comparing since they'll never be the same
        one_second_from_now = datetime.datetime.now() + datetime.timedelta(seconds=1)
        loop.add_callback(the_callback, {'seconds': 1})
        self.assertEqual(loop.callbacks[1][0], the_callback)
        self.assertEqual(loop.callbacks[1][1].replace(microsecond=0), one_second_from_now.replace(microsecond=0))

        one_minute_from_now = datetime.datetime.now() + datetime.timedelta(minutes=1)
        loop.add_callback(the_callback, one_minute_from_now)
        self.assertEqual(loop.callbacks[2], (the_callback, one_minute_from_now))

        loop.add_shutdown_callback(the_callback)
        self.assertEqual(loop.shutdown_callbacks, [the_callback])
