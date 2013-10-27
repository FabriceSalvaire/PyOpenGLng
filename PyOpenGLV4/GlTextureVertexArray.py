####################################################################################################
#
# PyOpenGLV4 - An OpenGL V4 layer on top of PyOpengl.
# Copyright (C) 2013 Salvaire Fabrice
#
####################################################################################################

""" This modules provides to tools to manage texture. """

####################################################################################################

import logging

import numpy as np

import OpenGL
import OpenGL.GL as GL
# Fix: define GL_RG_INTEGER cf. /usr/include/GL/glext.h
GL.GL_RG_INTEGER = OpenGL.constant.Constant('GL_RG_INTEGER', 0x8228)

####################################################################################################

from .GlVertexArrayObject import GlVertexArrayObject
from .GlBuffer import GlArrayBuffer

####################################################################################################

class GlTextureVertexArray(GlVertexArrayObject):

    """ This class wraps a Texture Vertex Array. """

    _logger = logging.getLogger(__name__)

    _uv_vbo = None

    ##############################################
    
    def __init__(self, position, dimension, image=None, integer_internal_format=False):

        """ The parameters *position* and *dimension* define the quad where is mapped the texture.
        """

        super(GlTextureVertexArray, self).__init__()

        if self._uv_vbo is None:
            self._create_uv_vbo()

        self._create_array(position, dimension)
        self._create_texture()

        if image is not None:
            self.set(image, integer_internal_format)

    ##############################################
    
    def __del__(self):

        #!# self._logger("Delete Texture %u" % (self._gl_textures_id))
        super(GlTextureVertexArray, self).__del__()
        GL.glDeleteTextures([self._gl_textures_id])

    ##############################################
    
    def _bind_texture(self):

        """ Bind the texture. """

        # Select the texture unit and bind it
        GL.glActiveTexture(GL.GL_TEXTURE0)
        GL.glBindTexture(GL.GL_TEXTURE_2D, self._gl_textures_id) # [0]

    ##############################################
    
    def _unbind_texture(self):

        """ Unbind the texture. """

        # Select the texture unit and unbind it
        GL.glActiveTexture(GL.GL_TEXTURE0)
        GL.glBindTexture(GL.GL_TEXTURE_2D, 0)

    ##############################################
    
    def _create_texture(self):

        """ Create the texture. """

        self._gl_textures_id = GL.glGenTextures(1, None)

        self._bind_texture()

        # Fixme:
        #  - ok?
        #  - use a sampler
        GL.glTexParameteri(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_WRAP_S, GL.GL_REPEAT) # ?
        GL.glTexParameteri(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_WRAP_T, GL.GL_REPEAT) # ?
        GL.glTexParameteri(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_MAG_FILTER, GL.GL_NEAREST) # ?
        GL.glTexParameteri(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_MIN_FILTER, GL.GL_NEAREST) # ?

        GL.glPixelStorei(GL.GL_UNPACK_ALIGNMENT, 1) # 1 means byte-alignment

        self._unbind_texture()

    ##############################################
    
    def set(self, image, integer_internal_format=False):

        """ Set the texture data.

        The parameter *image* is a Numpy array that can have up to 4 interleaved planes and of type
        uint8, int8, uint16 and int16.

        The flag *integer_internal_format* specfies if the texture uses an integer internal format.
        """

        self._bind_texture()

        if image.ndim == 2:
            height, width = image.shape
            number_of_planes = 1
        elif image.ndim == 3:
            height, width, number_of_planes = image.shape
        else:
            ValueError("Image dimension %u is not supported" % (image.ndim))

        if number_of_planes == 1:
            format_name = 'GL_RED'
        elif number_of_planes == 2:
            format_name = 'GL_RG'
        elif number_of_planes == 3:
            format_name = 'GL_RGB'
        elif number_of_planes == 4:
            format_name = 'GL_RGBA'
        else:
            raise ValueError("Image number of planes %s is not supported" % (number_of_planes))
        if integer_internal_format:
            format_name += '_INTEGER'
        data_format = getattr(GL, format_name)

        if image.dtype == np.uint8:
            data_type = GL.GL_UNSIGNED_BYTE
            if integer_internal_format:
                internal_format = GL.GL_RGBA8UI
            else: 
                internal_format = GL.GL_RGBA8
        elif image.dtype == np.uint16:
            data_type = GL.GL_UNSIGNED_SHORT
            if integer_internal_format:
                internal_format = GL.GL_RGBA16UI
            else: 
                internal_format = GL.GL_RGBA16
        elif image.dtype == np.float32:
            data_type = GL.GL_FLOAT
            internal_format = GL.GL_RGBA32F
        else:
            raise ValueError("Image data type %s is not supported" % (str(image.dtype)))

        level = 0
        border = 0
        # Fixme: check speed
        GL.glTexImage2D(GL.GL_TEXTURE_2D,
                        level, internal_format, width, height, border, data_format, data_type,
                        image)
        
        self._unbind_texture()

    ##############################################
    
    def _create_uv_vbo(self):

        """ Create the vertex array buffer for the UV texture coordinates. """

        position_uv = np.array([[0, 0],
                                [0, 1],
                                [1, 1],
                                [1, 0],
                                ],
                               dtype='f')

        self._uv_vbo = GlArrayBuffer(position_uv)

    ##############################################
    
    def _create_array(self, position, dimension):

        """ Create the vertex array buffer for the quad from a rectangle defined by its base
        position and its dimension.
        """

        vertex = np.array([[position.x, position.y],
                           [position.x, position.y + dimension.y],
                           [position.x + dimension.x, position.y + dimension.y],
                           [position.x + dimension.x, position.y],
                           ],
                          dtype='f') # dtype=np.float

        self._vertex_vbo = GlArrayBuffer(vertex)

    ##############################################
    
    def bind_to_shader(self, shader_program_interface):

        """ Bind to a shader program.

        The shader program must define a *position* vertex attribute for the quad where is mapped
        the texture, a *position_uv* vertex attribute for the UV texture coordinates and a
        *texture0* sampler uniform.
        """

        # Bind the vertex array object and record the vertex attribute bindings

        self.bind()

        shader_program_interface.position_uv.bind_to_buffer(self._uv_vbo)
        shader_program_interface.position.bind_to_buffer(self._vertex_vbo)

        # Texture unit as default
        # shader_program.uniforms.texture0 = 0

        self.unbind()

    ##############################################
    
    def draw(self):

        """ Map and paint the texture on the quad defined by the vertex array. """

        # Bind the vertex array object and the texture
        self._bind_texture()
        self.bind()
        GL.glDrawArrays(GL.GL_QUADS, 0, 4)
        self.unbind()
        self._unbind_texture()

####################################################################################################
#
# End
#
####################################################################################################
