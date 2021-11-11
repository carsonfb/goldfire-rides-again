import OpenGL.GL as gl
import OpenGL.GLUT as glut
#from OpenGL.GLU import *
import numpy
#import line_profiler
import sys
from datetime import datetime
import glob
import random

# https://www.youtube.com/watch?v=a4NVQC_2S2U

# TODO: Add keyboard support
# TODO: Remove the window frame
# TODO: Add a README.md
# TODO: Add a requirements file
# TODO: Add profiling

class Fire:
    def __init__(self):
        self.window_w = 640
        self.window_h = 480
        self.size = self.window_w * self.window_h

        self.frames = 0

        self.read_palettes()

        self.palette_index = 0
        self.num_palettes = len(self.palettes)

        self.front_buf = [0x00] * self.size
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
        random_bytes = []

        # Generate two rows of values at either the min or max value of the palette.
        for i in range(0, self.window_w << 1):
            random_bytes.append(random.randint(0, 1) * 255)

    def make_frame(self):
        pass

    #@profile
    def display_frame(self):
        random_bytes = self.generate_data()

        pixels = bytes([0xFF, 0x7F, 0x00, 0xFF, 0x00, 0xFF, 0X7F, 0XFF])
        bitmap = numpy.frombuffer(pixels * 320 * 480, numpy.uint8)

        index = 0

        for row in range(0, self.window_h):
            row_index = row * self.window_h

            for col in range(0, self.window_w):
                value = 0

                if col == 0:
                    value += self.back_buf[row_index + self.window_h - 1]
                    value += self.back_buf[row_index + col + 1]
                elif col == self.window_h - 1:
                    value += self.back_buf[row_index + col - 1]
                    value += self.back_buf[row_index]
                else:
                    value += self.back_buf[row_index + col - 1]
                    value += self.back_buf[row_index + col + 1]


        # TODO: Mapping a texture to a polygon should be much faster.

        gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)
        gl.glLoadIdentity()
        gl.glDrawPixels(self.window_w, self.window_h, gl.GL_RGBA, gl.GL_FLOAT, bitmap)
        glut.glutSwapBuffers()

        self.frames += 1

        if self.frames == 5000:
            stop_time = datetime.now()

            glut.glutDestroyWindow(self.window)

            print ("Frames: {}".format(self.frames))
            print ("Seconds: {}".format(((stop_time - self.start_time).total_seconds())))
            print ("FPS: {}".format(self.frames / (stop_time - self.start_time).total_seconds()))

    def kb_input(self, key, x, y):
        if key in [b'q', b'Q', b'\x1B']:
            stop_time = datetime.now()

            glut.glutDestroyWindow(self.window)

            print ("Frames: {}".format(self.frames))
            print ("Seconds: {}".format(((stop_time - self.start_time).total_seconds())))
            print ("FPS: {}".format(self.frames / (stop_time - self.start_time).total_seconds()))
        else:
            print ("KEY: {}".format(key))

    #@profile
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
