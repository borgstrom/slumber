import copy
import os
import shutil
import sys
import tempfile

from unittest import TestCase
try:
    from unittest.mock import MagicMock, patch, call
except ImportError:
    from mock import MagicMock, patch, call

from slumber.eventloop import EventLoop
from slumber.playback import PlaybackCommands, PlaybackManager

class PlaybackManagerTests(TestCase):
    def setUp(self):
        self.sounds_dir = tempfile.mkdtemp()
        self.stages = []

        for x in range(2):
            stage_dir = os.path.join(self.sounds_dir, str(x))
            os.mkdir(stage_dir)
            for y in range(3):
                open(os.path.join(stage_dir, "sound%d.wav" % y), 'w').write("RIFF0WAV")
                open(os.path.join(stage_dir, "SLUMBER"), 'w').write("play")

            self.stages.append(stage_dir)

    def tearDown(self):
        shutil.rmtree(self.sounds_dir, ignore_errors=True)

    @patch('slumber.playback.pygame')
    def test_init(self, pygame):
        loop = EventLoop.current()
        manager = PlaybackManager(loop, self.sounds_dir)

        self.assertEqual(manager.stages, self.stages)

        for stage in self.stages:
            command = manager.commands[stage]
            self.assertEqual(len(command.sound_files), 3)

class PlaybackCommandsTests(TestCase):
    commands = [
        "play 5",
        "wait 5",
        "fadeout 5",
        "set_volume 0.9",
        "swap 5"
    ]

    def setUp(self):
        """
        Setup our stage
        """
        self.stage = tempfile.mkdtemp()

        stage_path = lambda x: os.path.join(self.stage, x)
        self.command_file = stage_path('SLUMBER')
        open(self.command_file, 'w').write("\n".join(self.commands))

        for x in range(4):
            open(stage_path('sound-%d.wav' % x), 'w').write("RIFF0WAV")

    def tearDown(self):
        """
        Remove what we setup
        """
        shutil.rmtree(self.stage, ignore_errors=True)

    def test_init(self):
        """
        Test the initialization
        """
        manager = MagicMock()
        commands = PlaybackCommands(manager, self.stage)

        self.assertEqual(len(commands.sound_files), 4)

        self.assertEqual(commands.original_commands, [
            (commands.command_play, ["5"]),
            (commands.command_wait, ["5"]),
            (commands.command_fadeout, ["5"]),
            (commands.command_set_volume, ["0.9"]),
            (commands.command_swap, ["5"]),
        ])

    @patch('slumber.playback.PlaybackCommands.command_wait')
    @patch('slumber.playback.pygame')
    def test_start(self, pygame, command_wait):
        """
        Test processing of the commands
        """
        loop = EventLoop.current()

        manager = MagicMock()
        manager.loop = loop
        commands = PlaybackCommands(manager, self.stage)
        commands.testing = True
        commands.test_wait_durations = []

        # we've mocked out the command_wait method of PlaybackCommands
        # use a side_effect to make it work again, but ignore durations
        def test_command_wait(duration):
            commands.test_wait_durations.append(int(duration))
            commands.next_command()
        command_wait.side_effect = test_command_wait

        # start command processing, this is a coroutine and requires that the loop run
        commands.start()

        # run the loop, stopping it in 0.25 seconds
        loop.add_callback(loop.stop, {'seconds': 0.25})
        loop.start()

        # make sure things worked as expected
        pygame.mixer.Sound.assert_has_calls([
            call(commands.sound_file),
            call().play(-1, fade_ms=5000),
            call().fadeout(5000),
            call().set_volume(0.9),

            call(commands.swap_sound_file),
            call().play(-1, fade_ms=5000),
            call().fadeout(5000)
        ])

        # command_wait was mocked out and we logged the durations
        self.assertEqual(commands.test_wait_durations, [5, 5, 5, 0, 5])

        # finish the swap
        original_sound_file = copy.copy(commands.sound_file)
        self.assertTrue(original_sound_file in commands.sounds)
        self.assertNotEqual(commands.swap_sound_file, None)
        self.assertTrue(commands.swapping)
        self.assertFalse(commands.swapped)

        commands._complete_swap()

        self.assertFalse(original_sound_file in commands.sounds)
        self.assertEqual(commands.swap_sound_file, None)
        self.assertFalse(commands.swapping)
        self.assertTrue(commands.swapped)
