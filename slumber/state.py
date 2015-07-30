"""
Slumber State implementation

http://psychcentral.com/lib/stages-of-sleep/
"""

import datetime

from slumber.eventloop import EventLoop

class State(object):
    """
    Base implementation used by all states
    """
    def __init__(self, machine):
        self.machine = machine

    def get_data(self, name, default=None):
        """
        Get data from our machine
        """
        return self.machine.data.get(name, default=default)

    def set_data(self, name, value):
        """
        Set a value in our machine
        """
        self.machine.date[name] = value

    def start(self):
        """
        Called when we transition into this state

        By default it does nothing
        """
        pass

    def next(self):
        """
        Called to determine what the next state is
        """
        raise NotImplemented("This needs to be implemented by each State")

    def stop(self):
        """
        Called when we transition out of this state

        By default it does nothing
        """
        pass

class StateMachine(object):
    """
    """
    def __init__(self, loop=None):
        # general purpose data storage for use by our states
        self.data = {}

        self.current_state = None
        self.current_instance = None

        if loop is None:
            loop = EventLoop.current()
        self.loop = loop

    def start(self, initial_state):
        """
        Start the state machine
        """
        self.current_state = initial_state
        self.current_instance = initial_state(self)
        self.current_instance.start()

    def next(self):
        """
        Advance the state machine
        """
        next_state = self.current_instance.next()

        if next_state == self.current_state:
            # no transition is occurring
            return

        # transitioning
        self.current_instance.stop()

        # replace the current with next
        self.current_state = next_state
        self.current_instance = next_state(self)
        self.current_instance.start()


class Awake(State):
    """
    Fully awake

    This is currently a dummy stage that just transitions to Stage1.  In the future this should evaluate the environment
    and transition when we're ready to goto sleep (button press? microphone?)
    """
    def next(self):
        return Stage1

class TimedState(State):
    """
    A state that is bound by time
    """
    timedelta = None
    next_state = None

    def start(self):
        self.end_name = "_".join([self.__class__.__name__, "end"])
        self.set_data(end_name, datetime.datetime.now() + self.timedelta)

    def next(self):
        if datetime.datetime.now() < self.get_data(self.end_name):
            return self.__class__
        return self.next_state

class Stage1(TimedState):
    """
    Going through Alpha & Theta

    Play a sound from 1, 2 & 3.

    All start at 100% volume.

    3 fades to 0 over the stage.

    ~10 minutes
    """
    timedelta = datetime.timedelta(minutes=10)
    next_state = Stage2

    def start(self):
        super(Stage1, self).start()


class Stage2(TimedState):
    """
    Body temp is dropping and heart rate is slowing

    ~20 minutes
    """
    timedelta = datetime.timedelta(minutes=20)
    next_state = Stage3

class Stage3(State):
    """
    Delta Waves


    """
    def next(self):
        return Stage4
