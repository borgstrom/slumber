Slumber
=======

.. image:: https://img.shields.io/travis/borgstrom/slumber.svg
   :target: https://travis-ci.org/borgstrom/slumber

.. image:: https://img.shields.io/codecov/c/github/borgstrom/slumber.svg
   :target: https://codecov.io/github/borgstrom/slumber

.. image:: https://img.shields.io/codeclimate/github/borgstrom/slumber.svg
   :target: https://codeclimate.com/github/borgstrom/slumber

This is a noise machine to help you sleep better.  Really it's just an audio playback system that has a simple command
language and comes with a collection of sounds that have been sorted in a specific way.

It is meant to be run on an Raspberry Pi plugged into small powered speakers and placed near your bed, but can easily
be run on any machine that has Python & Pygame and can produce audio.

It is licensed under the Apache 2.0 License.

Use
---

It is built using Python and the pygame mixer module.

Raspberry Pi's already have pygame loaded and ready to go, just checkout this repository with git and go.

For OS X, see: `Homebrew pygame install instructions`_.

.. _Homebrew pygame install instructions: https://bitbucket.org/pygame/pygame/issues/82/homebrew-on-leopard-fails-to-install#comment-627494

To run slumber::

    python -m slumber.cli -s sounds

See the output of ``--help`` for all options.


Raspberry Pi Build
------------------

A `Raspberry Pi 1 model A+`_ was used along with a `3W+3W 5V Amp`_ and a 4 Ohm 3W speaker to build a small portable
sleep aid.

Slumber is set to start on boot up right now, in the future I'll add a button.

.. _Raspberry Pi 1 model A+: https://www.raspberrypi.org/products/model-a-plus/
.. _3W+3W 5V Amp: http://www.amazon.com/gp/product/B00C4N410G

TODO: Write more here

Sounds
------

All sound files are from freesound.org and are licensed under a Creative Commons By Attribution license.

They have been converted from their original formats to 16-bit, 44100kHz, 2-channel wav files and have been passed
through a "normalize" filter to -1dB in Audacity.

We pre-convert the sounds to save processor time when playing back.  If we're going to play the same
sound over and over there's no reason to waste cycles decoding anything.

Sounds Used
~~~~~~~~~~~

* `sounds/0/165342__corsica-s__above-chocolate-falls_SLUMBER.wav`_ by http://freesound.org/people/Corsica_S/
.. _sounds/0/165342__corsica-s__above-chocolate-falls_SLUMBER.wav: http://freesound.org/people/Corsica_S/sounds/165342/
* `sounds/0/174763__corsica-s__pacific-ocean_SLUMBER.wav`_ by http://freesound.org/people/Corsica_S/
.. _sounds/0/174763__corsica-s__pacific-ocean_SLUMBER.wav: http://freesound.org/people/Corsica_S/sounds/174763/
* `sounds/0/49634__corsica-s__national-water-10_SLUMBER.wav`_ by http://freesound.org/people/Corsica_S/
.. _sounds/0/49634__corsica-s__national-water-10_SLUMBER.wav: http://freesound.org/people/Corsica_S/sounds/49634/
* `sounds/0/82058__benboncan__lapping-waves_SLUMBER.wav`_ by http://freesound.org/people/Benboncan/
.. _sounds/0/82058__benboncan__lapping-waves_SLUMBER.wav: http://freesound.org/people/Benboncan/sounds/82058/
* `sounds/1/104952_Glaneur_de_sons__wind_SLUMBER.wav`_ by http://freesound.org/people/Glaneur%20de%20sons/
.. _sounds/1/104952_Glaneur_de_sons__wind_SLUMBER.wav: http://freesound.org/people/Glaneur%20de%20sons/sounds/104952/
* `sounds/1/105360__strangely-gnarled__windroar-constant-1m12s_SLUMBER.wav`_ by http://freesound.org/people/strangely_gnarled/
.. _sounds/1/105360__strangely-gnarled__windroar-constant-1m12s_SLUMBER.wav: http://freesound.org/people/strangely_gnarled/sounds/105360/
* `sounds/1/177479__unfa__slowly-raining-loop_SLUMBER.wav`_ by http://freesound.org/people/unfa/
.. _sounds/1/177479__unfa__slowly-raining-loop_SLUMBER.wav: http://freesound.org/people/unfa/sounds/177479/
* `sounds/1/93683__sithjawa__rainfrog-loop-1_SLUMBER.wav`_ by http://freesound.org/people/sithjawa/
.. _sounds/1/93683__sithjawa__rainfrog-loop-1_SLUMBER.wav: http://freesound.org/people/sithjawa/sounds/93683/

.. vim: set tw=100 wrap spell :
