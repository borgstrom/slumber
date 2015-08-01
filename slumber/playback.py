"""
Slumber playback code

Makes use of the pygame mixer
"""

import copy
import logging
import os
import random

import pygame

from glob import glob
from functools import partial

from slumber.eventloop import coroutine

class PlaybackException(Exception):
    pass

class NoSounds(PlaybackException):
    pass

class NoMoreChannels(PlaybackException):
    pass

class InvalidPlaybackCommand(PlaybackException):
    pass

class InvalidChannel(PlaybackException):
    pass


class PlaybackCommands(object):
    """
    This class reads the SLUMBER files in each stage and executes the commands inside them
    """

    def __init__(self, manager, stage):
        """
        Setup our attributes, load our sounds & validate our commands
        """
        self.log = logging.getLogger('commands')

        self.manager = manager
        self.stage = stage

        self.sound_files = glob(os.path.join(stage, '*.wav'))
        if len(self.sound_files) == 0:
            raise NoSounds("The stage %s does not contain any sounds!", stage)

        self.command_file = os.path.join(stage, 'SLUMBER')
        self.original_commands = []
        self.commands = []

        self.sounds = {}
        self.sound_file = None
        self.swap_sound_file = None
        self.swapping = False
        self.swapped = False

        self.log.info("Initializing playback command for %s", stage)
        self.log.debug("Reading command file: %s", self.command_file)

        # validate the commands
        for line in open(self.command_file).readlines():
            line = line.strip()
            try:
                func_name, arg_string = line.split(" ", 1)
            except ValueError:
                func_name = line
                arg_string = ""

            func_name = 'command_%s' % func_name
            command_func = getattr(self, func_name)
            if command_func is None:
                raise InvalidPlaybackCommand(func_name)

            self.log.debug(" - %s -> %s", line, command_func)
            self.original_commands.append((command_func, arg_string.split()))

    @coroutine
    def start(self):
        self.log.info("Starting playback for %s", self.stage)
        self.commands = copy.copy(self.original_commands)
        yield self.next_command()

    @coroutine
    def finish_swap(self):
        self.sounds[self.sound_file].stop()
        del self.sounds[self.sound_file]

        self.sound_file = copy.copy(self.swap_sound_file)
        self.swap_sound_file = None
        self.swapping = False
        self.swapped = True

        yield self.start()

    @coroutine
    def next_command(self):
        try:
            func, args = self.commands.pop(0)
        except IndexError:
            # this means we are out of commands, re-start
            # are we swapping?
            if self.swapping:
                yield self.finish_swap()
            else:
                yield self.start()
        else:
            self.log.debug("[%s] Running next command: %s, %s", self.stage, func, args)
            yield func(*args)

    def new_sound(self):
        """
        Returns a new sound file
        """
        new_sound = random.choice(self.sound_files)

        # if we have a current sound, and more than one total sounds then we want to make sure the new sound
        # isn't the same as what's currently playing
        if self.sound_file is not None and len(self.sound_files) > 1:
            while new_sound == self.sound_file:
                new_sound = random.choice(self.sound_files)

        return new_sound

    def command_play(self, fade_duration=0):
        fade_duration = int(fade_duration) * 1000

        if self.swapped:
            self.swapped = False
            self.log.debug("Swap complete")
        else:
            if self.sound_file and self.sound_file in self.sounds:
                self.sounds[self.sound_file].stop()
                del self.sounds[self.sound_file]

            self.sound_file = self.new_sound()
            self.log.debug("[%s] Playing %s", self.stage, self.sound_file)
            self.sounds[self.sound_file] = pygame.mixer.Sound(self.sound_file)
            self.sounds[self.sound_file].play(-1, fade_ms=fade_duration)

        self.command_wait(fade_duration / 1000)

    def command_fadeout(self, duration):
        duration = int(duration) * 1000
        if self.sound_file and self.sound_file in self.sounds:
            self.sounds[self.sound_file].fadeout(duration)

        self.command_wait(duration / 1000)

    def command_wait(self, duration):
        duration = int(duration)
        self.manager.loop.add_callback(self.next_command, deadline={'seconds': duration})

    def command_swap(self, duration):
        duration = int(duration) * 1000

        if self.sound_file and self.sound_file in self.sounds:
            self.swapping = True
            self.swap_sound_file = self.new_sound()
            self.log.info("[%s] Swapping with %s", self.stage, self.swap_sound_file)
            self.sounds[self.swap_sound_file] = pygame.mixer.Sound(self.swap_sound_file)
            self.sounds[self.swap_sound_file].play(-1, fade_ms=duration)
            self.sounds[self.sound_file].fadeout(duration)

        self.command_wait(duration / 1000)

    def command_set_volume(self, volume):
        volume = float(volume)
        if self.sound_file and self.sound_file in self.sounds:
            self.sounds[self.sound_file].set_volume(volume)

        self.command_wait(0)


class PlaybackManager(object):
    """
    The playback manager takes care of starting a PlaybackCommand object for each stage
    """

    def __init__(self, loop, sounds_directory):
        """
        Initialize the playback manager

        :param sounds_directory: The directory where we can find our sounds.  It should be organized into numbered
                                 directories for each of the stages.
        """
        self.log = logging.getLogger('playback')

        self.loop = loop

        # this will be used to track our currently playing sounds
        self.commands = {}
        self.sounds = {}
        self.stages = []
        self.load_sounds(sounds_directory)

        # pygame gives us 8 channels to work with
        self.channels = dict([
            (x, None)
            for x in range(8)
        ])

        # force the sdl video driver to be 'dummy' driver so we don't get a pygame window
        os.environ["SDL_VIDEODRIVER"] = "dummy"

        # init pygame
        pygame.init()
        self.loop.add_shutdown_callback(pygame.quit)

    def load_sounds(self, sounds_directory):
        """
        Load sounds from our sounds directory
        """
        self.log.info("Loading sounds from: %s", sounds_directory)

        stages = glob(os.path.join(sounds_directory, '*'))
        stages.sort()
        self.log.debug("Found stages: %s", stages)

        for stage in stages:
            if not os.path.isdir(stage):
                self.log.error("Invalid stage: %s -- it is not a directory", stage)
                continue

            slumber_file = os.path.join(stage, 'SLUMBER')
            if not os.path.exists(slumber_file):
                self.log.error("Invalid stage: %s -- missing SLUMBER file (%s)", stage, slumber_file)
                continue

            # now we know this is a valid stage, setup the command object for it
            self.commands[stage] = PlaybackCommands(self, stage)

            self.stages.append(stage)

    @coroutine
    def start(self):
        """
        Start playback via an event loop

        :param: loop: the event loop to use
        """
        for stage in self.stages:
            yield self.commands[stage].start()
