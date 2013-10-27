####################################################################################################
# 
# PyOpenGLV4 - An OpenGL V4 layer on top of PyOpengl.
# Copyright (C) 2013 Salvaire Fabrice
# 
####################################################################################################

""" This modules provides tools to manage random texture. """

####################################################################################################

import logging

import numpy as np

import OpenGL
import OpenGL.GL as GL
# Fix: define GL_R32F cf. /usr/include/GL/glext.h
GL.GL_R32F = OpenGL.constant.Constant('GL_R32F', 0x822E)

####################################################################################################

from .GlShader import GlShaderProgram

####################################################################################################

class GlRandomTexture(object):

    """ This class defines a 1D random texture. """

    ##############################################
    
    def __init__(self, size, texture_unit):

        self._texture_unit_number = texture_unit
        self._texture_unit = getattr(GL, 'GL_TEXTURE' + str(texture_unit))
        self._create_texture()
        self._set(size)

    ##############################################
    
    @property
    def texture_unit_number(self):
        return self._texture_unit_number

    ##############################################
    
    def __del__(self):

        GL.glDeleteTextures([self._gl_textures_id])

    ##############################################
    
    def bind(self):

        """ Bind the texture. """

        GL.glActiveTexture(self._texture_unit) # Fixme: check ?
        GL.glBindTexture(GL.GL_TEXTURE_1D, self._gl_textures_id) # [0]

    ##############################################
    
    def unbind(self):

        """ Unbind the texture. """

        GL.glActiveTexture(self._texture_unit)
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
    
    def _set(self, width):

        random_image = np.random.rand(width)

        self.bind()

        level = 0
        border = 0
        internal_format = GL.GL_R32F
        data_format = GL.GL_RED
        data_type = GL.GL_FLOAT
        GL.glTexImage1D(GL.GL_TEXTURE_1D,
                        level, internal_format, width, border, data_format, data_type,
                        random_image)

        self.unbind()

####################################################################################################

class GlRandomTextureShaderProgram(GlShaderProgram):

    _logger = logging.getLogger(__name__)

    ##############################################
    
    def __init__(self, program_name, random_texture):

        super(GlRandomTextureShaderProgram, self).__init__(program_name)

        self._random_texture = random_texture

    ##############################################
    
    def link(self):

        # Fixme: should use GlShaderProgramInterface ?
        super(GlRandomTextureShaderProgram, self).link()
        self.uniforms.random_label_texture = self._random_texture.texture_unit_number

    ##############################################
    
    def unbind(self):

        """ Unbind the shader. """

        self._random_texture.unbind()
        super(GlRandomTextureShaderProgram, self).unbind()

    ##############################################
    
    def bind(self):

        """ Bind the shader. """

        super(GlRandomTextureShaderProgram, self).bind()
        self._random_texture.bind()

####################################################################################################
#
# End
#
####################################################################################################
