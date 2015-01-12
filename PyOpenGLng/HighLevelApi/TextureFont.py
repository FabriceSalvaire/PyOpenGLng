# -*- coding: utf-8 -*-

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

####################################################################################################
#
#                                              Audit
#
# - 30/01/2014 Fabrice
#  - update doc
#  - pass atlas as parameter
#  - compute atlas size
#  - add SDF
#  - texture coordinate vs atlas coordinate
#
####################################################################################################

####################################################################################################

""" Texture font class """

####################################################################################################

import six

####################################################################################################

import logging
import string
import unicodedata

import numpy as np
import freetype

####################################################################################################

from .TextureAtlas import TextureAtlas

####################################################################################################

_module_logger = logging.getLogger(__name__)

####################################################################################################

def from_64th_point(x):
    return x/64.

def to_64th_point(x):
    return x*64

####################################################################################################

def test_bit(flags, mask):
    return flags & mask == 1

####################################################################################################

class TextureFont(object):

    """
    A texture font gathers a set of glyph relatively to a given font filename and size.

    Points are a physical unit, where 1 point equals 1/72th of an inch. The size in pixel of a glyph
    is thus size_in_point * resolution_in_dpi / 72.
    """

    _logger = _module_logger.getChild('TextureFont')

    ##############################################

    def __init__(self, font_path):

        self._font_path = font_path

        # Fixme: an atlas could be shared by several fonts and sizes
        atlas_size = 1024
        self._atlas = TextureAtlas(atlas_size, atlas_size, depth=3)
        self._dirty = False

        self._face = freetype.Face(self._font_path)
        self._face.select_charmap(freetype.FT_ENCODING_UNICODE)

        self._font_size = {}

    ##############################################

    @property
    def atlas(self):
        return self._atlas

    ##############################################

    def __getitem__(self, font_size):

        if font_size not in self._font_size:
            self._font_size[font_size] = TextureFontSize(self, font_size)
        return self._font_size[font_size]

    ##############################################

    def _dump_face_info(self):

        face = self._face

        string_template = """
postscript name:     %s
family name:         %s
style name:          %s
number of faces:     %u
number of glyphs:    %u
available sizes:     %s
char maps:           %s
units per em:        %s
flags:               %s
bold:                %s
italic:              %s
scalable:            %s
ascender:            %u
descender:           %u
height:              %u
max advance width:   %u
max advance height:  %u
underline position:  %u
underline thickness: %u
has horizontal:      %s
has vertical:        %s
has kerning:         %s
is fixed width:      %s
is scalable:         %s
"""

        six.print_(string_template % (
            face.postscript_name,
            face.family_name,
            face.style_name,
            face.num_faces,
            face.num_glyphs,
            str(face.available_sizes),
            str([charmap.encoding_name for charmap in face.charmaps]),
            hex(face.style_flags),
            face.units_per_EM,
            test_bit(face.style_flags, freetype.FT_STYLE_FLAG_BOLD),
            test_bit(face.style_flags, freetype.FT_STYLE_FLAG_ITALIC),
            test_bit(face.style_flags, freetype.FT_FACE_FLAG_SCALABLE),
            face.ascender,
            face.descender,
            face.height,
            face.max_advance_width,
            face.max_advance_height,
            face.underline_position,
            face.underline_thickness,
            face.has_horizontal,
            face.has_vertical,
            face.has_kerning,
            face.is_fixed_width,
            face.is_scalable,
            ))

        six.print_("Glyph Table:")
        charcode, glyph_index = face.get_first_char()
        while glyph_index:
            six.print_("  [%d] 0x%04lx %s %s" % (glyph_index,
                                                 charcode,
                                                 unichr(charcode),
                                                 unicodedata.name(unichr(charcode))))
            # face.get_glyph_name(glyph_index) # is not available
            charcode, glyph_index = face.get_next_char(charcode, glyph_index)

####################################################################################################

