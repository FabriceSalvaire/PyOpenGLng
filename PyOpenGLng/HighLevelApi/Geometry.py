####################################################################################################
#
# PyOpenGLng - An OpenGL Python Wrapper with a High Level API.
# Copyright (C) 2013 Salvaire Fabrice
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
