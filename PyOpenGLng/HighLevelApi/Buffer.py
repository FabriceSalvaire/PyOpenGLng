####################################################################################################
#
# PyOpenGLng - An OpenGL Python Wrapper with a High Level API.
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

####################################################################################################

from . import GL

####################################################################################################

_module_logger = logging.getLogger(__name__)

####################################################################################################

class GlBuffer(object):

    """ This class wraps an OpenGL Buffer.

    Public attributes:

      size

      type

    """

    # size and type attributes are used by VertexAttribPointer like functions.

    _logger = _module_logger.getChild(__name__)

    #: Define the target in subclass
    _target = None

    ##############################################
    
    def __init__(self, data=None):

        self._buffer_object_id = GL.glGenBuffers(1)

        self.size = 0
        self.type = None

        if data is not None:
            self.set(data)

    ##############################################
    
    def __del__(self):

        self._logger.debug("Delete Object %u" % (self._buffer_object_id))
        GL.glDeleteBuffers(1, [self._buffer_object_id])

    ##############################################
    
    def bind(self):

        """ Bind the buffer. """

        GL.glBindBuffer(self._target, self._buffer_object_id)

    ##############################################
    
    def unbind(self):

        """ Unind the buffer. """

        GL.glBindBuffer(self._target, 0)

    ##############################################
    
    def bind_buffer_base(self, binding_point):

        """ Binds the buffer object buffer to the given binding point. """

        GL.glBindBufferBase(self._target, binding_point, self._buffer_object_id)

    ##############################################
    
    def _set(self, data, usage):
        
        """ Set the data of the buffer. """

        if data.dtype == np.float32:
            self.type = GL.GL_FLOAT
        elif data.dtype == np.float64:
            self.type = GL.GL_DOUBLE
        elif data.dtype == np.int32:
            self.type = GL.GL_INT
        elif data.dtype == np.uint32:
            self.type = GL.GL_UNSIGNED_INT
        else:
            raise ValueError()

        # Fixme: shape?
        shape = data.shape
        if len(shape) == 2:
            self.size = data.shape[1] # xyzw
        else:
            self.size = 1

        self.bind()
        GL.glBufferData(self._target, data, usage)
        self.unbind()

    ##############################################
    
    def set(self, data, usage):

        """ Set the data of the buffer. """

        raise NotImplementedError

####################################################################################################

class GlUniformBuffer(GlBuffer):

    """ This class wraps an OpenGl Uniform Buffer. """

    _target = GL.GL_UNIFORM_BUFFER

    _logger = _module_logger.getChild(__name__)

    ##############################################
    
    def set(self, data, usage=GL.GL_DYNAMIC_DRAW):
        self._set(data, usage)

####################################################################################################

class GlArrayBuffer(GlBuffer):

    """ This class wraps an OpenGl Array Buffer. """

    _target = GL.GL_ARRAY_BUFFER

    _logger = _module_logger.getChild(__name__)

    ##############################################
    
    def set(self, data, usage=GL.GL_STATIC_DRAW):
        self._set(data, usage)

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
