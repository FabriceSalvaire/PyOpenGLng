####################################################################################################
#
# PyOpenGLV4 - An OpenGL V4 layer on top of PyOpengl..
# Copyright (C) 2013 Salvaire Fabrice
#
####################################################################################################

####################################################################################################

import logging

from PyQt4 import QtCore, QtGui

import numpy as np

import OpenGL.GL as GL
import OpenGL.GLU as GLU

####################################################################################################

from PyOpenGLV4.GlWidgetBase import GlWidgetBase

from PyOpenGLV4.Geometry import Point, Offset, Segment, Rectangle
from PyOpenGLV4.GlBuffer import GlUniformBuffer
#!# from PyOpenGLV4.GlOrtho2D import ZoomManagerAbc
from PyOpenGLV4.GlPrimitiveVertexArray import GlSegmentVertexArray, GlRectangleVertexArray
from PyOpenGLV4.GlStippleTexture import GlStippleTexture
from PyOpenGLV4.GlTextureVertexArray import GlTextureVertexArray
from PyOpenGLV4.Tools.Interval import IntervalInt2D
import PyOpenGLV4.GlFixedPipeline as GlFixedPipeline

####################################################################################################

class GlWidget(GlWidgetBase):

    logger = logging.getLogger(__name__)
 
    ##############################################
    
    def __init__(self, parent):

        self.logger.debug('Initialise GlWidget')

        super(GlWidget, self).__init__(parent)

    ##############################################

    def wheelEvent(self, event):

        self.logger.debug('Wheel Event')

        return self.wheel_zoom(event)

    ##############################################

    def init_glortho2d(self):

        # Set max_area so as to correspond to max_binning zoom centered at the origin
        area_size = 10**3
        max_area = IntervalInt2D([-area_size, area_size], [-area_size, area_size])

        super(GlWidget, self).init_glortho2d(max_area, zoom_manager=None)

    ##############################################

    def initializeGL(self):

        self.logger.debug('Initialise GL')

        super(GlWidget, self).initializeGL()

        GL.glEnable(GL.GL_POINT_SMOOTH)
        GL.glEnable(GL.GL_LINE_SMOOTH)
        
        self.qglClearColor(QtCore.Qt.black)
        # GL.glPointSize(5.)
        # GL.glLineWidth(3.)

        self._init_shader()
        self.create_vertex_array_objects()

    ##############################################

    def _init_shader(self):

        self.logger.debug('Initialise Shader')

        # try:
        import ShaderProgramesV3 as ShaderProgrames
        # except:
        # #? QtGui.QApplication.instance().quit()
        # import sys
        # sys.exit(1)
        self.shader_manager = ShaderProgrames.shader_manager
        self.position_shader_interface = ShaderProgrames.position_shader_program_interface

        # Fixme: share interface
        self._viewport_uniform_buffer = GlUniformBuffer()
        viewport_uniform_block = self.position_shader_interface.uniform_blocks.viewport
        self._viewport_uniform_buffer.bind_buffer_base(viewport_uniform_block.binding_point)

    ##############################################

    def update_model_view_projection_matrix(self):

        self.logger.debug('Update Model View Projection Matrix'
                         '\n' + str(self.glortho2d))

        # See also DSA http://www.opengl.org/registry/specs/EXT/direct_state_access.txt
        GL.glMatrixMode(GL.GL_PROJECTION)
        GL.glLoadIdentity()
        GLU.gluOrtho2D(* self.glortho2d.ortho2d_bounding_box())

        viewport_uniform_buffer_data = self.glortho2d.viewport_uniform_buffer_data(self.size())
        self.logger.debug('Viewport Uniform Buffer Data '
                          '\n' + str(viewport_uniform_buffer_data))
        self._viewport_uniform_buffer.set(viewport_uniform_buffer_data)

    ##############################################

    def create_vertex_array_objects(self):

        self.create_textures()

    ##############################################

    def create_textures(self):

        depth = 16

        if depth == 8:
            data_type = np.uint8
        elif depth == 16:
            data_type = np.uint16
        intensity_max = 2**depth -1
        integer_internal_format = True
        
        height, width = 10, 10
        number_of_planes = 3
        data = np.zeros((height, width, number_of_planes),
                        data_type)
        for c in xrange(width):
            data[:,c,:] = int((float(c+1) / width) * intensity_max)
        # data[...] = intensity_max
        # print data
        self.image = data
        self.set_count = 1

        self.texture_vertex_array1 = GlTextureVertexArray(position=Point(0, 0), dimension=Offset(width, height), image=data,
                                                          integer_internal_format=integer_internal_format)
        self.texture_vertex_array1.bind_to_shader(self.shader_manager.texture_shader_program.interface.attributes)
        
        self.texture_vertex_array2 = GlTextureVertexArray(position=Point(-5, -5), dimension=Offset(width, height))
        self.texture_vertex_array2.set(image=data/2, integer_internal_format=integer_internal_format)
        self.texture_vertex_array2.bind_to_shader(self.shader_manager.texture_shader_program.interface.attributes)

    ##############################################

    def paint(self):

        self.paint_textures()

    ##############################################

    def paint_textures(self):

        shader_program = self.shader_manager.texture_shader_program
        shader_program.bind()
        self.texture_vertex_array1.draw()
        self.texture_vertex_array2.draw()
        shader_program.unbind()

####################################################################################################
#
# End
#
####################################################################################################
