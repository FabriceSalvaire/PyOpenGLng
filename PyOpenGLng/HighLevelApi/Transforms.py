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

# Note: we use functions (e.g. sin) from math module because they are faster

####################################################################################################

import math
import numpy as np

####################################################################################################

def identity():
    return np.identity(4, dtype=np.float32)

####################################################################################################

def translate(matrix, x, y, z):

    """ in-place translation """

    T = np.array([[1., 0., 0., x],
                  [0., 1., 0., y],
                  [0., 0., 1., z],
                  [0., 0., 0., 1.]],
                 dtype=matrix.dtype)

    matrix[...] = np.dot(matrix, T)
    return matrix

####################################################################################################

def scale(matrix, x, y, z):

    S = np.array([[ x, 0., 0., 0.],
                  [0.,  y, 0., 0.],
                  [0., 0.,  z, 0.],
                  [0., 0., 0., 1.]],
                 dtype=matrix.dtype)

    matrix[...] = np.dot(matrix, S)
    return matrix

####################################################################################################

def rotate_x(matrix, theta):

    t = math.radians(theta)
    c = math.cos(t)
    s = math.sin(t)
    R = np.array([[1., 0., 0., 0.],
                  [0.,  c, -s, 0.],
                  [0.,  s,  c, 0.],
                  [0., 0., 0., 1.]],
                 dtype=matrix.dtype)

    matrix[...] = np.dot(matrix, R)
    return matrix

####################################################################################################

def rotate_y(matrix, theta):

    t = math.radians(theta)
    c = math.cos(t)
    s = math.sin(t)
    R = np.array([[ c, 0.,  s, 0.],
                  [0., 1., 0., 0.],
                  [-s, 0.,  c, 0.],
                  [0., 0., 0., 1.]],
                 dtype=matrix.dtype)

    matrix[...] = np.dot(matrix, R)
    return matrix

####################################################################################################

def rotate_z(matrix, theta):

    t= math.radians(theta)
    c = math.cos(t)
    s = math.sin(t)
    R = np.array([[ c, -s, 0., 0.],
                  [ s,  c, 0., 0.],
                  [0., 0., 1., 0.],
                  [0., 0., 0., 1.]],
                 dtype=matrix.dtype)

    matrix[...] = np.dot(matrix, R)
    return matrix

####################################################################################################

def rotate(matrix, x, y, z, angle):

    # R = I + sS + (1-c)S**2
    # S = [[ 0, -z,  y],
    #      [ z,  0, -x],
    #      [-y,  x,  0]]

    t = math.radians(angle)
    c = math.cos(t)
    s = math.sin(t)

    n = math.sqrt(x**2 + y**2 + z**2)
    x /= n
    y /= n
    z /= n
    one_minus_c = 1 - c
    cx = one_minus_c * x
    cy = one_minus_c * y
    cz = one_minus_c * z
    sx = s * x
    sy = s * y
    sz = s * z

    R = np.array([[cx*x + c,  cy*x - sz, cz*x + sy, 0],
                  [cx*y + sz, cy*y + c,  cz*y - sx, 0],
                  [cx*z - sy, cy*z + sx, cz*z + c,  0],
                  [0, 0, 0, 1]],
                 dtype=matrix.dtype)

    matrix[...] = np.dot(matrix, R)
    return matrix

####################################################################################################

def ortho(left, right, bottom, top, near, far):

    """
    left, right
      Specify the coordinates for the left and right vertical clipping planes.

    bottom, top
      Specify the coordinates for the bottom and top horizontal clipping planes.

    near, far
      Specify the distances to the nearer and farther depth clipping planes.
      These values are negative if the plane is to be behind the viewer.
    """            

    # vertex1 = np.array([[left], [bottom], [far]])
    # vertex2 = np.array([[right], [top], [near]])
    # scale = 2. / (vertex2 - vertex1)
    # offset = (vertex2 + vertex1)/(vertex2 - vertex1)
    # matrix = np.array([[ scale[0], 0.,       0.,       -offset[0] ],
    #                    [ 0.,       scale[1], 0.,       -offset[1] ],
    #                    [ 0.,       0.,       scale[2],  offset[2] ],
    #                    [ 0.,       0.,       0.,       1. ]],
    #                   dtype=np.float32)

    dx = float(right - left)
    dy = float(top - bottom)
    dz = float(near - far)

    matrix = np.zeros((4, 4), dtype=np.float32)
    matrix[0, 0] = 2. / dx
    matrix[1, 1] = 2. / dy
    matrix[2, 2] = 2. / dz
    matrix[0, 3] = - (left + right) / dx
    matrix[1, 3] = - (bottom + top) / dy
    matrix[2, 3] = (near + far) / dz
    matrix[3, 3] = 1.

    return matrix

####################################################################################################

def frustum(left, right, bottom, top, near, far):

    """
    left, right
      Specify the coordinates for the left and right vertical clipping planes.

    bottom, top
      Specify the coordinates for the bottom and top horizontal clipping planes.
      
    near, far
      Specify the distances to the near and far depth clipping planes.
      Both distances must be positive.
    """

    dx = float(right - left)
    dy = float(top - bottom)
    dz = float(near - far)

    matrix = np.zeros((4, 4), dtype=np.float32)
    matrix[0, 0] = 2. * near / dx
    matrix[1, 1] = 2. * near / dy
    matrix[0, 2] = (right + left) / dx
    matrix[1, 2] = (top + bottom) / dy
    matrix[2, 2] = (near + far) / dz
    matrix[3, 2] = -1.
    matrix[2, 3] = 2. * near * far / dz

    return matrix

####################################################################################################

def perspective(fovy, aspect, near, far):

    # vertical_field_of_view, aspect_ratio

    """
    fovy
      Specifies the field of view angle, in degrees, in the y direction.

    aspect
      Specifies the aspect ratio that determines the field of view in the x direction.
      the aspect ratio is the ratio of x (width) to y (height).

    near
     Specifies the distance from the viewer to the near clipping plane (always positive).

    far
      Specifies the distance from the viewer to the far clipping plane (always positive).
    """
                

    h = math.tan(math.radians(fovy)/2) # * near
    w = h * aspect
    dz = float(near - far)
    # return frustum(-w, w, -h, h, near, far)

    matrix = np.zeros((4, 4), dtype=np.float32)
    matrix[0, 0] = w
    matrix[1, 1] = h
    matrix[2, 2] = (near + far) / dz
    matrix[3, 2] = -1.
    matrix[2, 3] = 2. * near * far / dz

    return matrix

####################################################################################################
# 
# End
# 
####################################################################################################
