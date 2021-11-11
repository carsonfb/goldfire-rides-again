import OpenGL.GL as gl
import OpenGL.GLUT as glut
#from OpenGL.GLU import *

# https://www.youtube.com/watch?v=a4NVQC_2S2U

WINDOW_W = 640
WINDOW_H = 480

def showScreen():
    gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)
    gl.glLoadIdentity()
    glut.glutSwapBuffers()


def main():
    glut.glutInit()

    screen_w = glut.glutGet(glut.GLUT_SCREEN_WIDTH)
    screen_h = glut.glutGet(glut.GLUT_SCREEN_HEIGHT)

    glut.glutInitDisplayMode(glut.GLUT_RGBA)
    glut.glutInitWindowSize(WINDOW_W, WINDOW_H)
    glut.glutInitWindowPosition(int((screen_w - WINDOW_W) / 2), int((screen_h - WINDOW_H) / 2));
    wind = glut.glutCreateWindow("GoldFire Rides Again")
    glut.glutDisplayFunc(showScreen)
    glut.glutIdleFunc(showScreen)
    glut.glutMainLoop()

if __name__ == "__main__":
        main()