class TextureFontSize(object):

    ##############################################

    def __init__(self, texture_font, font_size):

        self._font = texture_font
        self._size = font_size

        self._metrics = FontMetrics(self)
        self._glyphs = {}

    ##############################################

    @property
    def font(self):
        return self._font

    @property
    def size(self):
        return self._size

    @property
    def metrics(self):
        return self._metrics

    ##############################################

    def __getitem__(self, charcode):

        if charcode not in self._glyphs:
            self.load_glyph('%c' % charcode) # Fixme: %c ?
        return self._glyphs[charcode]

    ##############################################

    def load_all_glyphs(self):

        # self.load_from_string(string.printable)

        face = self._font._face
        charcode, glyph_index = face.get_first_char()
        while glyph_index:
            self.load_glyph(six.unichr(charcode))
            charcode, glyph_index = face.get_next_char(charcode, glyph_index)

    ##############################################
 
    def load_from_string(self, charcodes):

        for charcode in charcodes:
            self.load_glyph(charcode)

    ##############################################
 
    def _set_face_transfrom(self):

        face = self._font._face
        horizontal_scale = 100
        resolution = 72 # dpi
        face.set_char_size(int(to_64th_point(self._size)), 0,
                           horizontal_scale*resolution, resolution)
        # Matrix cooeficients are expressed in 16.16 fixed-point units.
        # 2**16 = 0x10000L = 65536
        matrix = freetype.Matrix(int(2**16/horizontal_scale), 0,
                                 0, 2**16)
        # The vector coordinates are expressed in 1/64th of a pixel
        # (also known as 26.6 fixed-point numbers).
        delta = freetype.Vector(0, 0)
        face.set_transform(matrix, delta)

        freetype.set_lcd_filter(freetype.FT_LCD_FILTER_LIGHT)

    ##############################################
 
    def load_glyph(self, charcode):

        if charcode in self._glyphs:
            return

        self._set_face_transfrom()

        self.dirty = True

        face = self._font._face
        atlas = self._font._atlas

        flags = freetype.FT_LOAD_RENDER | freetype.FT_LOAD_FORCE_AUTOHINT
        if atlas.depth == 3:
            flags |= freetype.FT_LOAD_TARGET_LCD

        face.load_char(charcode, flags)
        # face.load_glyph(glyph_index, flags) # Fixme: index using charcode

        bitmap = face.glyph.bitmap # a list
        left = face.glyph.bitmap_left
        top = face.glyph.bitmap_top
        width = face.glyph.bitmap.width
        rows = face.glyph.bitmap.rows
        pitch = face.glyph.bitmap.pitch # stride / number of bytes taken by one bitmap row

        # Glyphes are separated by a margin
        # margin = 1 # px
        # dimension are given in pixel thus we correct the bitmap width
        x, y, w, h = atlas.get_region(width/atlas.depth +2, rows +2)
        if x == -1:
            raise NameError("Cannot allocate glyph in atlas")
        x, y = x+1, y+1
        w, h = w-2, h-2 # = width/depth, rows

        # Remove padding
        data = np.array(bitmap.buffer).reshape(rows, pitch)
        data = data[:,:width].astype(np.ubyte)
        data = data.reshape(rows, width/atlas.depth, atlas.depth)
        
        # Gamma correction
        # gamma = 1.5
        # Z = (data/255.0)**gamma
        # data = Z*255

        atlas.set_region((x, y, w, h), data)

        # Compute texture coordinates
        u0 = x / float(atlas.width)
        v0 = y / float(atlas.height)
        u1 = (x + w) / float(atlas.width)
        v1 = (y + h) / float(atlas.height)
        texture_coordinate = (u0, v0, u1, v1)

        # Build glyph
        size = w, h
        offset = left, top
        advance = face.glyph.advance.x, face.glyph.advance.y
        glyph = TextureGlyph(charcode, size, offset, advance, texture_coordinate)
        self._glyphs[charcode] = glyph

        # Generate kerning
        # Fixme: exhaustive?
        for glyph2 in self._glyphs.values():
            self._set_kerning(glyph, glyph2)
            self._set_kerning(glyph2, glyph)

    ##############################################

    def _set_kerning(self, glyph1, glyph2):

        charcode1 = glyph1.charcode
        charcode2 = glyph2.charcode
        face = self._font._face
        kerning = face.get_kerning(charcode2, charcode1, mode=freetype.FT_KERNING_UNFITTED)
        if kerning.x != 0:
            # 64 * 64 because of 26.6 encoding AND the transform matrix
            glyph1._kerning[charcode2] = kerning.x / float(64**2)

####################################################################################################

class FontMetrics(object):

    ##############################################

    def __init__(self, texture_font_size):

        face = texture_font_size._font._face
        face.set_char_size(int(to_64th_point(texture_font_size.size)))
        metrics = face.size

        self.ascender = from_64th_point(metrics.ascender)
        self.descender = from_64th_point(metrics.descender)
        self.height = from_64th_point(metrics.height)
        self.linegap = self.height - self.ascender + self.descender # Fixme: check

####################################################################################################

class TextureGlyph(object):

    """
    A texture glyph gathers information relative to the size/offset/advance and texture coordinates
    of a single character. It is generally built automatically by a TextureFont.
    """

    def __init__(self, charcode, size, offset, advance, texture_coordinates):

        """
        Build a new texture glyph

        Parameter:

        charcode : char
            Represented character

        size: tuple of 2 ints
            Glyph size in pixels

        offset: tuple of 2 floats
            Glyph offset relatively to anchor point

        advance: tuple of 2 floats
            Glyph advance

        texture_coordinates: tuple of 4 floats
            Texture coordinates of bottom-left and top-right corner
        """

        self.charcode = charcode
        self.size = size
        self.offset = offset
        self.advance = advance
        self.texture_coordinates = texture_coordinates

        self._kerning = {}

    ##############################################

    def get_kerning(self, charcode):

        """ Get kerning information

        Parameters:

        charcode: char
            Character preceding this glyph
        """

        return self._kerning.get(charcode, 0)

####################################################################################################
# 
# End
# 
####################################################################################################
