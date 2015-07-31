#!/bin/bash
#
# Simple little script to build the sound attributions for the README file
#

for sound in sounds/*/*.wav; do
	id=$(echo $sound | awk -F_ '{print $1}' | awk -F/ '{print $NF}')
	freesound_a_tag=$(curl -s "http://www.freesound.org/search/?q=$id" | grep 'class="title"' | head -n1)
	freesound_link=$(echo $freesound_a_tag | xmllint --xpath "//a/@href" - | awk -F'"' '{print "http://freesound.org"$2}')
	freesound_author=$(curl -s $freesound_link | grep 'id="sound_author"' | xmllint --xpath '//div/a' - | awk -F'"' '{print "http://freesound.org"$2}')

	echo " * $sound"
	echo "   Original link: $freesound_link"
	echo "   By $freesound_author"
	echo ""
done
