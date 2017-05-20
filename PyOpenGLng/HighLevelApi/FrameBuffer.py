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

""" This class provides tools to manage OpenGL Frame Buffer Objects.
"""

# https://www.opengl.org/wiki/Framebuffer_Object
# http://www.opengl-tutorial.org/intermediate-tutorials/tutorial-14-render-to-texture/
# http://www.lighthouse3d.com/tutorials/opengl-short-tutorials/opengl_framebuffer_objects/

####################################################################################################

import logging

import numpy as np

####################################################################################################

from . import GL

####################################################################################################

_module_logger = logging.getLogger(__name__)

####################################################################################################

class GlRenderBuffer(object):

    """ This class wraps an OpenGL Render Buffer.

    Public attributes:

    """

    _logger = _module_logger.getChild('GlRenderBuffer')

    ##############################################
    
    def __init__(self, width, height, internal_format):

        # internal_format: GL.GL_RGBA GL.GL_DEPTH_COMPONENT GL.GL_DEPTH_COMPONENT24
        
        self._gl_id = GL.glGenRenderBuffers(1)

        self.bind()
        target = GL.GL_RENDERBUFFER
        GL.glRenderbufferStorage(target, internal_format, width, height)

    ##############################################
    
    def __del__(self):

        self._logger.debug("Delete Object %u" % (self._gl_id))
        GL.glDeleteRenderBuffers([self._gl_id])

    ##############################################

    @property
    def id(self):
        return self._gl_id

    ##############################################
    
    def bind(self):

        """ Bind the buffer. """

        GL.glBindRenderbuffer(GL.GL_RENDERBUFFER, self._gl_id)

    ##############################################
    
    def unbind(self):

        """ Unind the buffer. """

        GL.glBindRenderbuffer(GL.GL_RENDERBUFFER, 0)

####################################################################################################

class GlFrameBuffer(object):

    """ This class wraps an OpenGL Frame Buffer.

    Public attributes:

    """

    _logger = _module_logger.getChild('GlFrameBuffer')

    # target = GL.GL_FRAMEBUFFER   GL_DRAW_FRAMEBUFFER GL_READ_FRAMEBUFFER
    
    ##############################################
    
    def __init__(self):

        self._gl_id = GL.glGenFrameBuffers(1)
        self._attachments = set()

    ##############################################
    
    def __del__(self):

        self._logger.debug("Delete Object %u" % (self._gl_id))
        GL.glDeleteFrameBuffers([self._gl_id])

    ##############################################
    
    def bind(self, target=GL.GL_FRAMEBUFFER):

        """ Bind the buffer. """

        GL.glBindBuffer(target, self._gl_id)

    ##############################################
    
    def unbind(self, target=GL.GL_FRAMEBUFFER):

        """ Unind the buffer. """

        GL.glBindBuffer(target, 0)

    ##############################################

    def attach_colour_texture(self, texture, attachment=0, target=GL.GL_FRAMEBUFFER):

        self.bind()
        attachment = GL.GL_COLOR_ATTACHMENT0 + attachment
        # level = 0
        # G:glFramebufferTexture2D(target, attachment, GL.GL_TEXTURE_2D, texture.id, 0)
        GL.glFramebufferTexture(target, attachment, texture.id, 0)
        self._attachments.add(attachment)

    ##############################################

    def attach_depth_texture(self, texture, target=GL.GL_FRAMEBUFFER):

        self.bind()
        # level = 0
        GL.glFramebufferTexture(target, Gl.GL_DEPTH_ATTACHMENT, texture.id, 0)

    ##############################################

    def attach_colour_render_buffer(self, render_buffer, attachment=0, target=GL.GL_FRAMEBUFFER):

        self.bind()
        attachment = GL.GL_COLOR_ATTACHMENT0 + attachment
        render_buffer.bind()
        Gl.glFramebufferRenderbuffer(target, attachment, GL.GL_RENDERBUFFER, render_buffer.id)
        self._attachments.add(attachment)

    ##############################################

    def attach_depth_render_buffer(self, render_buffer, target=GL.GL_FRAMEBUFFER):

        self.bind()
        render_buffer.bind()
        Gl.glFramebufferRenderbuffer(target, GL.GL_DEPTH_ATTACHMENT, GL.GL_RENDERBUFFER, render_buffer.id)

    ##############################################
        
        # GL_STENCIL_ATTACHMENT
        
    ##############################################

    def check(self):

        """ Check frame buffer status. """

        self.bind()
        is_complete = GL.glCheckFramebufferStatus(GL.GL_FRAMEBUFFER) == GL.GL_FRAMEBUFFER_COMPLETE
        # GL.GL_FRAMEBUFFER_UNDEFINED
        # GL.GL_FRAMEBUFFER_INCOMPLETE_ATTACHMENT 
        # GL.GL_FRAMEBUFFER_INCOMPLETE_MISSING_ATTACHMENT 
        # GL.GL_FRAMEBUFFER_INCOMPLETE_DRAW_BUFFER 
        # GL.GL_FRAMEBUFFER_UNSUPPORTED 
        # GL.GL_FRAMEBUFFER_COMPLETE
        # self.unbind()
        return is_complete

    ##############################################

    def draw(self):

        self.bind()
        GL.glDrawBuffers(list(self._attachments))
        # set viewport to texture size
        # GL.glViewport(0, 0, width, height)
        # draw ...
        # self.unbind()
                
        # GLSL
        # layout (location = 0) out vec4 normal_output;
        # GL.glBindFragDataLocation()

    ##############################################

        # bind the source framebuffer and select a color attachment to copy from
        # GL.glBindFramebuffer(GL.GL_READ_FRAMEBUFFER, fbo_src)
        # GL.glReadBuffers(GL.GL_COLOR_ATTACHMENT2)
        #
        # bind the destination framebuffer and select the color attachments to copy to
        # GL.glBindFramebuffer(GL.GL_DRAW_FRAMEBUFFER, fbo_dst)
        # GLuint attachments[2] = { GL.GL_COLOR_ATTACHMENT0, GL.GL_COLOR_ATTACHMENT1 }
        # GL.glDrawBuffers(2, attachments)
        #
        # copy
        # GL.glBlitFramebuffer(0, 0, 1024, 1024,
        #                      0, 0, 512, 512,
        #                      GL.GL_COLOR_BUFFER_BIT, GL.GL_LINEAR)

        # glReadBuffer(mode)
        # """mode: Specifies a color buffer. Accepted values are GL_FRONT_LEFT, GL_FRONT_RIGHT, GL_BACK_LEFT,
        # GL_BACK_RIGHT, GL_FRONT, GL_BACK, GL_LEFT, GL_RIGHT, and the constants GL_COLOR_ATTACHMENT.
        # """
        
####################################################################################################
#
# End
#
####################################################################################################
