####################################################################################################
#
# PyOpenGLV4 - An OpenGL V4 layer on top of PyOpengl..
# Copyright (C) 2013 Salvaire Fabrice
#
####################################################################################################

""" This class provides tools to manage OpenGL Vertex Array Objects.

Vertex array objects represent a collection of sets of vertex attributes. Each set
is stored as an array in a buffer object data store, with each element of the array
having a specified format and component count. The attributes of the currently
bound vertex array object are used as inputs to the vertex shader when executing
drawing commands.

Vertex array objects are container objects including references to buffer objects,
and are not shared.

The usual programming flow is to bind the VAO, then to bind a set of VBO at some locations and
finnaly to unbind the VAO for latter use.
"""

####################################################################################################

import logging

####################################################################################################

from OpenGL.GL.ARB import vertex_array_object as gl_vao

from OpenGL.arrays import arraydatatype as gl_array_data_type
GLuintArray = gl_array_data_type.GLuintArray

####################################################################################################

class GlVertexArrayObject(object):

    """ This class wraps an OpenGL Vertex Array OpenGL. """

    _logger = logging.getLogger(__name__)

    ##############################################
    
    def __init__(self):

        self._vao_id = gl_vao.glGenVertexArrays(1)

    ##############################################
    
    def __del__(self):

        self._logger.debug("Delete VAO %u" % (self._vao_id))
        gl_vao.glDeleteVertexArrays(1, [self._vao_id])

    ##############################################
    
    def bind(self):

        """ bind the vertex array object. """

        gl_vao.glBindVertexArray(self._vao_id)

    ##############################################
    
    def unbind(self):

        """ Unbind the vertex array object. """

        gl_vao.glBindVertexArray(0)

####################################################################################################
#
# End
#
####################################################################################################
