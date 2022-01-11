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
import OpenGL.GL as gl
import OpenGL.GLUT as glut
import numpy as np

class Fire:
    """
        This class creates a modified version of the old demo GoldFire.  The
        fire routine calculations are slightly adjusted from the original, some
        of the features have not been implemented yet (may never be), and the
        original had fire at both the top and bottom of the screen.

        The palette file format from the original is supported and most of the
        palettes from the original are included.  These are binary files
        consisting of 256 triplets of red, green, and blue values.

        Speed Notes (see the git history for more details on some of the changes):

        * In testing x << 2 was slightly faster than x * 4.  This doesn't matter very
          much on each frame, but adds up over time.  This likely varies by system
          architecture, but has been true on x86 architecture for a long time.

        * In testing, x + x is faster than x << 1, but x + x + x + x is slower than
          x << 2.  Though list[x] + list[x] is slower than x << 1.

        * Making local copies of frequently used variables rather than looking them
          up from self each time had an appreciable impact on speed.

        * Only processing lines that actually change before the fire tapers off
          had a large impact on speed (first_row).

        * Skipping the processing of any pixel that would be black also had a
          large impact on speed (black_pixels).

        * Continue is time-intensive.  Refactoring the code to remove it increased
          the frame-rate.

        * Partially caching the pixel calculations improved the speed by about 70%.  This
          surprised me as I would not have expected a dictionary lookup to be that much
          faster than and addition and a bit shift.  This could not be fully cached due
          to memory constraints and time constraints of building the cache.

        * Changing from RGBA to RGB yielded a speed increase with no loss since the alpha
          channel was not being used.
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
           'w': 320, # 384
           'h': 200, # 240
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
            'changed': True,
            'total': 0,
        }

        # Initialize the palettes.
        self.palettes, self.greys, self.black_pixels = read_palettes()
        self.palette_flags['total'] = len(self.palettes)

        # Copy the default palette into the current palette.
        self.current_palette = self.palettes[self.palette_flags['index']].copy()

        # Initialize the back buffer. The back buffer only has
        # the palette lookup value, so it is only a 1/4 of the size.
        self.back_buf = [0x00] * self.window['size']

        self.cached = create_cache()

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
        back_buf = self.back_buf
        window_w = self.window['w']

        # Generate two rows of random data.
        random_bytes = generate_data(window_w)

        cached = self.cached

        # The fire cuts out on its own due to the algorithm.  Only the bottom 50 or so
        # rows need to be calculated.
        for row in range(self.window['first_row'], self.window['h'] - 2):
            # The last two rows are calculated separately since they
            # have special processing due to the random data.

            # The next row is pre-calculated to save processing.
            from_index = (row + 1) * window_w
            to_index = from_index - window_w

            for col in range(1, window_w - 1):
                # Process all columns except for the first and last column.  Those are
                # special cases.

                # The pixel directly below the current one is pre-calculated
                # to save processing.
                col_index = from_index + col

                back_buf[to_index + col] = \
                    cached[back_buf[col_index - 1]][back_buf[col_index + 1]] + \
                        cached[back_buf[col_index]] [back_buf[col_index + window_w]]

            # Process the first column.
            back_buf[to_index] = \
                cached[back_buf[from_index - 1]][back_buf[from_index + 1]] + \
                    cached[back_buf[from_index]][back_buf[from_index + window_w]]

            # Process the last column.
            back_buf[from_index - 1] = \
                cached[back_buf[from_index + window_w - 2]][back_buf[from_index]] + \
                    cached[back_buf[from_index + window_w - 1]][back_buf[from_index + window_w + window_w - 1]]

        # The next row is pre-calculated to save processing.
        from_index = (self.window['h'] - 1) * window_w
        to_index = from_index - window_w

        for col in range(1, window_w - 1):
            # The pixel directly below the current one is pre-calculated
            # to save processing.
            col_index = from_index + col

            back_buf[from_index - window_w + col] = \
                cached[back_buf[col_index - 1]][back_buf[col_index + 1]] + \
                    cached[back_buf[col_index]][random_bytes[col]]

        # Process the first column.
        back_buf[to_index] = \
            cached[back_buf[from_index + window_w - 1]][back_buf[from_index + 1]] + \
                cached[back_buf[from_index]][random_bytes[0]]

        # Process the last column.
        back_buf[from_index - 1] = \
            cached[back_buf[from_index + window_w - 2]][back_buf[from_index]] + \
                cached[back_buf[from_index + window_w - 1]][random_bytes[window_w - 1]]

        for col in range(1, window_w - 1):
            back_buf[to_index + col] = \
                cached[random_bytes[col - 1]][random_bytes[col + 1]] + \
                    cached[random_bytes[col]][random_bytes[window_w + col]]

        # Process the first column.
        back_buf[to_index] = \
            cached[random_bytes[window_w - 1]][random_bytes[window_w + 1]] + \
                cached[random_bytes[0]][random_bytes[window_w]]

        # Process the last column.
        back_buf[from_index - 1] = \
            cached[random_bytes[window_w - 2]][random_bytes[window_w]] + \
                cached[random_bytes[window_w - 1]][random_bytes[(window_w + window_w) - 1]]

        # Update the instance's back buffer.
        self.back_buf = back_buf

        # Make local copies to avoid the overhead of lookups.
        cur_palette = self.current_palette
        black_pixels = self.black_pixels[self.palette_flags['index']]
        start_from = self.start_from
        end_from = self.end_from
        first_row = self.window['h'] - start_from

        # Clear the display buffer by setting it to black.
        display_buf = [0x00] * (self.window['size'] * 3)

        if self.palette_flags['changed']:
            # The palette changed, update the text area.
            # TODO: This is a placeholder for now.
            pass

        for index, value in enumerate(back_buf[start_from:end_from]):
            # The palette did not change, do not update the text area.  Also, only
            # perform half of the loops since the top and bottom do not need to be
            # looked up and calculated separately.
            if value not in black_pixels:
                # If the color is black it does not need to be looked up and set.

                # Pre-calculate indexing variables.
                quad, idx, idx2 = value * 3, (first_row - index) * 3, (start_from + index) * 3

                # Copy the RGB values from the palette to the display buffer.
                display_buf[idx:idx + 2] = display_buf[idx2:idx2 + 2] = cur_palette[quad:quad + 2]

        return bytes(display_buf)

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
            print (f"Frames: {self.fps['frames']}")
            print (f"Seconds: {elapsed_time}")
            print (f"FPS: {fps}")
        elif key in [b"p", b"P"]:
            # If the user pressed p, cycle through the palettes.
            self.palette_flags['changed'] = True

            if self.palette_flags['index'] == self.palette_flags['total'] - 1:
                # If the last palette is already in use, go back to the default palette.
                self.palette_flags['index'] = 0
            else:
                # Go to the next palette.
                self.palette_flags['index'] += 1

            if self.palette_flags['grey']:
                self.current_palette = self.greys[self.palette_flags['index']].copy()
            else:
                self.current_palette = self.palettes[self.palette_flags['index']].copy()
        elif key in ([b"r", b"R"]):
            # If the user pressed r, select a random palette.
            self.palette_flags['index'] = random.randint(0, self.palette_flags['total'] - 1)
            self.palette_flags['changed'] = True

            if self.palette_flags['grey']:
                self.current_palette = self.greys[self.palette_flags['index']].copy()
            else:
                self.current_palette = self.palettes[self.palette_flags['index']].copy()
        elif key in ([b"g", b"G"]):
            # If the user pressed g, change the palette to greyscale.
            self.palette_flags['grey'] = True
            self.palette_flags['changed'] = True

            self.current_palette = self.greys[self.palette_flags['index']]
        elif key in ([b"c", b"C"]):
            # If the user pressed c, change the palette to color.
            self.palette_flags['grey'] = False
            self.palette_flags['changed'] = True

            self.current_palette = self.palettes[self.palette_flags['index']]

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
        self.window['handle'] = glut.glutCreateWindow("GoldFire Rides Again")

        # Setup the callbacks for OpenGL.
        glut.glutDisplayFunc(self.display_frame)
        glut.glutIdleFunc(self.display_frame)
        glut.glutKeyboardFunc(self.kb_input)

        # Flip the image upside-right.
        gl.glLoadIdentity()
        gl.glRasterPos2f(-1,1)
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
    files = glob.glob(r"palettes\*.bin")

    for file in files:
        if os.path.getsize(file) != 768:
            # Skip the palette file if it is the wrong size.
            continue

        if "default.bin" in file:
            # Set the default palette to the first palette entry.
            palettes[0], greys[0], black_pixels[0] = make_palette(file)
        else:
            # Appened palettes other than the default to the list.
            pal, grey, black = make_palette(file)

            palettes.append(pal)
            greys.append(grey)
            black_pixels.append(black)

    return palettes, greys, black_pixels

def make_palette(file):
    """ This function loads a palette file and appends the alpha value. """

    # Initialize the palette structure.
    palette = []
    greys = []
    black_pixels = set()

    with open(file, "rb") as palette_fh:
        # Read in all of the color entries.
        for index in range(0, 256):
            # Read the red, green, and blue values for the color.
            red, green, blue = palette_fh.read(3)

            total = red + green + blue
            grey = total // 3

            if not total:
                # If the color is black, add it to the list.
                black_pixels.add(index)

            # Store the red, green, and blue values as well as the alpha value.
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
        still has to happen (requires two additions instead of 3 additions and a
        bit shift).  I suppose a constant-time lookup is faster than an addition
        and a bit shift.  Still, I wouldn't have expected a 70% increase in speed.

        There is a slight loss of fidelity as int((a + b) // 4) + int((c + d) // 4)
        could be a slightly lower value than int((a + b + c + d) // 4).  Ultimately,
        due to how the palettes are setup, this likely will not change the color of
        the pixel or, if it does, it will only change very slightly.  In practice, I
        did not notice any differences.
    """

    cached = {}

    for index in range(256):
        cached[index] = {}

        for index2 in range(256):
            cached[index][index2] = (index + index2) >> 2

    return cached

def generate_data(window_w):
    """
        This function generates two rows of values at either the min or max value
        of the palette. These are used in the averaging algorithm.
    """

    return np.random.choice([0, 255], size=window_w + window_w, p=[0.75, 0.25])

if __name__ == "__main__":
    fire = Fire()
    fire.main()
