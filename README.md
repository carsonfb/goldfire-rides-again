GoldFire Redux
==============

Description
-----------
GoldFire was a demo created by me (ABRAXAS of the programming group ΣNDVZTRÆ⅃ MµZ1K) in the mid to late 1990s (source files indicate most versions were created during 1995 and 1996 with a final release in 1998).  This is a Python port of the original x86 Assembler code.

See the notes section if you have problems running this on Windows.

Features
--------
- The ability to import palettes (P).  All of the palettes from the original version are included:
  * default.bin: This is the gold palette from which GoldFire gets it's name.  This file is required.
  * bluegray1.bin: This is a palette swap of default.bin but with blue-gray (same intensity, different hue).
  * pal.bin: This is the original system palette and looks a bit like an old school plasma effect.
  * psydel1.bin: This is a psychedlic palette, though pal.bin seems trippier to me.
  * purple.bin: This is a palette swap of default.bin but with purple (same intensity, different hue).
  * seagrn1.bin: This is a palette swap of default.bin but with green (same intensity, different hue).
- The ability to import your own palettes.  Palette files are binary files consisting of (in order) red, green, and blue triplets. Any 786 byte file dropped into the palettes folder with the extension bin will be loaded but, unless you want odd results, I'd recommend creating actual palette files.  This can be done relatively easily by making a copy of one of the palette swap files and changing the red, green, and blue values but keeping the sums of the three in each triplet the same as they were to begin with.  For example if the values were 128, 63, and 44, then 188, 23, 24 would be appropriate.
- The ability to randomly change the palette from the ones that have been loaded (R).
- The ability to switch between color (C) and greyscale (G).
- The ability to change only the words to grey (W).
- The ability to change only the fire to grey (F).
- The ability to display "GoldFire" in the fire and have it flame out (A).
- The ability to quit (Q) (ESC).

Differences from the original
-----------------------------
Not all of the commands of the original are supported yet.  Among those are:
- Changing the aspect ratio (H)

Other differences are:
- Only the program name ("GoldFire") is displayed in the text area.  In the original, it displayed "GoldFire by: ABRAXAS of ΣNDVZTRÆ⅃ MµZ1K".
- The fire area might be a slightly different height.  I'm not sure what it was on the original and haven't bothered to look it up.  I just went with what looked right in the new version which is what I did in the original as well.
- The frames / second are displayed when the user quits instead of the credits.
- In the original version, pressing "a" caused "ABRAXAS" to appear in the fire.  In the new version "GoldFire" appears in the fire.  ABRAXAS was my handle in the local demo scene.
- The fire algorithm is slightly different
- This version is more resource-intensive since it is written in Python and OpenGL rather than x86 Assembler and direct hardware calls.  Although, the user-facing speed (e.g. frames per second) is actually higher.
- This version is released under a Creative Commons license (see the License section below).  The original was closed source.
- The random pixels at the top (and bottom) are no longer displayed.  These are now only on the back-buffer.  This makes the display look a bit cleaner.
- The logo is read from a pre-processed binary file instead of being created dynamically.

[![Original Screenshot](https://carson.ballweb.org/images/goldfire.png)](https://carson.ballweb.org/images/goldfire.png)<br />
*Original version*

[![New Screenshot](https://carson.ballweb.org/images/goldfire_new.png)](https://carson.ballweb.org/images/goldfire_new.png)<br />
*New version*

Notes
-----
On Windows, you may have to jump through a small hoop in order to get GoldFire to run.  This [YouTube video](https://www.youtube.com/watch?v=a4NVQC_2S2U) gives detailed instructions and is what I followed.

This has been tested with Python 3.10.0 and 3.8.10 and runs 20% faster on 3.8.10.  It may run on other 3.x versions as well, but 3.8.10 is the recommended version.

Credits
-------
© 2023 [Carson F. Ball](<mailto://carson@ballweb.org>)

Creator of the original GoldFire: Carson F. Ball

Creator of GoldFire Redux: Carson F. Ball

Designer of the palettes (except pal.bin which is the system palette): Carson F. Ball

Testers of the original GoldFire: Chris Lehman and Dan Lehman

Donations
---------
If you like this project and want to see more projects from me, please contribute if you are able.

[![PayPal donation button](https://img.shields.io/badge/PayPal-00457C?style=for-the-badge&logo=paypal&logoColor=white)](https://www.paypal.com/cgi-bin/webscr?cmd=_s-xclick&hosted_button_id=CT5XNBHGD5TEN)

[![BitCoin Wallet](https://img.shields.io/badge/Bitcoin-000000?style=for-the-badge&logo=bitcoin&logoColor=white)](https://img.shields.io/badge/Bitcoin-000000?style=for-the-badge&logo=bitcoin&logoColor=white) 3QzgUdXzbLY7oy15XeMJ4W37cfBJDeKj6A
