Slumber
=======

This is a white noise machine written in Python.


Use
---

It is built using the pygame mixer.

For OS X, see: `Homebrew pygame install instructions`_.

.. _Homebrew pygame install instructions: https://bitbucket.org/pygame/pygame/issues/82/homebrew-on-leopard-fails-to-install#comment-627494



Sounds
------

All sound files are from freesound.org and are licensed under a Creative Commons By Attribution license.

They have been converted from their original formats to 16-bit, 44100kHz, 2-channel wav files and have been passed
through a "normalize" filter to -1dB in Audacity.

We pre-convert the sounds to save processor time when playing back.  If we're going to play the same
sound over and over there's no reason to waste cycles decoding anything.

 * sounds/0/165342__corsica-s__above-chocolate-falls_SLUMBER.wav
   Original link: http://freesound.org/people/Corsica_S/sounds/165342/
   By http://freesound.org/people/Corsica_S/

 * sounds/0/174763__corsica-s__pacific-ocean_SLUMBER.wav
   Original link: http://freesound.org/people/Corsica_S/sounds/174763/
   By http://freesound.org/people/Corsica_S/

 * sounds/0/24511__glaneur-de-sons__riviere-river_SLUMBER.wav
   Original link: http://freesound.org/people/Glaneur%20de%20sons/sounds/24511/
   By http://freesound.org/people/Glaneur%20de%20sons/

 * sounds/0/82058__benboncan__lapping-waves_SLUMBER.wav
   Original link: http://freesound.org/people/Benboncan/sounds/82058/
   By http://freesound.org/people/Benboncan/

 * sounds/1/177479__unfa__slowly-raining-loop_SLUMBER.wav
   Original link: http://freesound.org/people/unfa/sounds/177479/
   By http://freesound.org/people/unfa/

 * sounds/2/104952_Glaneur_de_sons__wind_SLUMBER.wav
   Original link: http://freesound.org/people/Glaneur%20de%20sons/sounds/104952/
   By http://freesound.org/people/Glaneur%20de%20sons/

.. vim: set tw=100 wrap spell :
