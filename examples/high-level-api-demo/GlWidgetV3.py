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

# Python 2 compatibility
from __future__ import division

####################################################################################################

import logging

import numpy as np

#!# import OpenGL.GL as GL3
#!# import OpenGL.GLU as GLU

####################################################################################################

from PyOpenGLng.HighLevelApi import GL
from PyOpenGLng.HighLevelApi.Buffer import GlUniformBuffer
from PyOpenGLng.HighLevelApi.GlWidgetBase import GlWidgetBase
from PyOpenGLng.HighLevelApi.PrimitiveVertexArray import GlSegmentVertexArray
from PyOpenGLng.HighLevelApi.TextureVertexArray import GlTextureVertexArray
from PyOpenGLng.Math.Geometry import Point, Offset, Segment
from PyOpenGLng.Math.Interval import IntervalInt2D
import PyOpenGLng.HighLevelApi.FixedPipeline as GlFixedPipeline

####################################################################################################

LOG_GL_CALL = False

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
        
        # self.qglClearColor(QtCore.Qt.black)
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
        #!# GL3.glMatrixMode(GL3.GL_PROJECTION)
        #!# GL3.glLoadIdentity()
        #!# GLU.gluOrtho2D(* self.glortho2d.ortho2d_bounding_box())

        viewport_uniform_buffer_data = self.glortho2d.viewport_uniform_buffer_data(self.size())
        self.logger.debug('Viewport Uniform Buffer Data '
                          '\n' + str(viewport_uniform_buffer_data))
        self._viewport_uniform_buffer.set(viewport_uniform_buffer_data)

    ##############################################

    def create_vertex_array_objects(self):

        self.create_grid()
        self.create_textures()

    ##############################################

    def create_grid(self):

        step = 10
        x_min, x_max = -100, 100
        y_min, y_max = -100, 100
       
        segments = []
        for x in range(x_min, x_max +1, step):
            p1 = Point(x, y_min)
            p2 = Point(x, y_max)
            segments.append(Segment(p1, p2))
        for y in range(y_min, y_max +1, step):
            p1 = Point(y_min, y)
            p2 = Point(y_max, y)
            segments.append(Segment(p1, p2))

        self.grid_vertex_array = GlSegmentVertexArray(segments)
        self.grid_vertex_array.bind_to_shader(self.position_shader_interface.attributes.position)

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
        for c in range(width):
            data[:,c,:] = int((float(c+1) / width) * intensity_max)
        # data[...] = intensity_max
        # print data
        self.image = data

        self.texture_vertex_array1 = GlTextureVertexArray(position=Point(0, 0), dimension=Offset(width, height), image=data,
                                                          integer_internal_format=integer_internal_format)
        self.texture_vertex_array1.bind_to_shader(self.shader_manager.texture_shader_program.interface.attributes)

        # self.texture_vertex_array2 = GlTextureVertexArray(position=Point(-5, -5), dimension=Offset(width, height))
        # self.texture_vertex_array2.set(image=data//2, integer_internal_format=integer_internal_format)
        # self.texture_vertex_array2.bind_to_shader(self.shader_manager.texture_shader_program.interface.attributes)

        from PIL import Image
        image = Image.open('flower.png')
        data = np.asarray(image, dtype=np.uint8)
        print((data.shape))
        self.texture_vertex_array2 = GlTextureVertexArray(position=Point(-5, -5), dimension=Offset(width, height))
        self.texture_vertex_array2.set(image=data)
        self.texture_vertex_array2.bind_to_shader(self.shader_manager.texture_shader_program.interface.attributes)

    ##############################################

    def paint(self):

        self.paint_grid()
        self.paint_textures()

        if LOG_GL_CALL:
            six.print_('\n', '='*100)
            for command in GL.called_commands():
                six.print_('\n', '-'*50)
                # six.print_(str(command))
                six.print_(command._command.prototype())
                six.print_(command.help())

    ##############################################

    def paint_grid(self):

        shader_program = self.shader_manager.fixed_shader_program
        shader_program.bind()

        GL.glLineWidth(2.)
        shader_program.uniforms.colour = (1., 1., 1.)
        self.grid_vertex_array.draw()

        #!# GL.glLineWidth(3.)
        #!# x = 25
        #!# GlFixedPipeline.draw_rectangle(-x, -x, x, x)

        shader_program.unbind()

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
