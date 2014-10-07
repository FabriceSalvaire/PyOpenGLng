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

        with(open(path, 'r')) as f:
            self._read(f)

    ##############################################

    def _read(self, file_handle):

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
                for i in xrange(3):
                    normals.append(normal)
            elif (state == states.in_solide and line.startswith('endsolid')):
                state = states.stop
            else:
                raise NameError("Bad STL file")

        self.positions = np.array(vertexes, dtype=np.float32)
        self.positions /= 3
        self.normals = np.array(normals, dtype=np.float32)

        colour = (1, 0, 0, 1)
        self.colours = np.zeros((self.positions.shape[0], 4), dtype=np.float32)
        self.colours[...] = colour

    ##############################################

    def to_vertex_array(self):

        # Fixme: here ?

        return TriangleVertexArray((self.positions, self.normals, self.colours))

####################################################################################################
# 
# End
# 
####################################################################################################
