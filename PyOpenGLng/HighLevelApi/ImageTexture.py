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
# - 28/01/2014 Fabrice
#   - should be used by TextureVertexArray
#   - complete format etc.
#
####################################################################################################

""" This modules provides tools to manage texture. """

####################################################################################################

import logging

import numpy as np

####################################################################################################

from . import GL

####################################################################################################

_module_logger = logging.getLogger(__name__)

####################################################################################################

class ImageTexture(object):

    _logger = _module_logger.getChild('ImageTexture')

    ##############################################
    
    def __init__(self, image):

        self._create_texture()
        self._shape = None
        self.set(image)

    ##############################################
    
    def __del__(self):

        GL.glDeleteTextures([self._gl_textures_id])

    ##############################################
    
    def bind(self):

        """ Bind the texture. """

        # Select the texture unit and bind it
        GL.glActiveTexture(GL.GL_TEXTURE0)
        GL.glBindTexture(GL.GL_TEXTURE_2D, self._gl_textures_id) # [0]

    ##############################################
    
    def unbind(self):

        """ Unbind the texture. """

        # Select the texture unit and unbind it
        GL.glActiveTexture(GL.GL_TEXTURE0)
        GL.glBindTexture(GL.GL_TEXTURE_2D, 0)

    ##############################################
    
    def _create_texture(self):

        """ Create the texture. """

        self._gl_textures_id = GL.glGenTextures(1)

        self.bind()

        GL.glTexParameteri(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_WRAP_S, GL.GL_CLAMP)
        GL.glTexParameteri(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_WRAP_T, GL.GL_CLAMP)
        GL.glTexParameteri(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_MAG_FILTER, GL.GL_LINEAR)
        GL.glTexParameteri(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_MIN_FILTER, GL.GL_LINEAR)

        # Fixme: required?
        GL.glPixelStorei(GL.GL_UNPACK_ALIGNMENT, 1) # 1 means byte-alignment

        self.unbind()

    ##############################################

    @property
    def shape(self):
        return self._shape

    ##############################################
    
    def set(self, image):

        shape = image.shape
        height, width = shape[:2]
        self._shape = height, width
        if len(shape) == 3:
            depth = shape[2]
        else:
            depth = 1

        if depth == 1:
            internal_format = data_format = GL.GL_ALPHA
        else:
            internal_format = data_format = GL.GL_RGB

        level = 0
        border = 0

        if image.dtype == np.uint8:
            data_type = GL.GL_UNSIGNED_BYTE
        else:
            raise NotImplementedError

        self.bind()
        GL.glTexImage2D(GL.GL_TEXTURE_2D,
                        level, internal_format, width, height, border, data_format, data_type,
                        image)
        self.unbind()

####################################################################################################
#
# End
#
####################################################################################################
