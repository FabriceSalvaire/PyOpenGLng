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

import six

####################################################################################################

from . import GL
from ..Math.Functions import epsilon_float

####################################################################################################

channel2GL = [GL.GL_RED, GL.GL_GREEN, GL.GL_BLUE]

####################################################################################################

def set_colour(red, blue, green):

    GL.glColor3i(red, blue, green)

####################################################################################################

def set_solid_line_style():

    GL.glDisable(GL.GL_LINE_STIPPLE)

def set_dashed_line_style():

    GL.glEnable(GL.GL_LINE_STIPPLE)
    GL.glLineStipple(1, 0x00FF)

def set_dotted_line_style():

    GL.glEnable(GL.GL_LINE_STIPPLE)
    # pattern = 0o101 = 00101
    GL.glLineStipple(1, 65)

def set_dash_dotted_line_style():

    GL.glEnable(GL.GL_LINE_STIPPLE)
    GL.glLineStipple(1, 0x1C47)

####################################################################################################

def draw_line(x1, y1, x2, y2):

    if x1 == y1 and x2 == y2:
        GL.glBegin(GL.GL_POINTS)
        GL.glVertex2f(x1, y1)
    else:
        GL.glBegin(GL.GL_LINES)
        GL.glVertex2i(x1, y1)
        GL.glVertex2i(x2, y2)

    GL.glEnd()

####################################################################################################

def draw_line_f(x1, y1, x2, y2):

    epsilon = .1

    if (epsilon_float(x1, x2, epsilon) and
        epsilon_float(y1, y2, epsilon)):

        GL.glBegin(GL.GL_POINTS)
        GL.glVertex2f(x1, y1)
        
    else:
        GL.glBegin(GL.GL_LINES)
        GL.glVertex2f(x1, y1)
        GL.glVertex2f(x2, y2)

    GL.glEnd()

####################################################################################################

def draw_rectangle(x1, y1, x2, y2):

    GL.glBegin(GL.GL_LINE_LOOP)
    GL.glVertex2i(x1, y1)
    GL.glVertex2i(x1, y2)
    GL.glVertex2i(x2, y2)
    GL.glVertex2i(x2, y1)
    GL.glEnd()

####################################################################################################

def draw_rectangle_with_dim(x, y, width, height):

    draw_rectangle(x, y, x + width, y + height)

####################################################################################################

def draw_rectangle_f(x1, y1, x2, y2):

    GL.glBegin(GL.GL_LINE_LOOP)
    GL.glVertex2f(x1, y1)
    GL.glVertex2f(x1, y2)
    GL.glVertex2f(x2, y2)
    GL.glVertex2f(x2, y1)
    GL.glEnd()

####################################################################################################

def draw_centred_square_f(x, y, size):

    draw_rectangle_f(x -size, y -size,
                     x +size, y +size)

####################################################################################################

def draw_rectangle_with_dim_f(x, y, width, height):

    draw_rectangle_f(x, y, x + width, y + height)

####################################################################################################

def draw_filled_rectangle_f(x1, y1, x2, y2):

    GL.glBegin(GL.GL_QUADS)
    GL.glVertex2f(x1, y1)
    GL.glVertex2f(x1, y2)
    GL.glVertex2f(x2, y2)
    GL.glVertex2f(x2, y1)
    GL.glEnd()

####################################################################################################
    
class GlLine(object):
    
    ##############################################
    
    def __init__(self, p0, p1):
        
        self.x0, self.y0 = p0.x, p0.y
        self.x1, self.y1 = p1.x, p1.y
        
    ##############################################
    
    def paint(self):

        draw_line_f(self.x0, self.y0, self.x1, self.y1)
        
####################################################################################################

class GlBoundingBox(object):

    ##############################################
    
    def __init__(self, x_min, y_min, x_max, y_max):

        self.x_min, self.y_min, self.x_max, self.y_max = x_min, y_min, x_max, y_max

    ##############################################
    
    def paint(self):

        draw_rectangle_f(self.x_min, self.y_min, self.x_max, self.y_max)

####################################################################################################

class GlRect(GlBoundingBox):

    ##############################################
    
    def __init__(self, p0, width, height):

        x_min, y_min = p0
        x_max, y_max = x_min + width, y_min + height

        super(GlRect, self).__init__(x_min, y_min, x_max, y_max)

####################################################################################################

class GlCentredSquare(GlBoundingBox):

    ##############################################
    
    def __init__(self, p0, size):

        x, y = p0
        x_min, y_min = x - size, y - size
        x_max, y_max = x + size, y + size

        super(GlCentredSquare, self).__init__(x_min, y_min, x_max, y_max)

####################################################################################################
#
# End
#
####################################################################################################
