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

        self.sounds = glob(os.path.join(stage, '*.wav'))
        if len(self.sounds) == 0:
            raise NoSounds("The stage %s does not contain any sounds!", stage)

        self.command_file = os.path.join(stage, 'SLUMBER')
        self.original_commands = []
        self.commands = []
        self.current_command = -1

        self.channel = None
        self.current_sound = None
        self.swapping = False
        self.swapped = False
        self.swap_channel = None
        self.swap_sound = None

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
        if self.channel is None:
            self.channel = self.manager.get_channel()

        yield self.process_commands()

    @coroutine
    def finish_swap(self):
        self.manager.release_channel(self.channel)
        self.channel = copy.copy(self.swap_channel)
        self.current_sound = copy.copy(self.swap_sound)
        self.swap_channel = None
        self.swap_sound = None
        self.swapping = False
        self.swapped = True

        yield self.process_commands()

    @coroutine
    def process_commands(self):
        self.commands = copy.copy(self.original_commands)
        yield self.next_command()

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
        new_sound = random.choice(self.sounds)

        # if we have a current sound, and more than one total sounds then we want to make sure the new sound
        # isn't the same as what's currently playing
        if self.current_sound is not None and len(self.sounds) > 1:
            while new_sound == self.current_sound:
                new_sound = random.choice(self.sounds)

        return new_sound

    def command_play(self, fade_duration=0):
        fade_duration = int(fade_duration) * 1000

        if self.swapped:
            self.swapped = False
        else:
            self.current_sound = self.new_sound()
            self.manager.play(self.channel, self.current_sound, fade_duration)

        self.command_wait(fade_duration / 1000)

    def command_fadeout(self, duration):
        duration = int(duration) * 1000
        self.manager.channels[self.channel].fadeout(duration)
        self.command_wait(duration / 1000)

    def command_wait(self, duration):
        duration = int(duration)
        self.manager.loop.add_callback(self.next_command, deadline={'seconds': duration})

    def command_swap(self, duration):
        duration = int(duration) * 1000

        self.swapping = True
        self.swap_channel = self.manager.get_channel()
        self.swap_sound = self.new_sound()
        self.manager.play(self.swap_channel, self.swap_sound, duration)
        self.manager.channels[self.channel].fadeout(duration)
        self.command_wait(duration / 1000)

    def command_set_volume(self, volume):
        volume = float(volume)
        self.manager.channels[self.channel].set_volume(volume)
        self.command_wait(0)


class PlaybackManager(object):
    """
    The playback manager takes care of playing back sounds
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
        self.current_stage = None
        self.load_sounds(sounds_directory)

        # pygame gives us 8 channels to work with
        self.channels = dict([
            (x, None)
            for x in range(8)
        ])

        # force the sdl video driver to be 'dummy' driver so we don't get a pygame window
        os.environ["SDL_VIDEODRIVER"] = "dummy"

        # init pygame
        pygame.mixer.pre_init(frequency=44100, size=-16, channels=2, buffer=2048)
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

    def start(self):
        """
        Start playback via an event loop

        :param: loop: the event loop to use
        """
        for stage in self.stages:
            self.commands[stage].start()

    def play(self, channel_id, sound_file, fade_duration=0):
        """
        Play a sound on the specified channel

        :param channel_id: The ID of a channel, see get_channel
        :param sound_file: The path of a sound file
        :param fade_duration: The duration to fade in by, in ms
        """
        if channel_id not in self.channels or self.channels[channel_id] is None:
            raise InvalidChannel(channel_id)

        self.log.info("Playing %s on channel %d", sound_file, channel_id)
        sound = pygame.mixer.Sound(sound_file)
        self.channels[channel_id].play(sound, -1, fade_ms=fade_duration)

    def get_channel(self):
        """
        Get a new channel

        :return: The ID of the channel
        """
        for channel_id, channel in self.channels.items():
            if channel is None:
                self.log.debug("Allocating channel %d", channel_id)
                self.channels[channel_id] = pygame.mixer.Channel(channel_id)
                return channel_id

        raise NoMoreChannels("There are no free channels")

    def release_channel(self, channel_id):
        """
        Releases the specified channel

        :param channel_id: The ID of the channel
        """
        if channel_id not in self.channels or self.channels[channel_id] is None:
            raise InvalidChannel(channel_id)

        self.log.debug("Releasing channel %d", channel_id)
        self.channels[channel_id].stop()
        self.channels[channel_id] = None

