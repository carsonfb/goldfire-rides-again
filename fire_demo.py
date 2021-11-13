import os
from datetime import datetime
import glob
import random
import OpenGL.GL as gl
import OpenGL.GLUT as glut
import numpy as np

# https://www.youtube.com/watch?v=a4NVQC_2S2U

class Fire:
    """
        This class creates a modified version of the old demo GoldFire.  The
        fire routine calculations are slightly adjusted from the original, some
        of the features have not been implemented yet (may never be), and the
        original had fire at both the top and bottom of the screen.

        The palette file format from the original is supported and most of the
        palettes from the original are included.  These are binary files
        consisting of 256 triplets of red, green, and blue values.
    """

    def __init__(self):
        # Setup the starting time.  It will be initialized later.
        self.start_time = None

        # Initialize the window size.
        self.window = None
        #self.window_w = 384
        #self.window_h = 240
        self.window_w = 320
        self.window_h = 200
        self.first_row = 140
        self.size = self.window_w * self.window_h

        self.end_to = (self.window_h - self.first_row) * self.window_w
        self.start_from = self.first_row * self.window_w
        self.end_from = (self.window_h - 1) * self.window_w + self.window_w

        # Set the starting frames to 0.
        self.frames = 0

        # Initialize the palettes.
        self.palette_index = 0
        self.palettes = self.read_palettes()
        self.num_palettes = len(self.palettes)

        # Initialize the display buffer and back buffer. The back buffer only has
        # the palette lookup value, so it is only a 1/4 of the size.
        self.back_buf = [0x00] * self.size
        self.display_buf = [0x00] * (self.size << 2)

    def read_palettes(self):
        """
            This method reads the palettes from the palettes folder on disk.  Users can supply
            their own palettes and they will be automatically loaded.  The default palette will
            be loaded as the first in the list.
        """

        # Initialize the palette structure and leave a placeholder for the default palette.
        palettes = []
        palettes.append([])

        # Find all of the palette files in the palettes folder.
        files = glob.glob(r"palettes\*.bin")

        for file in files:
            if os.path.getsize(file) != 768:
                # Skip the palette file if it is the wrong size.
                continue

            if "default.bin" in file:
                # Set the default palette to the first palette entry.
                palettes[0] = Fire.make_palette(file)
            else:
                # Appened palettes other than the default to the list.
                palettes.append(Fire.make_palette(file))

        return palettes

    @classmethod
    def make_palette(cls, file):
        """ This method loads a palette file and appends the alpha value. """

        # Initialize the palette structure.
        palette = []

        with open(file, "rb") as palette_fh:
            # Read in all of the color entries.
            for _ in range(0, 256):
                # Read the red, green, and blue values for the color.
                red, green, blue = palette_fh.read(3)

                # Store the red, green, and blue values as well as the alpha value.
                palette.extend([red, green, blue, 0xFF])

        return palette

    def generate_data(self):
        """
            This method generates two rows of values at either the min or max value
            of the palette. These are used in the averaging algorithm.
        """

        return random.choices([0, 255], weights=[3, 1], k=self.window_w << 1)

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

        # Generate two rows of random data.
        random_bytes = self.generate_data()

		# The fire cuts out on its own due to the algorithm.  Only the bottom 60 or so
		# rows need to be calculated.
        for row in range(self.first_row, self.window_h - 2):
            # The last two rows are calculated separately since they
            # have special processing due to the random data.

            # The next row is pre-calculated to save processing.
            from_index = (row + 1) * self.window_w
            to_index = from_index - self.window_w

            for col in range(1, self.window_w - 1):
                # Process all columns except for the first and last column.

                # The pixel directly below the current one is pre-calculated
                # to save processing.
                col_index = from_index + col

                value = (
                    self.back_buf[col_index - 1]
                    + self.back_buf[col_index + 1]
                    + self.back_buf[col_index]
                    + self.back_buf[col_index + self.window_w]
                ) >> 2

                self.back_buf[to_index + col] = value

            # Process the first column.
            value = (
                self.back_buf[from_index- 1]
                + self.back_buf[from_index + 1]
                + self.back_buf[from_index]
                + self.back_buf[from_index + self.window_w]
            ) >> 2

            self.back_buf[to_index] = value

            # For last column
            value = (
                self.back_buf[from_index + self.window_w - 2]
                + self.back_buf[from_index]
                + self.back_buf[from_index + self.window_w - 1]
                + self.back_buf[from_index + self.window_w + self.window_w - 1]
            ) >> 2

            self.back_buf[from_index - 1] = value

        # The next row is pre-calculated to save processing.
        from_index = (self.window_h - 1) * self.window_w
        to_index = from_index - self.window_w

        for col in range(1, self.window_w - 1):
            # The pixel directly below the current one is pre-calculated
            # to save processing.
            col_index = from_index + col

            value = (
                self.back_buf[col_index - 1]
                + self.back_buf[col_index + 1]
                + self.back_buf[col_index]
                + random_bytes[col]
            ) >> 2

            self.back_buf[from_index - self.window_w + col] = value

        # For column 0
        value = (
            self.back_buf[from_index + self.window_w - 1]
            + self.back_buf[from_index + 1]
            + self.back_buf[from_index]
            + random_bytes[0]
        ) >> 2

        self.back_buf[to_index] = value

        # For last column
        value = (
            self.back_buf[from_index + self.window_w - 2]
            + self.back_buf[from_index]
            + self.back_buf[from_index + self.window_w - 1]
            + random_bytes[self.window_w - 1]
        ) >> 2

        self.back_buf[from_index - 1] = value

        # The next row is pre-calculated to save processing.
        from_index = (self.window_h - 1) * self.window_w
        to_index = from_index - self.window_w

        for col in range(1, self.window_w - 1):
            value = (
                + random_bytes[col - 1]
                + random_bytes[col + 1]
                + random_bytes[col]
                + random_bytes[self.window_w + col]
            ) >> 2

            self.back_buf[to_index + col] = value

        # For column 0
        value = (
            random_bytes[self.window_w - 1]
            + random_bytes[self.window_w + 1]
            + random_bytes[0]
            + random_bytes[self.window_w]
        ) >> 2

        self.back_buf[to_index] = value

        # For last column
        value = (
            random_bytes[self.window_w - 2]
            + random_bytes[self.window_w]
            + random_bytes[self.window_w - 1]
            + random_bytes[(self.window_w << 1) - 1]
        ) >> 2

        self.back_buf[from_index - 1] = value

        # Copy the bottom values to the top.  This is reversed from left-to-right but
        # Not reversing it requires a loop and was a performance hit.  This will just be
        # another difference between the original and this version.
        self.back_buf[0:self.end_to] = self.back_buf[self.start_from:self.end_from][::-1]

        index = 0

        for value in self.back_buf:
            quad = value << 2

            self.display_buf[index:index + 3] = self.palettes[self.palette_index][quad:quad + 3]

            index += 4

        pixels = bytes(self.display_buf)

        return np.frombuffer(pixels, np.uint8)

    def display_frame(self):
        """
            This method is the callback for the OpenGL window and displays
            an updated frame of the fire.
        """

		# Generate the new frame.
        bitmap = self.make_frame()

        # TODO: Mapping a texture to a polygon should be much faster.

        # Display the new frame.
        gl.glDrawPixels(self.window_w, self.window_h, gl.GL_RGBA, gl.GL_UNSIGNED_BYTE, bitmap)
        glut.glutSwapBuffers()

        # Increment the number of frames for the purpose of calculating the FPS.
        self.frames += 1

    def kb_input(self, key, _x_pos, _y_pos):
        """ This method handles keyboard input from the user. """

        if key in [b'q', b'Q', b'\x1B']:
            # If the user pressed q or esc, terminate the program.

            # Get the current time and caculate the elapsed time and FPS.
            stop_time = datetime.now()
            elapsed_time = (stop_time - self.start_time).total_seconds()
            fps = self.frames / elapsed_time

            # Close the OpenGL window.
            glut.glutDestroyWindow(self.window)

            # Display the statistics to the user.
            print (f"Frames: {self.frames}")
            print (f"Seconds: {elapsed_time}")
            print (f"FPS: {fps}")
        elif key in [b'p', b'P']:
            # If the user pressed p, cycle through the palettes.
            if self.palette_index == self.num_palettes - 1:
                # If the last palette is already in use, go back to the default palette.
                self.palette_index = 0
            else:
                # Go to the next palette.
                self.palette_index += 1
        elif key in ([b'r', b'R']):
            self.palette_index = random.randint(0, self.num_palettes - 1)

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
        center_x = int((screen_w - self.window_w) >> 1)
        center_y = int((screen_h - self.window_h) >> 1)

        # Create the OpenGL window and display it.
        glut.glutInitDisplayMode(glut.GLUT_RGBA)
        glut.glutInitWindowSize(self.window_w, self.window_h)
        glut.glutInitWindowPosition(center_x, center_y)
        self.window = glut.glutCreateWindow("GoldFire Rides Again")

        # Setup the callbacks for OpenGL as well as initialize the start time.
        glut.glutDisplayFunc(self.display_frame)
        glut.glutIdleFunc(self.display_frame)
        glut.glutKeyboardFunc(self.kb_input)
        self.start_time = datetime.now()

		# Flip the image upsid-right.
        gl.glLoadIdentity()
        gl.glRasterPos2f(-1,1)
        gl.glPixelZoom(1, -1)

        # Start the main program loop.
        glut.glutMainLoop()

if __name__ == "__main__":
    fire = Fire()
    fire.main()
