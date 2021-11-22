GoldFire Redux
==============

Description
-----------
GoldFire was a demo created by Carson F. Ball (ABRAXAS of the programming group ΣNDVZTRÆ⅃ MµZ1K) in the mid to late 1990s (source files indicate most versions were created during 1995 and 1996 with a final release in 1998).  This is a Python port of the original x86 Assembler code.

See the notes section if you have problems running this on Windows.

Features
--------
- The ability to import palettes (P).  A number of palettes from the original version are included:
* default.bin: This is the gold palette from which GoldFire gets it's name.  This file is required.
* bluegray1.bin: This is a palette swap of default.bin but with blue-gray (same intensity, different hue).
* pal.bin: This is the original system palette and looks a bit like an old school plasma effect.
* psydel1.bin: This is a psychedlic palette, though pal.bin seems trippier to me.
* purple.bin: This is a palette swap of default.bin but with purple (same intensity, different hue).
* seagrn1.bin: This is a palette swap of default.bin but with green (same intensity, different hue).
- The ability to import your own palettes.  Palette files are binary files consisting of (in order) red, green, and blue triplets. Any 786 byte file dropped into the palettes folder with the extension bin will be loaded but, unless you want odd results, I'd recommend creating actual palette files.  This can be done relatively easily by making a copy of one of the palette swap files and changing the red, green, and blue values but keeping the sums of the three in each triplet the same as they were to begin with.  For example if the values were 128, 63, and 44, then 188, 23, 24 would be appropriate.
- The ability to randomly change the palette from the ones that have been loaded (R).
- The ability to switch between color (C) and greyscale (G).
- The ability to quit (Q) (ESC).

Differences from the original
-----------------------------
Not all of the commands of the original are supported yet.  Among those are:
- Printing ABRAXAS in the fire and having it burn out (A)
- Changing only the words to grey (W)
- Changing only the fire to grey (F)
- Changing the aspect ratio (H)

Among other differences are:
- There are no words on the screen
- The frames / second are displayed when the user quits instead of the credits
- The fire algorithm is slightly different
- This version is slower since it is written in Python and OpenGL rather than x86 Assembler and direct hardware calls.  Although, the user-facing speed is actually higher.
- This version is released under a Creative Commons license (see the License section below)

Notes
-----
On Windows, you may have to jump through a small hoop in order to get GoldFire to run.  This YouTube video gives detailed instructions and is what I followed. _https://www.youtube.com/watch?v=a4NVQC_2S2U

Credits
-------
Creator of the original GoldFire: Carson F. Ball
Creator of GoldFire Redux: Carson F. Ball
Designer of the palettes (except pal.bin which is the system palette): Carson F. Ball
Testers of the original GoldFire: Chris Lehman and Dan Lehman

License
-------
Creative Commons CC BY-NC
.. _Summary: https://creativecommons.org/licenses/by-nc/4.0/
.. _Full license: https://creativecommons.org/licenses/by-nc/4.0/legalcode