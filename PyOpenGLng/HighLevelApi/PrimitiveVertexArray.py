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
#                                              Audit
#
# - 02/05/2013 Fabrice
#   - check duplicated code
#   - 2 VBOs for rectangle ?
#
####################################################################################################

""" This modules provides tools to draw segments and rectangles primitives.

The aim of these classes has to be used by a Geometry Shader.
"""

####################################################################################################

from six.moves import xrange

####################################################################################################

import logging
import numpy as np

####################################################################################################

from . import GL
from .Buffer import GlArrayBuffer
from .VertexArrayObject import GlVertexArrayObject

####################################################################################################

class GlLinesVertexArray(GlVertexArrayObject):

    """ Base class to draw primitives as lines. """

    ##############################################
    
    def __init__(self, objects=None):

        super(GlLinesVertexArray, self).__init__()

        self._number_of_objects = 0
        self._vertex_array_buffer = GlArrayBuffer()

        if objects is not None:
            self.set(objects)

    ##############################################
    
    def set(self, objects):

        raise NotImplementedError

    ##############################################
    
    def bind_to_shader(self, shader_program_interface_attribute):

        """ Bind the vertex array to the shader program interface attribute.
        """

        self.bind()
        shader_program_interface_attribute.bind_to_buffer(self._vertex_array_buffer)
        self.unbind()

    ##############################################
    
    def draw(self):

        """ Draw the vertex array as lines. """

        self.bind()
        GL.glDrawArrays(GL.GL_LINES, 0, 2*self._number_of_objects)
        self.unbind()

####################################################################################################

class GlSegmentVertexArray(GlLinesVertexArray):

    """ Base class to draw segments primitives as lines. """

    _logger = logging.getLogger(__name__)

    ##############################################
    
    def __init__(self, segments=None):

        super(GlSegmentVertexArray, self).__init__(objects=segments)

    ##############################################
    
    def set(self, segments):

        """ Set the vertex array from an iterable of segments. """

        self._number_of_objects = len(segments)

        vertex = np.zeros((2*self._number_of_objects, 2), dtype='f') # dtype=np.float
        for i in xrange(self._number_of_objects):
            segment = segments[i]
            j = 2*i
            vertex[j] = segment.p1
            vertex[j+1] = segment.p2

        self._logger.debug(str(vertex)) # Fixme:

        self._vertex_array_buffer.set(vertex)

####################################################################################################

class GlRectangleVertexArray(GlLinesVertexArray):

    """ Base class to draw rectangles primitives as lines. """

    ##############################################
    
    def __init__(self, rectangles=None):

        super(GlRectangleVertexArray, self).__init__(objects=rectangles)

    ##############################################
    
    def set(self, rectangles):

        """ Set the vertex array from an iterable of rectangles. """

        self._number_of_objects = len(rectangles)

        vertex = np.zeros((2*self._number_of_objects, 2), dtype='f') # dtype=np.float
        for i in xrange(self._number_of_objects):
            rectangle = rectangles[i]
            j = 2*i
            vertex[j] = rectangle.point
            vertex[j+1] = rectangle.dimension

        self._vertex_array_buffer.set(vertex)

####################################################################################################

class TriangleVertexArray(GlVertexArrayObject):

    """ Base class to draw primitives as triangles. """

    # Fixme: 3d

    ##############################################
    
    def __init__(self, items=None):

        super(TriangleVertexArray, self).__init__()

        self._number_of_items = 0
        self._positions_buffer = GlArrayBuffer()
        self._normals_buffer = GlArrayBuffer()
        self._colours_buffer = GlArrayBuffer()

        if items is not None:
            self.set(*items)

    ##############################################
    
    def set(self, positions, normals, colours):

        """ Set the vertex array from an iterable of triangles. """

        self._number_of_items = positions.shape[0]

        # Fixme:
        #  - set from high level primitive: slow
        #  - set from Numpy array: fast but check for mistake

        # vertex = np.zeros((self._number_of_objects, 3), dtype='f') # dtype=np.float

        self._positions_buffer.set(positions)
        self._normals_buffer.set(normals)
        self._colours_buffer.set(colours)

    ##############################################
    
    def bind_to_shader(self, shader_program_interface):

        """ Bind the vertex array to the shader program interface attribute.
        """

        # Fixme: we cannot reuse the vbo

        self.bind()
        shader_program_interface.position.bind_to_buffer(self._positions_buffer)
        shader_program_interface.normal.bind_to_buffer(self._normals_buffer)
        shader_program_interface.colour.bind_to_buffer(self._colours_buffer)
        self.unbind()

    ##############################################
    
    def draw(self):

        """ Draw the vertex array as lines. """

        self.bind()
        GL.glDrawArrays(GL.GL_TRIANGLES, 0, 3*self._number_of_items)
        self.unbind()

####################################################################################################
#
# End
#
####################################################################################################
