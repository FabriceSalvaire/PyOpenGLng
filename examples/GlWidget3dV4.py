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
from PyOpenGLng.HighLevelApi.Solids import cube, sphere, torus
from PyOpenGLng.HighLevelApi.Transforms import *
from PyOpenGLng.HighLevelApi.STL import StlParser

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
        model_view_matrix = look_at(model_matrix, (0, 0, 2), (0, 0, 0), (0, 1, 0))
        # model_view_matrix = model_matrix
        normal_matrix = model_view_matrix[:3,:3] # without translation
        w = 3
        projection_matrix = ortho(-w, w, -w, w, -w, w)
        # projection_matrix = frustum(-2, 2, -2, 2, 1, 3)
        # projection_matrix = perspective(60, 16/9., 1, 3)
        model_view_projection_matrix = np.dot(projection_matrix, model_view_matrix)

        viewport_array = np.array(list(model_view_projection_matrix.transpose().flatten()) +
                                  list(model_view_matrix.transpose().flatten()) +
                                  list(normal_matrix.transpose().flatten()) +
                                  list(projection_matrix.transpose().flatten()),
                                  dtype=np.float32)

        self._viewport_uniform_buffer.set(viewport_array)

    ##############################################

    def create_vertex_array_objects(self):

        self.create_object()

    ##############################################

    def create_object(self):

        # self.object_vertex_array = cube(1, 1, 1)
        # self.object_vertex_array = sphere(1)
        self.object_vertex_array = torus(1)

        # stl_path = 'cube.stl'
        stl_path = 'cardan.stl'
        # stl_parser = StlParser(stl_path)
        # self.object_vertex_array = stl_parser.to_vertex_array()
        self.object_vertex_array.bind_to_shader(self.basic_shader_interface.attributes)

    ##############################################

    def paint(self):

        self.paint_object()

        # print '\n', '='*100
        # for command in GL.called_commands():
        #     print '\n', '-'*50
        #     # print str(command)
        #     print command._command.prototype()
        #     print command.help()

    ##############################################

    def paint_object(self):

        GL.glPolygonMode(GL.GL_FRONT_AND_BACK, GL.GL_FILL)
        GL.glEnable(GL.GL_POLYGON_OFFSET_FILL)
        GL.glPolygonOffset(1., 1.)
        shader_program = self.shader_manager.basic_shader_program
        # shader_program = self.shader_manager.lighting_shader_program
        # shader_program.light.Position = (0, 0, 100, 1)
        shader_program.bind()
        self.object_vertex_array.draw()
        GL.glDisable(GL.GL_POLYGON_OFFSET_FILL)

        GL.glPolygonMode(GL.GL_FRONT_AND_BACK, GL.GL_LINE)
        GL.glLineWidth(1.)
        shader_program = self.shader_manager.fixed_colour_shader_program
        shader_program.bind()
        self.object_vertex_array.draw()

        shader_program.unbind()

####################################################################################################
#
# End
#
####################################################################################################
