####################################################################################################
#
# PyOpenGLV4 - An OpenGL V4 layer on top of PyOpengl.
# Copyright (C) 2013 Salvaire Fabrice
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

import logging
import numpy as np

import OpenGL.GL as GL

####################################################################################################

from .VertexArrayObject import GlVertexArrayObject
from .Buffer import GlArrayBuffer

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
            vertex[j] = segment.p1.vertex
            vertex[j+1] = segment.p2.vertex

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
            vertex[j] = rectangle.point.vertex
            vertex[j+1] = rectangle.dimension.vertex

        self._vertex_array_buffer.set(vertex)

####################################################################################################
#
# End
#
####################################################################################################
