####################################################################################################
#
# PyOpenGLV4 - An OpenGL V4 layer on top of PyOpengl.
# Copyright (C) 2013 Salvaire Fabrice
#
####################################################################################################

""" This module provides OpenGL Version and feature information.
"""

####################################################################################################

import re

import OpenGL.GL as GL

####################################################################################################

from .Tools.RevisionVersion import RevisionVersion

####################################################################################################

class GlVersion(object):

    """ This class provides the OpenGL Vendor version and the list of supported extensions.

    It must be instantiated after OpenGl was initialised.

    The public attributes are:

      :attr:`vendor_string`
      
      :attr:`renderer_string`
      
      :attr:`version_string`
      
      :attr:`gl_major_version`
      
      :attr:`gl_minor_version`
      
      :attr:`gl_revision_version`

      :attr:`shading_language_version_string`
      
      :attr:`glsl_major_version`
      
      :attr:`glsl_minor_version`

      :attr:`extensions`

    We can test if a particular extension is supported using::

      extension in GlVersion()

    """

    _VERSION_STRING_PATTERN = '^(?P<major>\d+)\.(?P<minor>\d+)(\.(?P<revision>\d+))?.*'
    _GLSL_VERSION_STRING_PATTERN = '(?P<major>\d+)\.(?P<minor>\d+).*'

    ##############################################
    
    def __init__(self):

        self.vendor_string = GL.glGetString(GL.GL_VENDOR)
        self.renderer_string = GL.glGetString(GL.GL_RENDERER)
        self.version_string = GL.glGetString(GL.GL_VERSION)
        self.shading_language_version_string = GL.glGetString(GL.GL_SHADING_LANGUAGE_VERSION)
        self.extensions = GL.glGetString(GL.GL_EXTENSIONS).split(' ')

        match = re.match(self._VERSION_STRING_PATTERN, self.version_string)
        if match is not None:
            d = match.groupdict()
            # Fixme: for compatibility
            self.gl_major_version = d['major']
            self.gl_minor_version = d['minor']
            if d['revision'] is None:
                d['revision'] = 0
            self.gl_revision_version = d['revision']
            self.version = RevisionVersion([int(d[x]) for x in ('major', 'minor', 'revision')])
        else:
            raise ValueError("%s: Can't decode GL Version String: %s" %
                             (self.__class__.__name__,
                              self.version_string))

        match = re.match(self._GLSL_VERSION_STRING_PATTERN, self.shading_language_version_string)
        if match is not None:
            self.glsl_major_version, self.glsl_minor_version = match.groups()
        else:
            raise ValueError("%s: Can't decode GLSL Version String: %s" %
                             (self.__class__.__name__,
                              self.shading_language_version_string))

    ##############################################
    
    def __contains__(self, extension):

        return extension in self.extensions

    ##############################################
    
    def __str__(self):

        message_template = """
Vendor: %s
Version: %s
Renderer: %s
Shading Language Version: %s
Extensions:"""

        message = message_template % (self.vendor_string,
                                   self.version_string,
                                   self.renderer_string,
                                   self.shading_language_version_string,
                                   )

        message += '\n'.join([' '*2 + x for x in sorted(self.extensions)]) + '\n'

        message += 'MAX_VERTEX_ATTRIBS: %u' % (GL.glGetInteger(GL.GL_MAX_VERTEX_ATTRIBS))

        return message

        # self.gl_major_version, self.gl_minor_version, self.gl_revision_version
        # self.glsl_major_version, self.glsl_minor_version

####################################################################################################
#
# End
#
####################################################################################################
