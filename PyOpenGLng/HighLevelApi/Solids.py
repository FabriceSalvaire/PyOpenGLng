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

####################################################################################################

# sphere radius
# cylinder

####################################################################################################

def norm(x):
    # Fixme: faster method ?
    v = np.sqrt(np.sum(x**2, axis=1))
    v.shape = x.shape[0], 1
    return v

####################################################################################################

def unit_cube():

    # near plan   far plan
    #   4 8         3 7
    #   2 6         1 5
    
    position1 = (-1, -1, -1)
    position2 = (-1, -1,  1)
    position3 = (-1,  1, -1)
    position4 = (-1,  1,  1)
    position5 = ( 1, -1, -1)
    position6 = ( 1, -1,  1)
    position7 = ( 1,  1, -1)
    position8 = ( 1,  1,  1)

    # positions = np.array([position1, position2, position4,  # left
    #                       position7, position1, position3,  # far
    #                       position6, position1, position5,  # bottom
    #                       position7, position5, position1,  # far
    #                       position1, position4, position3,  # left
    #                       position6, position2, position1,  # bottom
    #                       position4, position2, position6,  # near
    #                       position8, position5, position7,  # right
    #                       position5, position8, position6,  # right
    #                       position8, position7, position3,  # top
    #                       position8, position3, position4,  # top
    #                       position8, position4, position6], # near
    #                      dtype=np.float32)

    positions = np.array([
        position1, position2, position4,  # left
        position1, position4, position3,  # left
        position5, position8, position6,  # right
        position8, position5, position7,  # right
        position6, position1, position5,  # bottom
        position6, position2, position1,  # bottom
        position8, position3, position4,  # top
        position8, position7, position3,  # top
        position7, position1, position3,  # far
        position7, position5, position1,  # far
        position4, position2, position6,  # near
        position8, position4, position6], # near
                         dtype=np.float32)


    # (V{i+1} - Vi)x(V{i+2} - V{i+1})
    vertex1 = positions[::3]
    vertex2 = positions[1::3]
    vertex3 = positions[2::3]
    vector1 = vertex2 - vertex1
    vector2 = vertex3 - vertex2
    normals = np.cross(vector1, vector2, axisa=-1, axisb=-1, axisc=-1)
    normals /= norm(normals)

    return positions, normals

####################################################################################################

def cube(width, height, depth):

    # Fixme: scale!

    positions, normals = unit_cube()

    colour2 = (1, 0, 0, 1)
    colour4 = (1, 0, 0, 1)
    colour8 = (1, 0, 0, 1)
    colour6 = (1, 0, 0, 1)
    
    colour1 = (0, 1, 0, 1)
    colour3 = (0, 1, 0, 1)
    colour7 = (0, 1, 0, 1)
    colour5 = (0, 1, 0, 1)

    colours = np.array([
        colour1, colour2, colour4,  # left
        colour1, colour4, colour3,  # left
        colour5, colour8, colour6,  # right
        colour8, colour5, colour7,  # right
        colour6, colour1, colour5,  # bottom
        colour6, colour2, colour1,  # bottom
        colour8, colour3, colour4,  # top
        colour8, colour7, colour3,  # top
        colour7, colour1, colour3,  # far
        colour7, colour5, colour1,  # far
        colour4, colour2, colour6,  # near
        colour8, colour4, colour6], # near
                         dtype=np.float32)
    
    return TriangleVertexArray((positions, normals, colours))

####################################################################################################
#
# End
#
####################################################################################################
