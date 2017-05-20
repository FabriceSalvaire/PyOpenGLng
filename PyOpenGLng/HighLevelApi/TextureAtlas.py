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

import logging
import math
import sys

import numpy as np

####################################################################################################

_module_logger = logging.getLogger(__name__)

####################################################################################################

def ceil2(x):
    """ Compute the smallest power of 2 >= x """
    return int(math.pow(2, math.ceil(math.log(x, 2))))

####################################################################################################

class TextureAtlas:

    """
    Group multiple small data regions into a larger texture.

    The algorithm is based on the article by Jukka Jylänki : "A Thousand Ways to Pack the Bin - A
    Practical Approach to Two-Dimensional Rectangle Bin Packing", February 27, 2010. More precisely,
    this is an implementation of the Skyline Bottom-Left algorithm based on C++ sources provided by
    Jukka Jylänki at: http://clb.demon.fi/files/RectangleBinPack/

    Example usage::

        atlas = TextureAtlas(512,512,3)
        region = atlas.get_region(20,20)
        ...
        atlas.set_region(region, data)
    """

    _logger = _module_logger.getChild('TextureAtlas')

    ##############################################

    def __init__(self, width=1024, height=1024, depth=1):

        """
        Initialize a new atlas of given size.

        Parameters

        width : int
            Width of the underlying texture

        height : int
            Height of the underlying texture

        depth : 1 or 3
            Depth of the underlying texture
        """

        self._height = ceil2(height)
        self._width = ceil2(width)
        self._depth = depth
        if self._depth == 1: # Fixme: check?
            self._data = np.zeros((self._height, self._width), dtype=np.ubyte)
        else:
            self._data = np.zeros((self._height, self._width, self._depth), dtype=np.ubyte)
        self._nodes = [(0, 0, self._width)]
        self._used = 0 # used area

    ##############################################

    @property
    def depth(self):
        return self._depth

    @property
    def height(self):
        return self._height

    @property
    def width(self):
        return self._width

    @property
    def data(self):
        return self._data

    ##############################################

    def set_region(self, region, data):

        """
        Set a given region width provided data.

        Parameters

        region : (int,int,int,int)
            an allocated region (x,y,width,height)

        data : numpy array
            data to be copied into given region
        """

        # self._logger.debug(str(region))
        x, y, width, height = region
        if self._depth == 1: # Fixme: check?
            self._data[y:y+height, x:x+width] = data
        else:
            self._data[y:y+height, x:x+width, :] = data

    ##############################################

    def get_region(self, width, height):

        """
        Get a free region of given size and allocate it

        Parameters

        width : int
            Width of region to allocate

        height : int
            Height of region to allocate

        Return
            A newly allocated region as (x,y,width,height) or (-1,-1,0,0)
        """

        max_int = 2**32 # sys.maxint
        best_height = max_int
        best_index = -1
        best_width = max_int
        region = 0, 0, width, height

        for i in range(len(self._nodes)):
            y = self._fit(i, width, height)
            if y >= 0:
                node = self._nodes[i]
                if (y + height < best_height or
                    (y + height == best_height and node[2] < best_width)):
                    best_height = y + height
                    best_index = i
                    best_width = node[2]
                    region = node[0], y, width, height

        if best_index == -1:
            return -1, -1, 0, 0

        node = region[0], region[1] + height, width
        self._nodes.insert(best_index, node)

        i = best_index +1
        while i < len(self._nodes):
            node = self._nodes[i]
            prev_node = self._nodes[i-1]
            if node[0] < prev_node[0] + prev_node[2]:
                shrink = prev_node[0] + prev_node[2] - node[0]
                x, y, w = self._nodes[i]
                self._nodes[i] = x + shrink, y, w - shrink
                if self._nodes[i][2] <= 0:
                    del self._nodes[i]
                    i -= 1
                else:
                    break
            else:
                break
            i += 1

        self._merge()
        self._used += width * height

        return region

    ##############################################

    def _fit(self, index, width, height):

        """
        Test if region (width,height) fit into self._nodes[index]

        Parameters

        index : int
            Index of the internal node to be tested

        width : int
            Width or the region to be tested

        height : int
            Height or the region to be tested
        """

        node = self._nodes[index]
        x, y = node[0], node[1]
        width_left = width        

        if x + width > self._width:
            return -1

        i = index
        while width_left > 0:
            node = self._nodes[i]
            y = max(y, node[1])
            if y + height > self._height:
                return -1
            width_left -= node[2]
            i += 1

        return y

    ##############################################

    def _merge(self):

        """ Merge nodes """

        i = 0
        while i < len(self._nodes) -1:
            node = self._nodes[i]
            next_node = self._nodes[i+1]
            if node[1] == next_node[1]:
                self._nodes[i] = node[0], node[1], node[2] + next_node[2]
                del self._nodes[i+1]
            else:
                i += 1

    ##############################################

    def save(self, filename):

        from PIL import Image
        image = Image.fromarray(self._data)
        image.save(filename)

####################################################################################################
# 
# End
# 
####################################################################################################
