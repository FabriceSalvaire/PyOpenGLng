####################################################################################################
#
# PyOpenGLng - An OpenGL Python Wrapper with a High Level API.
# Copyright (C) 2013 Salvaire Fabrice
#
####################################################################################################

####################################################################################################

class ApiNumber(object):

    """ This class implements a basic API number suitable for OpenGL.

    Use case::

      >>> api_number = ApiNumber('4.4')
      >>> str(api_number)
      '4.4'
      >>> ApiNumber('4.0') < ApiNumber('4.1')
      True
      >>> ApiNumber('4.0') <= ApiNumber('4.0')
      True

    """

    ##############################################

    def __init__(self, number):

        """ The argument *number* must be of the form "x.y". """

        self.major, self.minor = [int(x) for x in number.split('.')]

    ##############################################

    def __int__(self):

        return self.major * 1000 + self.minor

    ##############################################

    def __str__(self):

        return "%u.%u" % (self.major, self.minor)

    ##############################################

    def __le__(self, api_number):

        return int(self) <= int(api_number)

    ##############################################

    def __lt__(self, api_number):

        return int(self) < int(api_number)

####################################################################################################
# 
# End
# 
####################################################################################################
