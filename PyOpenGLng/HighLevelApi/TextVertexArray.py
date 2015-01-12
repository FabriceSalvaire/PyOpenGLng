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
# This source code is derived from:
#
#   Nicolas P. Rougier, Higher Quality 2D Text Rendering,
#   Journal of Computer Graphics Techniques (JCGT), vol. 2, no. 1, 50-64, 2013.
#   Available online http://jcgt.org/published/0002/01/04/1
#
#  Copyright 2011 Nicolas P. Rougier
#  Distributed under the terms of the new BSD license.
#
####################################################################################################

""" This modules provides tools to manage text. """

####################################################################################################

import logging

import numpy as np

####################################################################################################

from . import GL
from .TextureFont import from_64th_point
from .Buffer import GlArrayBuffer
from .VertexArrayObject import GlVertexArrayObject

####################################################################################################

_module_logger = logging.getLogger(__name__)

####################################################################################################

class TextVertexArray(GlVertexArrayObject):

    """ This class wraps a Text Vertex Array. """

    _logger = _module_logger.getChild('TextVertexArray')

    _uv_vbo = None

    ##############################################
    
    def __init__(self, image_texture):

        super(TextVertexArray, self).__init__()

        self._image_texture = image_texture # Fixme: could contains several font and size
        self._font_atlas_shape = image_texture.shape

        self._number_of_vertexes = 0
        self._vertexes, self._glyph_sizes, self._texture_coordinates, self._colours = self._create_arrays(0)

    ##############################################
    
    def _create_arrays(self, number_of_vertexes):

        vertexes = np.zeros((number_of_vertexes, 4), dtype=np.float32)
        glyph_sizes = np.zeros((number_of_vertexes, 2), dtype=np.float32)
        texture_coordinates = np.zeros((number_of_vertexes, 2), dtype=np.float32)
        colours = np.zeros((number_of_vertexes, 4), dtype=np.float32)

        return vertexes, glyph_sizes, texture_coordinates, colours

    ##############################################
    
    def add(self, text, font_size,
            colour=(1.0, 1.0, 1.0, 1.0),
            x=0, y=0,
            anchor_x='left', anchor_y='baseline',
            ):

        if not text:
            return

        # Compute glyph vertexes 

        font = font_size.font

        number_of_glyphs = len(text)
        number_of_vertexes = number_of_glyphs
        vertexes, glyph_sizes, texture_coordinates, colours = self._create_arrays(number_of_vertexes)

        pen = [x, y]
        prev = None

        for i, charcode in enumerate(text):
            glyph = font_size[charcode]
            kerning = glyph.get_kerning(prev)

            x0 = pen[0] + glyph.offset[0] + kerning
            dx = x0 - int(x0) # fractional part of x0
            x0 = int(x0)
            y0 = pen[1] + glyph.offset[1]
            # x1 = x0 + glyph.size[0]
            # y1 = y0 - glyph.size[1]
            u0, v0, u1, v1 = glyph.texture_coordinates

            vertexes[i] = (x, y, x0 - x, y0 - y)
            glyph_sizes[i] = glyph.size
            texture_coordinates[i] = (u0, v0)
            colours[i] = colour

            pen[0] = pen[0] + from_64th_point(glyph.advance[0]) + kerning
            pen[1] = pen[1] + from_64th_point(glyph.advance[1])

            prev = charcode

        # Correct width for last glyph
        width = pen[0] - glyph.advance[0]/64.0 + glyph.size[0]

        if anchor_y == 'top':
            dy = -round(font_size.metrics.ascender)
        elif anchor_y == 'center':
            dy = +round(-font_size.metrics.height/2 - font_size.metrics.descender)
        elif anchor_y == 'bottom':
            dy = -round(font_size.metrics.descender)
        else:
            dy = 0

        if anchor_x == 'right':
            dx = -width
        elif anchor_x == 'center':
            dx = -width / 2.
        else:
            dx = 0

        # Block position
        vertexes[:,:2] += (round(dx), round(dy))

        # Concatenate the vertexes
        self._number_of_vertexes += number_of_vertexes
        self._vertexes = np.concatenate((self._vertexes, vertexes))
        self._glyph_sizes = np.concatenate((self._glyph_sizes, glyph_sizes))
        self._texture_coordinates = np.concatenate((self._texture_coordinates, texture_coordinates))
        # self._horizontal_offsets = np.concatenate((self._horizontal_offsets, horizontal_offsets))
        self._colours = np.concatenate((self._colours, colours))

    ##############################################
    
    def __del__(self):

        self._logger.debug('')
        super(TextVertexArray, self).__del__()

    ##############################################
    
    def upload(self):

        # Create VBO
        # self._logger.debug(str(self._vertexes))
        self._vertexes_vbo = GlArrayBuffer(self._vertexes)
        self._glyph_sizes_vbo = GlArrayBuffer(self._glyph_sizes)
        self._texture_coordinates_vbo = GlArrayBuffer(self._texture_coordinates)
        self._colours_vbo = GlArrayBuffer(self._colours)

    ##############################################
    
    def bind_to_shader(self, shader_program_interface):

        self.bind()

        shader_program_interface.position.bind_to_buffer(self._vertexes_vbo) # self._vertex_vbo
        shader_program_interface.glyph_size.bind_to_buffer(self._glyph_sizes_vbo)
        shader_program_interface.position_uv.bind_to_buffer(self._texture_coordinates_vbo) # self._uv_vbo
        shader_program_interface.colour.bind_to_buffer(self._colours_vbo)

        # Texture unit as default
        # shader_program.uniforms.texture0 = 0

        self.unbind()

    ##############################################
    
    def draw(self, shader_program):

        GL.glEnable(GL.GL_BLEND)
        # Blending: O = Sf*S + Df*D
        # alpha: 0: complete transparency, 1: complete opacity
        # Set (Sf, Df) for transparency: O = Sa*S + (1-Sa)*D 
        # GL.glBlendEquation(GL.GL_FUNC_ADD)
        GL.glBlendFunc(GL.GL_SRC_ALPHA, GL.GL_ONE_MINUS_SRC_ALPHA)

        shader_program.bind()
        self._image_texture.bind()
        self.bind()

        shader_program.uniforms.font_atlas = 0
        shader_program.uniforms.font_atlas_shape = self._font_atlas_shape
        shader_program.uniforms.gamma = 1.

        GL.glDrawArrays(GL.GL_POINTS, 0, self._number_of_vertexes)

        self.unbind()
        self._image_texture.unbind()
        shader_program.unbind()

        GL.glDisable(GL.GL_BLEND)

####################################################################################################
# 
# End
# 
####################################################################################################
