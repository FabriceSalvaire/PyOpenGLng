####################################################################################################
#
# PyOpenGLng - An OpenGL Python Wrapper with a High Level API.
# Copyright (C) 2013 Salvaire Fabrice
#
####################################################################################################

####################################################################################################

import logging
import sys

import numpy as np

from PyQt4 import QtCore, QtGui

####################################################################################################

import PyOpenGLng.Wrapper as GlWrapper
from PyOpenGLng.HighLevelApi.GlWidgetBase import GlWidgetBase

####################################################################################################

class GlWidget(GlWidgetBase):

    logger = logging.getLogger(__name__)
 
    ##############################################
    
    def __init__(self, parent):

        self.logger.debug('Initialise GlWidget')

        super(GlWidget, self).__init__(parent)

    ##############################################

    def initializeGL(self):

        self.logger.debug('Initialise GL')

        super(GlWidget, self).initializeGL()
        self._init_shader()
        
        GL = GlWrapper.init() # api_number='3.0'

        self._test_wrapper(GL)

    ##############################################

    def _init_shader(self):

        self.logger.debug('Initialise Shader')

        import ShaderProgramesV3 as ShaderProgrames
        self.shader_manager = ShaderProgrames.shader_manager

    ##############################################

    def _test_wrapper(self, GL):

        print GL.glGetString(GL.GL_VERSION)
        # print GL.glGetString(GL.GL_EXTENSIONS) # works
        print GL.glGetStringi(GL.GL_EXTENSIONS, 1)

        # print GL._error_code_message(GL.glGetError())

        print GL.glGetString(0)
        print GL._error_code_message(GL.glGetError())

        print GL.glGetString(0, check_error=False)

        try:
            print GL.glGetString(0, check_error=True)
        except Exception as e:
            print e.message

        with GL.error_checker():
            print GL.glGenBuffers(10)
            data = np.zeros(10, dtype=np.uint32)
            GL.glGenBuffers(data)
            print data

        with GL.error_checker():
            N = 10
            data = np.arange(N, dtype=np.uint8)
            data_back = data.copy()

            buffer_id = GL.glGenBuffers(1)
            GL.glBindBuffer(GL.GL_ARRAY_BUFFER, buffer_id)
            GL.glBufferData(GL.GL_ARRAY_BUFFER, data, GL.GL_STATIC_DRAW)
            # data_back = GL.glGetBufferSubData(GL.GL_ARRAY_BUFFER, 0, data.nbytes) # void * has no type
            GL.glGetBufferSubData(GL.GL_ARRAY_BUFFER, 0, data_back)

            print data, data_back

        with GL.error_checker():
            texture_id = GL.glGenTextures(1)
            GL.glActiveTexture(GL.GL_TEXTURE0)
            GL.glBindTexture(GL.GL_TEXTURE_1D, texture_id)
            GL.glTexParameteri(GL.GL_TEXTURE_1D, GL.GL_TEXTURE_MAG_FILTER, GL.GL_NEAREST)
            GL.glTexParameteri(GL.GL_TEXTURE_1D, GL.GL_TEXTURE_MIN_FILTER, GL.GL_NEAREST)
            stipple_pattern_image = np.zeros((100), dtype=np.uint8)
            # <param len="COMPSIZE(format,type,width)">const void *<name>pixels</name></param>
            #   width = array.size
            GL.glTexImage1D(GL.GL_TEXTURE_1D,
                            0, GL.GL_LUMINANCE, stipple_pattern_image.size, 0, GL.GL_LUMINANCE, GL.GL_UNSIGNED_BYTE,
                            stipple_pattern_image)

        with GL.error_checker():
            data = np.arange(1, dtype=np.int32)
            GL.glActiveTexture(GL.GL_TEXTURE4)
            GL.glGetIntegerv(GL.GL_ACTIVE_TEXTURE, data)
            assert(data[0] == GL.GL_TEXTURE4)
            data = np.arange(2, dtype=np.int32)
            GL.glGetIntegerv(GL.GL_POINT_SIZE_RANGE, data)
            # GL_DEPTH_RANGE
            assert(data[0] == 1 and data[1] == 255)

        with GL.error_checker():
            shader_id = GL.glCreateShader(GL.GL_VERTEX_SHADER)
            # more than one input pointer sharing the same size parameter
            #   <param><ptype>GLsizei</ptype> <name>count</name></param>
            #   <param len="count">const <ptype>GLchar</ptype> *const*<name>string</name></param>
            #   <param len="count">const <ptype>GLint</ptype> *<name>length</name></param>
            GL.glShaderSource(shader_id, "uniform vec2 x;")
            log, length = GL.glGetShaderSource(shader_id, 1000)
            print length, ':', log
            GL.glShaderSource(shader_id, ("uniform vec23 x;",))
            GL.glCompileShader(shader_id)
            log, length = GL.glGetShaderInfoLog(shader_id, 1000)
            print length, ':', log
            print GL.glGetShaderInfoLog.__doc__

        # Open manual
        # GL.glShaderSource.manual()
        # GL.glShaderSource.manual(local=True)

        # void glGetActiveAttrib(GLuint program,  GLuint index,  GLsizei bufSize,  GLsizei *length,  GLint *size,  GLenum *type,  GLchar *name);

        sys.exit(0)
        # QtGui.QApplication.instance().exit()

    ##############################################

    def update_model_view_projection_matrix(self):

        pass

    ##############################################

    def paint(self):

        pass

####################################################################################################
#
# End
#
####################################################################################################
