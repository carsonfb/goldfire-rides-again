"""
    This program is a new version of the old PC demo GoldFire by Carson F. Ball.
    The original was written in x86 Assembly and has been ported mostly as an
    exercise to see if it could run at a decent speed in Python.  The original
    was limited to the scanline refresh and had a hard-limit of 60 FPS because
    of this; without the limitation, it was faster than that on a Pentium I 60MHz
    but I don't remember how much faster.  The current version (running at the
    same resolution) is ~80 FPS on modern hardware.  However, not all of the
    features have been implemented yet.

    See the README.md for more details and licensing information.
"""

import os
from time import perf_counter
import glob
import random
import numpy as np
import OpenGL.GL as gl
import OpenGL.GLUT as glut

class Fire:
    """
        This class creates a modified version of the demo GoldFire from the 1990s.  The fire
        routine calculations are slightly adjusted from the original and one of the features of the
        original version has not been implemented yet and may never be.

        The palette file format from the original is supported and most of the palettes from the
        original are included.  A couple of the palettes that I was never quite happy with were
        excluded.  In general, I either never got the color distribution quite right, or they were
        very similar to other palettes.  These are binary files consisting of 256 triplets of red,
        green, and blue values.

        Speed Notes (see the git history for more details on some of the changes):

        * In testing x << 2 was slightly faster than x * 4.  This doesn't matter very much on each
          frame, but adds up over time.  This likely varies by system architecture, but has been
          true on x86 architecture for a long time.

        * In testing, x + x is faster than x << 1, but x + x + x + x is slower than x << 2.
          Though list[x] + list[x] is slower than list[x] << 1.  This is likely due to accessing
          the indexed value twice in the first case, though that's just a guess.

        * Making local copies of frequently used variables rather than looking them up from self
          each time had an appreciable impact on speed.

        * Only processing lines that actually change before the fire tapers off had a large impact
          on speed (first_row).

        * Skipping the processing of any pixel that would be black also had a large impact on
          speed (black_pixels).

        * Continue is time-intensive.  Refactoring the code to remove it increased the frame-rate.

        * Partially caching the pixel calculations improved the speed by about 70%.  This
          surprised me as I would not have expected a dictionary lookup to be that much faster
          than an addition and a bit shift.  This could not be fully cached due to memory
          constraints and time constraints of building the cache.

        * Changing from RGBA to RGB yielded a speed increase with no loss since the alpha channel
          was not being used.  I assume that nothing about RGB is inherently faster than RGBA and
          that the entire speed increase was due to operating on 25% less data.

        * Changing the cache to a list of lists from a dict of dicts increases the speed by about
          20%.  It seems that, from what I've read, under the hood using a list saves a lookup over
          using a dict (techincally two lookups since it is a list of lists).  This speed up was
          counter-intuitive since lists are supposed to be O(n) and dicts are supposed to be O(1).
          However, if the list was larger, dicts may be faster.

        * Assigning multiple values in one statement yields a slight speed improvement.  It also
          reduces the number of statements which makes pylint happy.
    """

    def __init__(self):
        # Setup the starting time and frames for determing the fps.  The time
        # will be initialized later.
        self.fps = {
            'start_time': None,
            'frames': 0
        }

        # Initialize the window handle, dimensions, first row of fire, and size.
        self.window = {
            'handle': None,
            'w': 320, # 384,
            'h': 200, # 240,
            'first_row': 145,
            'size': 0
        }

        self.window['size'] = self.window['w'] * self.window['h']

        self.start_from = self.window['first_row'] * self.window['w']
        self.end_from = (self.window['h'] - 1) * self.window['w'] + self.window['w']

        # Setup the palette index, grey flag, the changed flag, and the number of palettes.
        self.palette_flags = {
            'index': 0,
            'grey': False,
            'fire_grey': False,
            'words_grey': False,
            'changed': True,
            'total': 0,
        }

        # Initialize the palettes.
        self.palettes, self.greys, self.black_pixels = read_palettes()
        self.palette_flags['total'] = len(self.palettes)

        # Store the logo information.
        self.logo = self.pre_process_logo()

        # Copy the default palette into the current palette.
        self.current_words_palette = self.palettes[self.palette_flags['index']].copy()
        self.current_fire_palette = self.palettes[self.palette_flags['index']].copy()

        # Initialize the back buffer. The back buffer only has
        # the palette lookup value, so it is only a 1/4 of the size.
        self.back_buf = [0x00] * self.window['size']

        self.cached = create_cache()

        self.words_buf = None

        self.display_word = False

    def make_frame(self):
        """
            This method creates the bitmap for the frame.  The algorithm is below:

            For the normal cases, average the value of the pixel directly below the
            current one, the pixel below and to the left, below and to the right, and
            two below.

            For the left-most pixels, instead of using the one to the left, wrap to
            the right.

            For the right-most pixels, instead of using the one to the right, wrap to
            the left.

            For the bottom two rows, pull pixels from the randomly generated data.

            Since no pixel is changed until all calculations that use it have completed,
            we do not need another buffer.

            This is a slight departure from the method used in the original GoldFire.
        """

        # Make local copies to avoid the overhead of lookups.
        cached, back_buf, window_w = self.cached, self.back_buf, self.window['w']

        # Precalculate values.
        win_w_min, from_index = window_w - 1, self.window['first_row'] * window_w
        to_index = from_index - window_w

        # Generate two rows of random data.
        random_bytes = generate_data(window_w)

        # The fire cuts out on its own due to the algorithm.  Only the bottom 50 or so
        # rows need to be calculated.
        for _ in range(self.window['first_row'], self.window['h'] - 2):
            # The last two rows are calculated separately since they
            # have special processing due to the random data.

            # The next row is pre-calculated to save processing.
            from_index += window_w
            to_index += window_w
            col_index = from_index

            for col in range(1, win_w_min):
                # Process all columns except for the first and last column.  Those are
                # special cases.

                col_index += 1

                back_buf[to_index + col] = \
                    cached[back_buf[col_index - 1]][back_buf[col_index + 1]] + \
                        cached[back_buf[col_index]][back_buf[col_index + window_w]]

            # Pre-calculate a frequently used value.
            from_window = from_index + window_w

            # Process the first column.
            back_buf[to_index] = \
                cached[back_buf[from_index - 1]][back_buf[from_index + 1]] + \
                    cached[back_buf[from_index]][back_buf[from_window]]

            # Process the last column.
            back_buf[from_index - 1] = \
                cached[back_buf[from_window - 2]][back_buf[from_index]] + \
                    cached[back_buf[from_window - 1]][back_buf[from_window + win_w_min]]

        # The next row is pre-calculated to save processing.
        col_index = from_index = (self.window['h'] - 1) * window_w
        to_index = from_index - window_w

        for col in range(1, win_w_min):
            # The pixel directly below the current one is pre-calculated
            # to save processing.
            col_index += 1

            back_buf[from_index - window_w + col] = \
                cached[back_buf[col_index - 1]][back_buf[col_index + 1]] + \
                    cached[back_buf[col_index]][random_bytes[col]]

        # Process the first column.
        back_buf[to_index] = \
            cached[back_buf[from_index + win_w_min]][back_buf[from_index + 1]] + \
                cached[back_buf[from_index]][random_bytes[0]]

        # Process the last column.
        back_buf[from_index - 1] = \
            cached[back_buf[from_index + window_w - 2]][back_buf[from_index]] + \
                cached[back_buf[from_index + win_w_min]][random_bytes[win_w_min]]

        for col in range(1, win_w_min):
            back_buf[to_index + col] = \
                cached[random_bytes[col - 1]][random_bytes[col + 1]] + \
                    cached[random_bytes[col]][random_bytes[window_w + col]]

        # Process the first column.
        back_buf[to_index] = \
            cached[random_bytes[win_w_min]][random_bytes[window_w + 1]] + \
                cached[random_bytes[0]][random_bytes[window_w]]

        # Process the last column.
        back_buf[from_index - 1] = \
            cached[random_bytes[window_w - 2]][random_bytes[window_w]] + \
                cached[random_bytes[win_w_min]][random_bytes[(window_w + window_w) - 1]]

        # Make local copies to avoid the overhead of lookups.
        cur_fire_palette, black_pixels \
            = self.current_fire_palette, self.black_pixels[self.palette_flags['index']]

        start_from, end_from, first_row \
            = self.start_from, \
            self.end_from, \
            (self.window['h'] - self.window['first_row']) * window_w

        logo = self.logo['logo']

        if self.display_word:
            # The user chose to display a word in the fire, process it.
            start_col = self.logo['start_col']
            end_col = start_col + self.logo['logo_cols']

            pal_index = 0

            for index in range(self.logo['fire_start'], self.logo['fire_end']):
                calc_index = (index * window_w)

                # Copy an entire row of the logo at a time.
                back_buf[calc_index + start_col:calc_index + end_col] \
                    = logo[pal_index:pal_index + end_col - start_col]

                pal_index += end_col - start_col

            self.display_word = False

        # Update the instance's back buffer and clear the display buffer by setting it to black.
        self.back_buf, display_buf = back_buf, bytearray(self.window['size'] * 3)

        # Calculate the start and end columns of the logo.
        start_col = self.logo['start_col'] * 3
        end_col = start_col + self.logo['logo_cols'] * 3

        if self.palette_flags['changed']:
            # The palette changed, update the text area.
            cur_words_palette = self.current_words_palette

            self.words_buf = bytearray(len(logo) * 3)

            pal_index = words_index = 0

            for index in range(self.logo['start_row'], self.logo['end_row']):
                calc_index = (index * window_w * 3)

                for col in range(start_col, end_col, 3):
                    # Do not process black pixels as they won't be seen.
                    if logo[pal_index] not in black_pixels:
                        # Precalculate values used more than once.
                        calc_col, calc_pal = calc_index + col, logo[pal_index] * 3

                        # Update the display buffer and the words cache.
                        display_buf[calc_col:calc_col + 3] \
                            = self.words_buf[words_index:words_index + 3] \
                            = cur_words_palette[calc_pal:calc_pal + 3]

                    words_index += 3
                    pal_index += 1

            self.palette_flags['changed'] = False
        else:
            # The palette did not change so use the cached logo.

            buf_start = self.logo['start_row'] * window_w * 3 + start_col
            words_start = 0
            logo_cols = self.logo['logo_cols'] * 3

            for index in range(0, 20):
                # Copy each row of the logo to the display buffer.
                display_buf[buf_start:buf_start + logo_cols] \
                    = self.words_buf[words_start:words_start + logo_cols]

                buf_start += self.window['w'] * 3
                words_start += logo_cols

        for index, value in enumerate(back_buf[start_from:end_from + 1]):
            # Update only the fire area.  Only perform half of the loops since the top
            # and bottom do not need to be looked up and calculated separately.
            if value not in black_pixels:
                # If the color is black, it does not need to be looked up and set.

                # Pre-calculate indexing variables.
                quad, idx, idx2 = value * 3, (first_row - index) * 3, (start_from + index) * 3

                # Copy the RGB values from the palette to the display buffer.
                display_buf[idx:idx + 3] \
                    = display_buf[idx2:idx2 + 3] \
                    = cur_fire_palette[quad:quad + 3]

        return display_buf

    def display_frame(self):
        """
            This method is the callback for the OpenGL window and displays
            an updated frame of the fire.
        """

        # Generate the new frame.
        bitmap = self.make_frame()

        # Display the new frame.
        gl.glDrawPixels(self.window['w'], self.window['h'], gl.GL_RGB, gl.GL_UNSIGNED_BYTE, bitmap)
        glut.glutSwapBuffers()

        # Increment the number of frames for the purpose of calculating the FPS.
        self.fps['frames'] += 1

    def set_palettes(self):
        """
            This method is sets up the current palettes based on the greyscale flags.
        """

        if self.palette_flags['grey']:
            # Set both palettes to grey.
            self.current_words_palette = self.greys[self.palette_flags['index']].copy()
            self.current_fire_palette = self.greys[self.palette_flags['index']].copy()
        elif self.palette_flags['words_grey']:
            # Set the word palette to grey and the fire palette to color.
            self.current_words_palette = self.greys[self.palette_flags['index']].copy()
            self.current_fire_palette = self.palettes[self.palette_flags['index']].copy()
        elif self.palette_flags['fire_grey']:
            # Set the fire palette to grey and the word palette to color.
            self.current_words_palette = self.palettes[self.palette_flags['index']].copy()
            self.current_fire_palette = self.greys[self.palette_flags['index']].copy()
        else:
            # Set both palettes to color.
            self.current_words_palette = self.palettes[self.palette_flags['index']].copy()
            self.current_fire_palette = self.palettes[self.palette_flags['index']].copy()

    def pre_process_logo(self):
        """
            This method creates the logo structure avoiding the need to recalculate the values
            each time through the main loop.
        """

        logo = {
            'logo': None,
            'start_row': 0,
            'end_row': 0,
            'start_col': 0,
            'fire_start': 0,
            'fire_end': 0
        }

        # Read the logo from the file.
        logo['logo'] = read_logo()

        # There are 20 rows so divide the total bytes by 20 to get the number of columns.  The
        # divisor could be stored in a variable instead of being hard-coded, but that seemed
        # unnecessary unless scaling is allowed at some point in the future.
        logo_cols = len(logo['logo']) // 20

        # Set the first column such that the text will be centered.
        logo['start_col'] = (self.window['w'] - logo_cols) // 2

        start_row = self.window['h'] - self.window['first_row']
        end_row = self.window['first_row']
        diff = (end_row - start_row)

        diff = ((diff - 20) >> 1)
        start_row += diff
        end_row = start_row + 20

        logo['logo_cols'] = logo_cols
        logo['start_row'] = start_row
        logo['end_row'] = end_row
        logo['fire_start'] = start_row + 87
        logo['fire_end'] = end_row + 87

        return logo

    def kb_input(self, key, _x_pos, _y_pos):
        """ This method handles keyboard input from the user. """

        if key in [b'q', b'Q', b'\x1B']:
            # If the user pressed q or esc, terminate the program.

            # Get the current time and caculate the elapsed time and FPS.
            stop_time = perf_counter()
            elapsed_time = stop_time - self.fps['start_time']
            fps = self.fps['frames'] / elapsed_time

            # Close the OpenGL window.
            glut.glutDestroyWindow(self.window['handle'])

            # Display the statistics to the user.
            print(f'Frames: {self.fps["frames"]}')
            print(f'Seconds: {elapsed_time}')
            print(f'FPS: {fps}')
        elif key in [b'p', b'P']:
            # If the user pressed p, cycle through the palettes.
            self.palette_flags['changed'] = True

            if self.palette_flags['index'] == self.palette_flags['total'] - 1:
                # If the last palette is already in use, go back to the default palette.
                self.palette_flags['index'] = 0
            else:
                # Go to the next palette.
                self.palette_flags['index'] += 1

            self.set_palettes()
        elif key in ([b'r', b'R']):
            # If the user pressed r, select a random palette.
            self.palette_flags['index'] = random.randint(0, self.palette_flags['total'] - 1)
            self.palette_flags['changed'] = True

            self.set_palettes()
        elif key in ([b'g', b'G']):
            # If the user pressed g, change the palette to greyscale.
            self.palette_flags['grey'] = True
            self.palette_flags['fire_grey'] = True
            self.palette_flags['words_grey'] = True
            self.palette_flags['changed'] = True

            self.current_words_palette = self.greys[self.palette_flags['index']]
            self.current_fire_palette = self.greys[self.palette_flags['index']]
        elif key in ([b'c', b'C']):
            # If the user pressed c, change the palette to color.
            self.palette_flags['grey'] = False
            self.palette_flags['fire_grey'] = False
            self.palette_flags['words_grey'] = False
            self.palette_flags['changed'] = True

            self.current_words_palette = self.palettes[self.palette_flags['index']]
            self.current_fire_palette = self.palettes[self.palette_flags['index']]
        elif key in ([b'f', b'F']):
            # If the user presses f, change the fire to greyscale.
            self.palette_flags['fire_grey'] = True
            self.palette_flags['changed'] = True

            self.current_fire_palette = self.greys[self.palette_flags['index']]
        elif key in ([b'w', b'W']):
            # If the user presses w, change the fire to greyscale.
            self.palette_flags['words_grey'] = True
            self.palette_flags['changed'] = True

            self.current_words_palette = self.greys[self.palette_flags['index']]
        elif key in ([b'a', b'A']):
            # If the user presses a, display "GoldFire" in the fire area and process it.  This is
            # command a becuase, in the original version, it displayed "ABRAXAS".
            self.display_word = True

    def main(self):
        """
            This method is the main entry point for the class and sets up
            the OpenGL display and keyboard as well as initializes the
            start time for the FPS calculation.
        """

        # Initialize OpenGL
        glut.glutInit()

        # Get the width and height of the monitor and the center for the window.
        screen_w = glut.glutGet(glut.GLUT_SCREEN_WIDTH)
        screen_h = glut.glutGet(glut.GLUT_SCREEN_HEIGHT)
        center_x = int((screen_w - self.window['w']) >> 1)
        center_y = int((screen_h - self.window['h']) >> 1)

        # Create the OpenGL window and display it.
        glut.glutInitDisplayMode(glut.GLUT_RGB)
        glut.glutInitWindowSize(self.window['w'], self.window['h'])
        glut.glutInitWindowPosition(center_x, center_y)
        self.window['handle'] = glut.glutCreateWindow('GoldFire Rides Again'.encode('ascii'))

        # Setup the callbacks for OpenGL.
        glut.glutDisplayFunc(self.display_frame)
        glut.glutIdleFunc(self.display_frame)
        glut.glutKeyboardFunc(self.kb_input)

        # Flip the image upside-right.
        gl.glLoadIdentity()
        gl.glRasterPos2f(-1, 1)
        gl.glPixelZoom(1, -1)

        # Initialize the timer for calculating the FPS.
        self.fps['start_time'] = perf_counter()

        # Start the main program loop.
        glut.glutMainLoop()

