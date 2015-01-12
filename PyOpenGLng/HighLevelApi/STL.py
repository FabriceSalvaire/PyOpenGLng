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

import six
from six.moves import xrange

####################################################################################################

import mmap
import struct

import numpy as np

####################################################################################################

from .PrimitiveVertexArray import TriangleVertexArray
from PyOpenGLng.Tools.EnumFactory import EnumFactory

####################################################################################################

class StlParser(object):

    stl_parser_state = EnumFactory('StlParserState',
                                   ('start', 'in_solide', 'in_facet', 'in_loop', 'stop'))

    ##############################################

    def __init__(self, path):

        with(open(path, 'r')) as file_handle:
            stream = mmap.mmap(file_handle.fileno(), length=0, access=mmap.ACCESS_READ)
            text_stl = stream.read(6) == 'solid '
            stream.seek(0)
            if text_stl:
                self._read_text(file_handle)
            else:
                self._read_binary(file_handle, stream)

    ##############################################

    def _read_text(self, file_handle):

        # solid OpenSCAD_Model
        #   facet normal -1 0 0
        #     outer loop
        #       vertex 0 0 1
        #       vertex 0 1 1
        #       vertex 0 0 0
        #     endloop
        #   endfacet
        #   ...
        # endsolid OpenSCAD_Model

        vertexes = []
        normals = []
        states = self.stl_parser_state
        state = states.start
        normal = None
        for line in file_handle:
            line = line.strip()
            if (state == states.start and line.startswith('solid ')):
                self.name = line[len('solid '):]
                state = states.in_solide
            elif (state == states.in_solide and line.startswith('facet normal ')):
                state = states.in_facet
                normal = line[len('facet normal '):].split() # Fixme: better ...
                normal = [float(x) for x in normal]
            elif (state == states.in_facet and line.startswith('outer loop')):
                state = states.in_loop
            elif (state == states.in_loop and line.startswith('vertex ')):
                vertex = line[len('vertex '):].split()
                vertex = [float(x) for x in vertex]
                vertexes.append(vertex)
            elif (state == states.in_loop and line.startswith('endloop')):
                state = states.in_facet
            elif (state == states.in_facet and line.startswith('endfacet')):
                state = states.in_solide
                normals.append(normal)
            elif (state == states.in_solide and line.startswith('endsolid')):
                state = states.stop
            else:
                raise NameError("Bad STL file")

        self.positions = np.array(vertexes, dtype=np.float32)
        self.normals = np.zeros(self.positions.shape, dtype=np.float32)
        normals = np.array(normals, dtype=np.float32)
        self.normals[0::3] = normals
        self.normals[1::3] = normals
        self.normals[2::3] = normals

    ##############################################

    def _read_binary(self, file_handle, stream):

        header = stream.read(80)
        number_of_triangles = struct.unpack('<I', stream.read(4))[0]
        six.print_(number_of_triangles)

        positions = np.zeros((3*number_of_triangles, 3), dtype=np.float32)
        normals = np.zeros(positions.shape, dtype=np.float32)

        for i in xrange(number_of_triangles):
            j = 3*i
            normals[j:j+3] = struct.unpack('<fff', stream.read(12))
            for k in xrange(3):
                positions[j+k] = struct.unpack('<fff', stream.read(12))
            stream.read(2)
            # struct.unpack('<H', stream.read(2))
        # stream.seek(84)

        # Center the solid
        for i in xrange(3):
            positions[:,i] -= .5*(positions[:,i].max() + positions[:,i].min())
        six.print_(positions[:,0].min(), positions[:,1].min(), positions[:,2].min())
        six.print_(positions[:,0].max(), positions[:,1].max(), positions[:,2].max())

        # normal, 3 vertex
        # dtype = np.dtype('12<f4, <u2')
        # data = np.memmap(file_handle, mode='r', dtype=dtype, shape=number_of_triangles)
        # six.print_(data[0])

        self.positions = positions
        self.normals = normals

    ##############################################

    def to_vertex_array(self):

        # Fixme: here ?

        colour = (1, 0, 0, 1)
        self.colours = np.zeros((self.positions.shape[0], 4), dtype=np.float32)
        self.colours[...] = colour

        return TriangleVertexArray((self.positions, self.normals, self.colours))

####################################################################################################
# 
# End
# 
####################################################################################################
