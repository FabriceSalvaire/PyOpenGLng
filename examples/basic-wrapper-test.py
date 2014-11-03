####################################################################################################
# 
# PyOpenGLng - An OpenGL Python Wrapper with a High Level API.
# Copyright (C) 2014 Fabrice Salvaire
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
# 
####################################################################################################

####################################################################################################
#
# This script shows a basic usage of the wrapper.
#
#   GLFW is used to create a window and an OpenGL context.
#   For simplicity, we use the OpenGL 2.1 API to display a triangle.   
#
####################################################################################################

import logging
import sys

####################################################################################################

import PyGlfwCffi as glfw
import PyOpenGLng.Wrapper as GlWrapper
from PyOpenGLng.GlApi import ApiNumber

####################################################################################################

logging.basicConfig(
    format='\033[1;32m%(asctime)s\033[0m - \033[1;34m%(name)s.%(funcName)s\033[0m - \033[1;31m%(levelname)s\033[0m - %(message)s',
    level=logging.WARNING,
)

####################################################################################################
#
# GLFW Callbacks
#

@glfw.key_callback
def on_key(window, key, scancode, action, mods):
    if key == glfw.KEY_ESCAPE and action == glfw.PRESS:
        glfw.set_window_should_close(window, 1)

def error_callback(error, description):
    raise NameError("{} {}".format(error, description))

####################################################################################################

# Initialize the GLFW library
if not glfw.init():
    sys.exit()
glfw.set_error_callback(error_callback)

# Create a windowed mode window and its OpenGL context
api_number = ApiNumber('2.1')
glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, api_number.major)
glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, api_number.minor)
glfw.window_hint(glfw.CLIENT_API, glfw.OPENGL_API)
window = glfw.create_window(640, 480, "Hello World")
if not window:
    glfw.terminate()
    sys.exit()

# Create the OpenGL wrapper
gl = GlWrapper.init(api_number=str(api_number), profile='compat',
                    check_api_number=False,
                    wrapper='ctypes') # or cffi

# Make the window's context current
glfw.make_context_current(window)

# Install a key handler
glfw.set_key_callback(window, on_key)

# Loop until the user closes the window
while not glfw.window_should_close(window):
    # Render here
    width, height = glfw.get_framebuffer_size(window)
    ratio = width / float(height)
    gl.glViewport(0, 0, width, height)
    gl.glClear(gl.GL_COLOR_BUFFER_BIT)
    gl.glMatrixMode(gl.GL_PROJECTION)
    gl.glLoadIdentity()
    gl.glOrtho(-ratio, ratio, -1, 1, 1, -1)
    gl.glMatrixMode(gl.GL_MODELVIEW)
    gl.glLoadIdentity()
    gl.glBegin(gl.GL_TRIANGLES)
    gl.glColor3f(1, 0, 0)
    gl.glVertex3f(-0.6, -0.4, 0)
    gl.glColor3f(0, 1, 0)
    gl.glVertex3f(0.6, -0.4, 0)
    gl.glColor3f(0, 0, 1)
    gl.glVertex3f(0, 0.6, 0)
    gl.glEnd()

    # Swap front and back buffers
    glfw.swap_buffers(window)

    # Poll for and process events
    glfw.poll_events()

glfw.terminate()

####################################################################################################
# 
# End
# 
####################################################################################################