def read_palettes():
    """
        This function reads the palettes from the palettes folder on disk.  Users can supply
        their own palettes and they will be automatically loaded.  The default palette will
        be loaded as the first in the list.
    """

    # Initialize the palette structure and leave a placeholder for the default palette.
    palettes = []
    palettes.append([])

    greys = []
    greys.append([])

    black_pixels = []
    black_pixels.append([])

    # Find all of the palette files in the palettes folder.
    files = glob.glob(r'palettes\*.bin')

    for file in files:
        if os.path.getsize(file) != 768:
            # Skip the palette file if it is the wrong size.
            continue

        if 'default.bin' in file:
            # Set the default palette to the first palette entry.
            palettes[0], greys[0], black_pixels[0] = make_palette(file)
        else:
            # Appened palettes other than the default to the list.
            pal, grey, black = make_palette(file)

            palettes.append(pal)
            greys.append(grey)
            black_pixels.append(black)

    return palettes, greys, black_pixels

def read_logo():
    """
        This function reads in the GoldFire logo bitmap that was created with
        create_logo.py.
    """

    with open('data/goldfire.bin', 'rb') as gf_file:
        goldfire = gf_file.read()

    return goldfire

def make_palette(file):
    """ This function loads a palette file and appends the alpha value. """

    # Initialize the palette structure.
    palette = []
    greys = []
    black_pixels = set()

    with open(file, 'rb') as palette_fh:
        # Read in all of the color entries.
        for index in range(0, 256):
            # Read the red, green, and blue values for the color.
            red, green, blue = palette_fh.read(3)

            # The colors were extremely dark and needed to be scaled.  I'm not sure why though as
            # the palette files are the same ones that the original version from the 1990s was
            # using.  This is very close to the original colors after the faked "gamma" correction.
            red *= 5
            green *= 5
            blue *= 5

            # Prevent overflows.
            red = min(red, 255)
            green = min(green, 255)
            blue = min(blue, 255)

            # Calculate the greyscale values.  These should have the same luminosity as the color
            # vales.
            total = red + green + blue
            grey = total // 3

            if not total:
                # If the color is black, add it to the list.
                black_pixels.add(index)

            # Store the red, green, and blue values.
            palette.extend([red, green, blue])
            greys.extend([grey, grey, grey])

    return palette, greys, black_pixels

