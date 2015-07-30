Slumber
=======

Sleep better.

This is a white noise based sleep aid that uses an accelerometer to influence the volume and type of
white noise being played.

This was built in July of 2015 following the arrival of a new baby.


Theory of operation
-------------------

    "Williamson [59] investigated the influence of ocean sounds (white noise) on the night sleep
    pattern of postoperative coronary artery bypass graft patients after being transferred from an
    ICU. The group receiving ocean sounds reported higher scores in sleep depth, awakening, return
    to sleep, quality of sleep, and total sleep scores, indicating better sleep than the controlled
    group. The study by Stanchina and colleagues [60] suggested that white noise increased arousal
    thresholds in healthy individuals exposed to recorded ICU noise. The change in sound from
    baseline to peak, rather than the peak sound level, determined whether an arousal occurred. From
    Table ​Table33 it can be seen that sound masking has the most significant effect in
    promoting ICU patients' sleep, producing an improvement of 42.7%."

    http://www.ncbi.nlm.nih.gov/pmc/articles/PMC2689451/

Research has shown that white noise allows for people to reach deeper, more restful sleep.

Sleep happens in patterns.

While in deep sleep the person will move less.  As the cycle ends more movement occurs.  The
accelerometer will detect this movement and respond by layering more sounds and increasing the
overall volume.


Implementation notes
--------------------

Sounds will be grouped into different categories.  Each category will have an "intensity" value
associated with it.  As more movement occurs we will start playing a random sound from the next
intensity category.

Sounds will have long (1/4 of their length) fade in and fade out effects applied.


Use
---

It is built using the pygame mixer.

For OS X, see: `Homebrew pygame install instructions`_.

.. _Homebrew pygame install instructions: https://bitbucket.org/pygame/pygame/issues/82/homebrew-on-leopard-fails-to-install#comment-627494



Sounds
------

All sound files are Creative Commons By Attribution licenses.

They have been converted from their original formats to 16-bit, 44100kHz, 2-channel wav files
using the following command::

    ffmpeg -i original_input_file.mp3 -ac 2 -ar 44100 output.wav

We pre-convert the sounds to save processor time when playing back.  If we're going to play the same
sound over and over there's no reason to waste cycles decoding anything.

* wind.wav - http://www.freesound.org/people/Glaneur%20de%20sons/sounds/104952/
* thunderstorm-long.wav - http://www.freesound.org/people/Arctura/sounds/39828/


.. vim: set tw=100 wrap spell :
