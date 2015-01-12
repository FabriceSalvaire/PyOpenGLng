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

import logging
import os

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

        self._scale = 1.

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

    def wheelEvent(self, event):

        self.logger.debug('Wheel Event')

        return self.wheel_zoom(event)
    ##############################################

    def wheel_zoom(self, event):

        # self._logger.debug('Wheel Zoom')
        delta = int(event.delta())
        if delta == 120:
            self._scale *= 1.1
        else:
            self._scale /= 1.1
        self.update()

    ##############################################

    def update_model_view_projection_matrix(self):

        self.logger.debug('Update Model View Projection Matrix')

        model_matrix = identity()
        scale_factor = self._scale
        scale(model_matrix, scale_factor, scale_factor, scale_factor)
        rotate_x(model_matrix, self.rotation_x)
        rotate_y(model_matrix, self.rotation_y)
        model_view_matrix = look_at(model_matrix, (0, 0, 50), (0, 0, 0), (0, 1, 0))
        # model_view_matrix = model_matrix
        # Fixme: mat3 doesn't work
        normal_matrix = np.zeros((4, 4), dtype=np.float32)
        normal_matrix[:3,:3] = model_view_matrix[:3,:3] # without translation
        w = 100
        projection_matrix = ortho(-w, w, -w, w, -w, w)
        # projection_matrix = frustum(-2, 2, -2, 2, 1, 3)
        # projection_matrix = perspective(60, 16/9., 1, 3)
        model_view_projection_matrix = np.dot(projection_matrix, model_view_matrix)

        data = []
        for item in (
                     model_view_matrix,
                     normal_matrix,
                     model_view_projection_matrix,
                    ):
            data += list(item.transpose().flatten())

        viewport_array = np.array(data, dtype=np.float32)

        self._viewport_uniform_buffer.set(viewport_array)

    ##############################################

    def create_vertex_array_objects(self):

        self.create_object()

    ##############################################

    def create_object(self):

        # self.object_vertex_array = cube(1, 1, 1)
        # self.object_vertex_array = sphere(1)
        # self.object_vertex_array = torus(1)

        # stl_path = 'cube.stl'
        # stl_path = 'cardan.stl'
        # stl_path = 'teapot.stl'
        stl_path = 'cow.stl'
        # stl_path = 'wild-cow.stl'
        stl_parser = StlParser(os.path.join(os.path.dirname(__file__), 'stl', stl_path))
        self.object_vertex_array = stl_parser.to_vertex_array()
        self.object_vertex_array.bind_to_shader(self.basic_shader_interface.attributes)

    ##############################################

    def paint(self):

        self.paint_object()

        # six.print_('\n', '='*100)
        # for command in GL.called_commands():
        #     six.print_('\n', '-'*50)
        #     # six.print_(str(command))
        #     six.print_(command._command.prototype())
        #     six.print_(command.help())

    ##############################################

    def paint_object(self):

        GL.glPolygonMode(GL.GL_FRONT_AND_BACK, GL.GL_FILL)
        GL.glEnable(GL.GL_POLYGON_OFFSET_FILL)
        GL.glPolygonOffset(1., 1.)
        # shader_program = self.shader_manager.basic_shader_program
        shader_program = self.shader_manager.lighting_shader_program
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