def create_cache():
    """
        This function sets up a partial lookup table for the pixel calculations.
        The full 256*256*256*256 table cannot be constructed due to memory
        constraints as well as it taking much too long though the latter issue
        could potentially be addressed by using a different data structure such
        as a numpy array.  Instead the first two values of the original calculation
        are added and the last two are added and then these are used to lookup the
        pixel color.

        I am surprised that this yielded a speed increase since most of the math
        still has to happen (requires two additions instead of four additions and a
        bit shift).  I suppose a constant-time lookup is faster than an addition
        and a bit shift.  Still, I wouldn't have expected a 70% increase in speed.

        There is a slight loss of fidelity as int((a + b) // 4) + int((c + d) // 4)
        could be a slightly lower value than int((a + b + c + d) // 4).  Ultimately,
        due to how the palettes are setup, this likely will not change the color of
        the pixel or, if it does, it will only change very slightly.  In practice, I
        did not notice any differences.
    """

    cached = []

    for index in range(256):
        cached.append([])

        for index2 in range(256):
            cached[index].append((index + index2) >> 2)

    return cached

def generate_data(window_w):
    """
        This function generates two rows of values at either the min or halfway value
        of the palette. These are used in the averaging algorithm.
    """

    return np.random.choice([0, 128], size=window_w + window_w, p=[0.43, 0.57])

if __name__ == '__main__':
    FIRE = Fire()
    FIRE.main()
