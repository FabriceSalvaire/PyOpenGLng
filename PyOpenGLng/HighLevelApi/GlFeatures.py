####################################################################################################
#
# PyOpenGLng - An OpenGL Python Wrapper with a High Level API.
# Copyright (C) 2013 Salvaire Fabrice
#
####################################################################################################

""" This module gives access to the OpenGL version and features.
"""

####################################################################################################

import re

import OpenGL.GL as GL

####################################################################################################

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
                  for key, value in match.groupdict().iteritems()
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
