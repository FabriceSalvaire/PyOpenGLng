####################################################################################################
#
# PyOpenGLng - An OpenGL Python Wrapper with a High Level API.
# Copyright (C) 2013 Salvaire Fabrice
#
####################################################################################################

####################################################################################################

import logging

from PyQt4.QtCore import Qt

import numpy as np

####################################################################################################

from PyOpenGLng.HighLevelApi import GL
from PyOpenGLng.HighLevelApi.Buffer import GlUniformBuffer
from PyOpenGLng.HighLevelApi.GlWidgetBase3D import GlWidgetBase3D
from PyOpenGLng.HighLevelApi.Solids import cube
from PyOpenGLng.HighLevelApi.Transforms import *
from PyOpenGLng.Tools.Interval import IntervalInt2D

####################################################################################################

class GlWidget(GlWidgetBase3D):

    logger = logging.getLogger(__name__)
 
    ##############################################
    
    def __init__(self, parent):

        self.logger.debug('Initialise GlWidget')
        super(GlWidget, self).__init__(parent)

    ##############################################

    def initializeGL(self):

        self.logger.debug('Initialise GL')
        super(GlWidget, self).initializeGL()

        self.qglClearColor(Qt.black)

        self._init_shader()
        self.create_vertex_array_objects()

    ##############################################

    def _init_shader(self):

        self.logger.debug('Initialise Shader')

        import ShaderProgrames3dV4 as ShaderProgrames
        self.shader_manager = ShaderProgrames.shader_manager
        self.basic_shader_interface = ShaderProgrames.basic_shader_program_interface

        # Fixme: share interface
        self._viewport_uniform_buffer = GlUniformBuffer()
        viewport_uniform_block = self.basic_shader_interface.uniform_blocks.viewport
        self._viewport_uniform_buffer.bind_buffer_base(viewport_uniform_block.binding_point)

    ##############################################

    def update_model_view_projection_matrix(self):

        self.logger.debug('Update Model View Projection Matrix')

        model_matrix = identity()
        rotate_x(model_matrix, self.rotation_x)
        rotate_y(model_matrix, self.rotation_y)
        view_matrix = ortho(-2, 2, -2, 2, -2, 2)
        model_view_matrix = np.dot(model_matrix, view_matrix)
        self._viewport_uniform_buffer.set(model_view_matrix)

    ##############################################

    def create_vertex_array_objects(self):

        self.create_cube()

    ##############################################

    def create_cube(self):

        self.cube_vertex_array = cube(1, 1, 1)
        self.cube_vertex_array.bind_to_shader(self.basic_shader_interface.attributes)

    ##############################################

    def paint(self):

        self.paint_cube()

        # print '\n', '='*100
        # for command in GL.called_commands():
        #     print '\n', '-'*50
        #     # print str(command)
        #     print command._command.prototype()
        #     print command.help()

    ##############################################

    def paint_cube(self):

        GL.glPolygonMode(GL.GL_FRONT_AND_BACK, GL.GL_FILL)
        GL.glEnable(GL.GL_POLYGON_OFFSET_FILL)
        GL.glPolygonOffset(1., 1.)
        shader_program = self.shader_manager.basic_shader_program
        shader_program.bind()
        self.cube_vertex_array.draw()
        GL.glDisable(GL.GL_POLYGON_OFFSET_FILL)

        GL.glPolygonMode(GL.GL_FRONT_AND_BACK, GL.GL_LINE)
        GL.glLineWidth(1.)
        shader_program = self.shader_manager.fixed_colour_shader_program
        shader_program.bind()
        self.cube_vertex_array.draw()

        shader_program.unbind()

####################################################################################################
#
# End
#
####################################################################################################
