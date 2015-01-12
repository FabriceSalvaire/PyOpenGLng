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

""" This module gives access to the OpenGL version and features.
"""

####################################################################################################

import six

####################################################################################################

import re

####################################################################################################

from . import GL
from ..Tools.RevisionVersion import RevisionVersion

####################################################################################################

class GlVersion(object):

    """ This class encapsulates the OpenGL vendor version.

    It must only be instantiated after that an OpenGl context was created.

    The public attributes are:

      :attr:`glsl_version`

      :attr:`renderer_string`

      :attr:`shading_language_version_string`

      :attr:`vendor_string`

      :attr:`version`

      :attr:`version_string`

    """

    _VERSION_STRING_PATTERN = '^(?P<major>\d+)\.(?P<minor>\d+)(\.(?P<revision>\d+))?.*'
    _GLSL_VERSION_STRING_PATTERN = '(?P<major>\d+)\.(?P<minor>\d+).*'

    ##############################################
    
    @staticmethod
    def _version_from_match(match):
        kwargs = {key:int(value)
                  for key, value in six.iteritems(match.groupdict())
                  if value is not None}

        return RevisionVersion(kwargs)

    ##############################################
    
    def __init__(self):

        self.vendor_string = GL.glGetString(GL.GL_VENDOR)
        self.renderer_string = GL.glGetString(GL.GL_RENDERER)
        self.version_string = GL.glGetString(GL.GL_VERSION)
        self.shading_language_version_string = GL.glGetString(GL.GL_SHADING_LANGUAGE_VERSION)

        match = re.match(self._VERSION_STRING_PATTERN, self.version_string)
        if match is not None:
            self.version = self._version_from_match(match)
        else:
            raise ValueError("Can't decode GL Version String: " + self.version_string)

        match = re.match(self._GLSL_VERSION_STRING_PATTERN, self.shading_language_version_string)
        if match is not None:
            self.glsl_version = self._version_from_match(match)
        else:
            raise ValueError("Can't decode GLSL Version String: " + self.shading_language_version_string)

####################################################################################################

class GlFeatures(object):

    """ This class encapsulates the OpenGL implementation features and available extensions.

    It must only be instantiated after that an OpenGl context was created.

    The public attributes are:

      :attr:`extensions`

    We can test whether a particular extension is supported using::

      extension in GlVersion()

    """

    ##############################################
    
    def __init__(self):

        self.extensions = GL.glGetString(GL.GL_EXTENSIONS).split(' ')

    ##############################################
    
    def __contains__(self, extension):

        """ Test whether a particular extension is supported. """

        return extension in self.extensions

####################################################################################################
#
# End
#
####################################################################################################
