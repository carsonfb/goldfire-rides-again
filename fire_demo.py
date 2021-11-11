import OpenGL.GL as gl
import OpenGL.GLUT as glut
#from OpenGL.GLU import *
import numpy

# https://www.youtube.com/watch?v=a4NVQC_2S2U

WINDOW_W = 640
WINDOW_H = 480

def read_palettes():
    pass

def make_palette():
    pass

def display_frame():
    pixels = bytes([0xFF, 0x7F, 0x00, 0xFF, 0x00, 0xFF, 0X7F, 0XFF])
    bitmap = numpy.fromstring(pixels * 320 * 480, numpy.uint8)

    gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)
    gl.glLoadIdentity()
    gl.glDrawPixels(WINDOW_W, WINDOW_H, gl.GL_RGBA, gl.GL_FLOAT, bitmap)
    glut.glutSwapBuffers()

def main():
    glut.glutInit()

    screen_w = glut.glutGet(glut.GLUT_SCREEN_WIDTH)
    screen_h = glut.glutGet(glut.GLUT_SCREEN_HEIGHT)

    glut.glutInitDisplayMode(glut.GLUT_RGBA)
    glut.glutInitWindowSize(WINDOW_W, WINDOW_H)
    glut.glutInitWindowPosition(int((screen_w - WINDOW_W) / 2), int((screen_h - WINDOW_H) / 2))
    wind = glut.glutCreateWindow("GoldFire Rides Again")
    glut.glutDisplayFunc(display_frame)
    glut.glutIdleFunc(display_frame)
    glut.glutMainLoop()

if __name__ == "__main__":
    main()
