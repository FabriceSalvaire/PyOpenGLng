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
QUERY_BUFFER              Query result buffer
SHADER_STORAGE_BUFFER     Read-write storage for shaders
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

        self._gl_id = GL.glGenBuffers(1)
        
        self.size = 0
        self._dtype = None
        self._dtype_nbytes = None
        self.type = None
        
        if data is not None:
            self.set(data)

    ##############################################

    def __del__(self):

        self._logger.debug("Delete Object %u" % (self._gl_id))
        GL.glDeleteBuffers([self._gl_id])

    ##############################################

    def bind(self):

        """ Bind the buffer. """

        GL.glBindBuffer(self._target, self._gl_id)

    ##############################################

    def unbind(self):

        """ Unind the buffer. """

        GL.glBindBuffer(self._target, 0)

    ##############################################

    def bind_buffer_base(self, binding_point):

        """ Binds the buffer object buffer to the given binding point. """

        GL.glBindBufferBase(self._target, binding_point, self._gl_id)

    ##############################################

    def _set(self, data, usage):

        """Set the data of the buffer.

        usage: Specifies the expected usage pattern of the data store. The symbolic constant must be
        GL_STREAM_DRAW, GL_STREAM_READ, GL_STREAM_COPY, GL_STATIC_DRAW, GL_STATIC_READ,
        GL_STATIC_COPY, GL_DYNAMIC_DRAW, GL_DYNAMIC_READ, or GL_DYNAMIC_COPY.

        """

        self._dtype = data.dtype
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
        self._dtype_nbytes = self._dtype.type(1).nbytes
        
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

    ##############################################

    def set_sub_data(self, data, offset):

        """ Set buffer sub-data.

        The parameter offset lies in a linear array shape.
        """

        self.bind()
        # print(offset, self._dtype_nbytes)
        offset = offset * self._dtype_nbytes
        GL.glBufferSubData(self._target, offset, data)
        self.unbind()

    ##############################################

    def read_sub_data(self, offset, data=None, size=None):

        """ Read buffer sub-data.

        The parameter offset and size lies in a linear array shape.
        """

        if data is None:
            if size is None:
                raise ValueError("size must be provided when data is None")
            data = np.zeros((size,), dtype=self._dtype)
        
        self.bind()
        offset = offset * self._dtype_nbytes
        GL.glGetBufferSubData(self._target, offset, data)
        self.unbind()
        
        return data

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
