####################################################################################################
#
# PyOpenGLV4 - An OpenGL V4 layer on top of PyOpengl.
# Copyright (C) 2013 Salvaire Fabrice
#
####################################################################################################

""" This class provides tools to manage OpenGL Buffer Objects.

========================= ==================================
Target name               Purpose
========================= ==================================
ARRAY_BUFFER              Vertex attributes
ATOMIC_COUNTER_BUFFER     Atomic counter storage
COPY_READ_BUFFER          Buffer copy source
COPY_WRITE_BUFFER         Buffer copy destination
DISPATCH_INDIRECT_BUFFER  Indirect compute dispatch commands
DRAW_INDIRECT_BUFFER      Indirect command arguments
ELEMENT_ARRAY_BUFFER      Vertex array indices
PIXEL_PACK_BUFFER         Pixel read target
PIXEL_UNPACK_BUFFER       Texture data source
SHADER_STORAGE_BUFFER     Read=write storage for shaders
TEXTURE_BUFFER            Texture data buffer
TRANSFORM_FEEDBACK_BUFFER Transform feedback buffer
UNIFORM_BUFFER            Uniform block storage
========================= ==================================

"""

####################################################################################################

import logging

import numpy as np

import OpenGL.GL as GL
from OpenGL.GL.ARB import vertex_buffer_object as gl_vbo
from OpenGL.arrays import arraydatatype as gl_array_data_type

####################################################################################################

class GlBuffer(object):

    """ This class wraps an OpenGL Buffer.

    Public attributes:

      size

      type

    """

    # size and type attributes are used by VertexAttribPointer like functions.

    _logger = logging.getLogger(__name__)

    #: Define the target in subclass
    _target = None

    ##############################################
    
    def __init__(self, data=None):

        self._buffer_object_id = gl_vbo.glGenBuffersARB(1)

        self.size = 0
        self.type = None

        if data is not None:
            self.set(data)

    ##############################################
    
    def __del__(self):

        self._logger.debug("Delete Object %u" % (self._buffer_object_id))
        gl_vbo.glDeleteBuffersARB(1, [self._buffer_object_id])

    ##############################################
    
    def bind(self):

        """ Bind the buffer. """

        gl_vbo.glBindBufferARB(self._target, self._buffer_object_id)

    ##############################################
    
    def unbind(self):

        """ Unind the buffer. """

        gl_vbo.glBindBufferARB(self._target, 0)

    ##############################################
    
    def bind_buffer_base(self, binding_point):

        """ Binds the buffer object buffer to the given binding point. """

        GL.glBindBufferBase(self._target, binding_point, self._buffer_object_id)

    ##############################################
    
    def set(self, data):

        raise NotImplementedError

    ##############################################
    
    def _set_float(self, data, usage=GL.GL_STATIC_DRAW):
        
        """ Set the data of the buffer.
        
        Data type must be float 32-bit.
        """

        if data.dtype == np.float32:
            self.type = GL.GL_FLOAT
        else:
            raise ValueError()

        self.bind()
        data_size = gl_array_data_type.ArrayDatatype.arrayByteCount(data)
        gl_vbo.glBufferDataARB(self._target, data_size, data, usage)
        self.unbind()

####################################################################################################

class GlUniformBuffer(GlBuffer):

    """ This class wraps an OpenGl Uniform Buffer. """

    _target = GL.GL_UNIFORM_BUFFER

    _logger = logging.getLogger(__name__)

    ##############################################
    
    def set(self, data, usage=GL.GL_DYNAMIC_DRAW):
        
        """ Set the data of the buffer.
        
        Data type must be float 32-bit.
        """

        self.size = data.shape # ?
        self._set_float(data, usage)

####################################################################################################

class GlArrayBuffer(GlBuffer):

    """ This class wraps an OpenGl Array Buffer. """

    _target = GL.GL_ARRAY_BUFFER

    _logger = logging.getLogger(__name__)

    ##############################################
    
    def set(self, data, usage=GL.GL_STATIC_DRAW):
        
        """ Set the data of the buffer.
        
        Data type must be float 32-bit.
        """

        self.size = data.shape[1] # xyzw
        self._set_float(data, usage)

    ##############################################
    
    def bind_at_location(self, location):

        """ Bind and enable the Vertex Buffer Object at the given attribute location. """

        self._logger.debug("Bind at location %u" % (location))        
        self.bind()
        GL.glVertexAttribPointer(location, self.size, self.type, GL.GL_FALSE, 0, None)
        GL.glEnableVertexAttribArray(location) # cf. enable # required !
        self.unbind()

####################################################################################################
#
# End
#
####################################################################################################
