####################################################################################################
#
# PyOpenGLV4 - An OpenGL V4 layer on top of PyOpengl.
# Copyright (C) 2013 Salvaire Fabrice
#
####################################################################################################

####################################################################################################

import os
import logging
import sys

import numpy as np

from PyQt4 import QtCore, QtGui

import OpenGL.GL as GL

####################################################################################################

from PyOpenGLV4.GlApi.CtypeWrapper import CtypeWrapper
from PyOpenGLV4.GlApi.GlSpecParser import GlSpecParser, ApiNumber
from PyOpenGLV4.GlWidgetBase import GlWidgetBase

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
        
        ##############################################
        print 'PyOpenGL'
        print GL.glGetString(GL.GL_VERSION)
        
        ##############################################
        print 'ctypes'
        import ctypes
        libGL = ctypes.cdll.LoadLibrary('/usr/lib64/libGL.so')
        libGL.glGetString.restype = ctypes.c_char_p
        print libGL.glGetString(int(GL.GL_VERSION))
        
        ##############################################
        if False:
            print 'cffi'
            from cffi import FFI
            ffi = FFI()
            ffi.cdef("""
              int glGetError(void);
              const char* glGetString(int name);
            """)
            libGL = ffi.dlopen('/usr/lib64/libGL.so')
            print ffi.string(libGL.glGetString(int(GL.GL_VERSION)))
            print libGL.glGetError()
        
        ##############################################
        print 'PyOpenGL-ng'
        api_path = '/home/gv/fabrice/unison-osiris/inactive-projects/PyOpenGLV4/doc/registry-api'
        gl_xml_file_path = os.path.join(api_path, 'gl.xml')
        gl_spec = GlSpecParser(gl_xml_file_path)
        
        wrapper = CtypeWrapper(gl_spec, api='gl', api_number=ApiNumber('3.0'), profile='core')
        print wrapper.glGetString(wrapper.GL.GL_VERSION)
        # print wrapper.glGetString(wrapper.GL.GL_EXTENSIONS) # works
        print wrapper.glGetStringi(wrapper.GL.GL_EXTENSIONS, 1)
        print wrapper._pythonic_wrapper.error_code_message(wrapper.glGetError())
        print wrapper.glGetString(0)
        print wrapper._pythonic_wrapper.error_code_message(wrapper.glGetError())
        print wrapper.glGetString(0, check_error=False)
        try:
            print wrapper.glGetString(0, check_error=True)
        except Exception as e:
            print e.message

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
