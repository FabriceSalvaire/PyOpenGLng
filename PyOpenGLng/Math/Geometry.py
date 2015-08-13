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

class Vector(np.ndarray):

    # Fixme: ndarray is probably not efficient for a so small array

    """ This class implements a vector.

    Public attributes:

      x

      y

    """

    ##############################################

    def __new__(cls, *args, **kwargs):

        dimension = 2
        dtype = kwargs.get('dtype', np.float32)
        
        number_of_args = len(args)
        if not number_of_args:
            input_array = (0, 0)
        elif number_of_args == 1:
            obj = args[0]
            if (isinstance(obj, Vector)
                or (isinstance(obj, np.ndarray) and obj.shape == (dimension,))):
                input_array = obj
            # elif iterable
            else:
                raise ValueError("Bad argument " + str(type(obj))) # Fixme: redundant
        elif number_of_args == 2:
            input_array = args
        else:
            raise ValueError("Bad argument " + str(type(obj)))
        
        obj = np.asarray(input_array, dtype=dtype).view(cls)
        
        # obj = np.ndarray.__new__(cls, (dimension,), dtype,
        #                          buffer=None, offset=0, strides=None, order=None)
        
        # if kwargs.get('share', False):
        #     obj = input_array.view(cls)
        
        return obj

    ##############################################

    # def __array_finalize__(self, obj):

    #     if obj is None:
    #         return

    ##############################################

    def __repr__(self):

        return 'Vector ' + str(self)

    ##############################################

    @property
    def x(self):
        return self[0]

    @x.setter
    def x(self, value):
        self[0] = value

    @property
    def y(self):
        return self[1]

    @y.setter
    def y(self, value):
        self[1] = value

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
