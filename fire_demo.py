import OpenGL.GL as gl
import OpenGL.GLUT as glut
import numpy as np
from datetime import datetime
import glob
import random

# https://www.youtube.com/watch?v=a4NVQC_2S2U

# TODO: Remove the window frame
# TODO: Add a README.md
# TODO: Add a requirements file

class Fire:
    def __init__(self):
        self.window_w = 320
        self.window_h = 200
        self.size = self.window_w * self.window_h

        self.frames = 0

        self.read_palettes()

        # TODO: Make the default palette the first index.
        self.palette_index = 1
        self.num_palettes = len(self.palettes)

        self.back_buf = [0x00] * self.size
        self.display_buf = [0x00] * (self.size << 2)

    def read_palettes(self):
        self.palettes = []
        files = glob.glob("palettes\*.BIN")

        for file in files:
            self.palettes.append(self.make_palette(file))

    def make_palette(self, file):
        palette = []

        with open(file, "rb") as fh:
            for index in range(0, 256):
                r, g, b = fh.read(3)

                palette.extend([r, g, b, 0xFF])

        return(palette)

    def generate_data(self):
        # Generate two rows of values at either the min or max value of the palette.

        return random.choices([0, 255], weights=[2, 1], k=self.window_w << 1)

    def make_frame(self):
        pass

    def display_frame(self):
        random_bytes = self.generate_data()

        # TODO: This doesn't have to start at 0.
        for row in range(self.window_h - 2):
            row_index = (row + 1) * self.window_w

            for col in range(1, self.window_w - 1):
                col_index = row_index + col

                value = (
                    self.back_buf[col_index - 1]
                    + self.back_buf[col_index + 1]
                    + self.back_buf[col_index]
                    + self.back_buf[col_index + self.window_w]
                ) >> 2

                self.back_buf[row_index - self.window_w + col] = value

            # For column 0
            value = (
                self.back_buf[row_index- 1]
                + self.back_buf[row_index + 1]
                + self.back_buf[row_index]
                + self.back_buf[row_index + self.window_w]
            ) >> 2

            self.back_buf[row_index - self.window_w] = value

            # For last column
            value = (
                self.back_buf[row_index + self.window_w - 2]
                + self.back_buf[row_index]
                + self.back_buf[row_index + self.window_w - 1]
                + self.back_buf[row_index + self.window_w + self.window_w - 1]
            ) >> 2

            self.back_buf[row_index - 1] = value

        row_index = (self.window_h - 1) * self.window_w

        for col in range(1, self.window_w - 1):
            col_index = row_index + col

            value = (
                self.back_buf[col_index - 1]
                + self.back_buf[col_index + 1]
                + self.back_buf[col_index]
                + random_bytes[col]
            ) >> 2

            self.back_buf[row_index - self.window_w + col] = value

        # For column 0
        value = (
            self.back_buf[row_index + self.window_w - 1]
            + self.back_buf[row_index + 1]
            + self.back_buf[row_index]
            + random_bytes[0]
        ) >> 2

        self.back_buf[row_index - self.window_w] = value

        # For last column
        value = (
            self.back_buf[row_index + self.window_w - 2]
            + self.back_buf[row_index]
            + self.back_buf[row_index + self.window_w - 1]
            + random_bytes[self.window_w - 1]
        ) >> 2

        self.back_buf[row_index - 1] = value

        row_index = (self.window_h - 1) * self.window_w

        for col in range(1, self.window_w - 1):
            value = (
                + random_bytes[col - 1]
                + random_bytes[col + 1]
                + random_bytes[col]
                + random_bytes[self.window_w + col]
            ) >> 2

            self.back_buf[row_index - self.window_w + col] = value

        # For column 0
        value = (
            random_bytes[self.window_w - 1]
            + random_bytes[self.window_w + 1]
            + random_bytes[0]
            + random_bytes[self.window_w]
        ) >> 2

        self.back_buf[row_index - self.window_w] = value

        # For last column
        value = (
            random_bytes[self.window_w - 2]
            + random_bytes[self.window_w]
            + random_bytes[self.window_w - 1]
            + random_bytes[(self.window_w << 1) - 1]
        ) >> 2

        self.back_buf[row_index - 1] = value

        index = 0

        for value in self.back_buf:
            quad = value << 2

            self.display_buf[index:index + 3] = self.palettes[self.palette_index][quad:quad + 3]

            index += 4

        #print("BACK_BUF:\n{}\n\n".format(self.back_buf))

        pixels = bytes(self.display_buf)
        bitmap = np.frombuffer(pixels, np.uint8)

        # TODO: Mapping a texture to a polygon should be much faster.

        gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)
        gl.glLoadIdentity()
        gl.glDrawPixels(self.window_w, self.window_h, gl.GL_RGBA, gl.GL_UNSIGNED_BYTE, bitmap)
        glut.glutSwapBuffers()

        self.frames += 1

    def kb_input(self, key, x, y):
        if key in [b'q', b'Q', b'\x1B']:
            stop_time = datetime.now()

            glut.glutDestroyWindow(self.window)

            print ("Frames: {}".format(self.frames))
            print ("Seconds: {}".format(((stop_time - self.start_time).total_seconds())))
            print ("FPS: {}".format(self.frames / (stop_time - self.start_time).total_seconds()))
        elif key in [b'p', b'P']:
            if self.palette_index == self.num_palettes - 1:
                self.palette_index = 0
            else:
                self.palette_index += 1
        else:
            print ("KEY: {}".format(key))

    def main(self):
        glut.glutInit()

        screen_w = glut.glutGet(glut.GLUT_SCREEN_WIDTH)
        screen_h = glut.glutGet(glut.GLUT_SCREEN_HEIGHT)

        glut.glutInitDisplayMode(glut.GLUT_RGBA)
        glut.glutInitWindowSize(self.window_w, self.window_h)
        glut.glutInitWindowPosition(int((screen_w - self.window_w) / 2), int((screen_h - self.window_h) / 2))
        self.window = glut.glutCreateWindow("GoldFire Rides Again")
        glut.glutDisplayFunc(self.display_frame)
        glut.glutIdleFunc(self.display_frame)
        glut.glutKeyboardFunc(self.kb_input)
        self.start_time = datetime.now()
        glut.glutMainLoop()

if __name__ == "__main__":
    fire = Fire()
    fire.main()
