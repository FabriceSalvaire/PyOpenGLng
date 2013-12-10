####################################################################################################
#
# PyOpenGLng - An OpenGL Python Wrapper with a High Level API.
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

from . import GL

####################################################################################################

class GlVertexArrayObject(object):

    """ This class wraps an OpenGL Vertex Array OpenGL. """

    _logger = logging.getLogger(__name__)

    ##############################################
    
    def __init__(self):

        self._vao_id = GL.glGenVertexArrays(1)

    ##############################################
    
    def __del__(self):

        self._logger.debug("Delete VAO %u" % (self._vao_id))
        GL.glDeleteVertexArrays(1, [self._vao_id])

    ##############################################
    
    def bind(self):

        """ bind the vertex array object. """

        GL.glBindVertexArray(self._vao_id)

    ##############################################
    
    def unbind(self):

        """ Unbind the vertex array object. """

        GL.glBindVertexArray(0)

####################################################################################################
#
# End
#
####################################################################################################
