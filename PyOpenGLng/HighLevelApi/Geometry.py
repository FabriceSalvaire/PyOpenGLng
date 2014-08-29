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

""" This modules provides geometric primitive classes. """

####################################################################################################

import numpy as np

####################################################################################################

class Vector(object):

    """ This class implements a vector.

    Public attributes:

      x

      y

    """

    ##############################################
    
    def __init__(self, x, y):

        self.vertex = np.array([x, y], dtype='f') # dtype=np.float

    ##############################################
    
    def __repr__(self):

        return 'Vector ' + str(self.vertex)

    ##############################################

    @property
    def x(self):
        return self.vertex[0]

    ##############################################
 
    @property
    def y(self):
        return self.vertex[1]

####################################################################################################

class Point(Vector):
    """ This class implements a point. """
    pass

####################################################################################################

class Offset(Vector):
    """ This class implements an offset. """
    pass

####################################################################################################

class Segment(object):

    """ This class implements a segment.

    Public attributes:

      p1

      p2

    """

    ##############################################
    
    def __init__(self, p1, p2):

        self.p1 = p1
        self.p2 = p2

    ##############################################
    
    def __repr__(self):

        return 'Segment ' + str(self.p1) + ' --- ' + str(self.p2)

####################################################################################################

class BoundingBox(Segment):
    """ This class implements a bounding box. """
    pass

####################################################################################################

class Rectangle(object):

    """ This class implements a rectangle defined with a base point and a dimension vector.

    Public attributes:

      point

      dimension

    """

    ##############################################
    
    def __init__(self, point, dimension):

        self.point = point
        self.dimension = dimension

####################################################################################################
#
# End
#
####################################################################################################
