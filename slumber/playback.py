"""
Slumber playback code

Makes use of the pygame mixer
"""

import datetime
import logging
import os

import pygame

from glob import glob
from functools import partial

class PlaybackManager(object):
    """
    The playback manager takes care of playing back sounds
    """

    def __init__(self, sounds_directory):
        """
        Initialize the playback manager

        :param sounds_directory: The directory where we can find our sounds.  It should be organized into numbered
                                 directories for each of the stages.
        """
        self.log = logging.getLogger('playback')

        self.loop = None

        # this will be used to track our currently playing sounds
        self.sounds = {}
        self.stages = []
        self.current_stage = None
        self.load_sounds(sounds_directory)

        # force the sdl video driver to be 'dummy' driver so we don't get a pygame window
        os.environ["SDL_VIDEODRIVER"] = "dummy"

        # init pygame
        pygame.init()

    def load_sounds(self, sounds_directory):
        """
        Load sounds from our sounds directory
        """
        self.log.info("Loading sounds from: %s", sounds_directory)

        stages = glob(os.path.join(sounds_directory, '*'))
        self.log.debug("Found stages: %s", stages)

        for stage in stages:
            if not os.path.isdir(stage):
                self.log.error("Invalid stage: %s -- skipping", stage)
                continue
            self.stages.append(stage)
            self.sounds[stage] = glob(os.path.join(stage, '*'))
            self.log.debug("Found sounds for stage %s: %s", stage, self.sounds[stage])

    def start(self, loop):
        """
        Start playback via an event loop

        :param: loop: the event loop to use
        """
        self.loop = loop
        self.messing_around()

    def messing_around(self):
        self.log.debug("Playing")
        c1 = pygame.mixer.Channel(1)
        sound = pygame.mixer.Sound('sounds/0/24511__glaneur-de-sons__riviere-river_SLUMBER.wav')
        c1.play(sound, -1)
        self.fade_out(c1, 20)

    def fade_in(self, channel, duration, callback=None):
        """
        Fades a channel in over the specified duration

        :param channel: A pygame channel object
        :param duration: The duration the fade_in should occur over, in seconds
        :param callback: An optional callback to run upon completion
        """
        self._do_fade(channel, duration, start=0.0, target=1.0, callback=callback)

    def fade_out(self, channel, duration, callback=None):
        """
        Fades a channel out over the specified duration

        :param channel: A pygame channel object
        :param duration: The durationt he fade_out should occur over, in seconds
        :param callback: An optional callback to run upon completion
        """
        self._do_fade(channel, duration, start=1.0, target=0.0)

    def _do_fade(self, channel, duration, start, target, callback=None):
        """
        Starts a fade on a channel, used by fade_in & fade_out

        :param channel: The pygame channel
        :param duration: The duration, in seconds
        :param start: The volume to start at
        :param target: The target volume
        :param callback: An optional callback to run upon completion
        """
        # adjust the volume twice a second
        seconds_step = 0.5

        # calculate how much the volume needs to change each step
        if start < target:
            step = (target - start) / (duration / seconds_step)
        else:
            step = (start - target) / (duration / seconds_step) * -1

        channel.set_volume(start)
        callback = partial(self._fade_step, channel, step, target, seconds_step, callback)
        self.log.debug("_do_fade: channel=%s, duration=%f, start=%f, target=%f, step=%f",
                                  channel, duration, start, target, step)
        self.loop.add_callback(callback, deadline={'seconds': seconds_step})

    def _fade_step(self, channel, step, target, seconds_step, callback=None):
        """
        The callback used by the event loop to do the actual fading.

        :param channel: The pygame channel
        :param step: How much to step each iteration
        :param target: The target to fade to
        :param seconds_step: How often to re-run this step
        :param callback: An optional callback to run once we reach our target
        """
        new_volume = channel.get_volume() + step
        channel.set_volume(new_volume)

        if new_volume != target:
            # repeat the fade step
            callback = partial(self._fade_step, channel, step, target, seconds_step, callback)
            self.loop.add_callback(callback, deadline={'seconds': seconds_step})

        elif hasattr(callback, '__call__'):
            # we have reached our target, call the callback -- if we have one
            callback()
