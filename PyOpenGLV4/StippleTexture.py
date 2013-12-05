####################################################################################################
#
# PyOpenGLV4 - An OpenGL V4 layer on top of PyOpengl.
# Copyright (C) 2013 Salvaire Fabrice
#
####################################################################################################

""" This modules provides tools to manage stipple texture. """

####################################################################################################

import numpy as np

import OpenGL.GL as GL

####################################################################################################

class GlStippleTexture(object):

    """ This class defines a 1D stipple texture. """

    ##############################################
    
    def __init__(self, stipple_pattern):

        self._create_texture()

        if stipple_pattern is not None:
            self.set(stipple_pattern)

    ##############################################
    
    def __del__(self):

        GL.glDeleteTextures([self._gl_textures_id])

    ##############################################
    
    def bind(self):

        """ Bind the texture. """

        GL.glActiveTexture(GL.GL_TEXTURE0) # Fixme: check ?
        GL.glBindTexture(GL.GL_TEXTURE_1D, self._gl_textures_id) # [0]

    ##############################################
    
    def unbind(self):

        """ Unbind the texture. """

        GL.glActiveTexture(GL.GL_TEXTURE0)
        GL.glBindTexture(GL.GL_TEXTURE_1D, 0)

    ##############################################
    
    def _create_texture(self):

        """ Create the texture. """

        self._gl_textures_id = GL.glGenTextures(1, None)

        self.bind()

        GL.glTexParameteri(GL.GL_TEXTURE_1D, GL.GL_TEXTURE_MAG_FILTER, GL.GL_NEAREST) # ?
        GL.glTexParameteri(GL.GL_TEXTURE_1D, GL.GL_TEXTURE_MIN_FILTER, GL.GL_NEAREST) # ?

        self.unbind()

    ##############################################
    
    def set(self, stipple_pattern):

        """ Set the stipple pattern.

        The stipple pattern is provided as a 16-bit number that define a 16-pixel binary 1D
        texture.

        For example 0xFF00 defines a dash pattern and 0xAAAA defines a dotted pattern.
        """

        width = 16

        stipple_pattern_image = np.zeros((width), dtype=np.uint8)
        for i in xrange(width):
            if stipple_pattern & (1 << i):
                value = 0xFF
            else:
                value = 0
            stipple_pattern_image[i] = value
 
        self.bind()

        level = 0
        border = 0
        internal_format = GL.GL_LUMINANCE
        data_format = GL.GL_LUMINANCE
        data_type = GL.GL_UNSIGNED_BYTE
        GL.glTexImage1D(GL.GL_TEXTURE_1D,
                        level, internal_format, width, border, data_format, data_type,
                        stipple_pattern_image)

        self.unbind()

####################################################################################################
#
# End
#
####################################################################################################
