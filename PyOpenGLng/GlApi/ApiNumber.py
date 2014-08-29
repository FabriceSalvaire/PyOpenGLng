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

        try:
            self.major, self.minor = [int(x) for x in number.split('.')]
        except ValueError:
            # self.major, self.minor = int(number), 0
            raise NameError("Version number must be of the form x.y")

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
