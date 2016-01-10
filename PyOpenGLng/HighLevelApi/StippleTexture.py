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

""" This modules provides tools to manage stipple texture. """

####################################################################################################

import numpy as np

####################################################################################################

from . import GL

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

        self._gl_textures_id = GL.glGenTextures(1)

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
        for i in range(width):
            if stipple_pattern & (1 << i):
                value = 0xFF
            else:
                value = 0
            stipple_pattern_image[i] = value

        self.bind()

        level = 0
        border = 0
        internal_format = GL.GL_LUMINANCE #compat#
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
