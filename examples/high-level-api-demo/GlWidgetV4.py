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



import six
from six.moves import xrange

####################################################################################################

import logging

import numpy as np

####################################################################################################

# import OpenGL.GLU as GLU
# try:
#     import OpenGL.GL.NV.path_rendering as nvpath
# except ImportError:
#     nvpath = None
nvpath = None

####################################################################################################

#!# from PyOpenGLng.HighLevelApi.GlOrtho2D import ZoomManagerAbc

from PyOpenGLng.HighLevelApi import GL
from PyOpenGLng.HighLevelApi.Buffer import GlUniformBuffer
from PyOpenGLng.HighLevelApi.GlWidgetBase import GlWidgetBase
from PyOpenGLng.HighLevelApi.ImageTexture import ImageTexture
from PyOpenGLng.HighLevelApi.PrimitiveVertexArray import GlSegmentVertexArray, GlRectangleVertexArray
from PyOpenGLng.HighLevelApi.StippleTexture import GlStippleTexture
from PyOpenGLng.HighLevelApi.TextVertexArray import TextVertexArray
from PyOpenGLng.HighLevelApi.TextureFont import TextureFont
from PyOpenGLng.HighLevelApi.TextureVertexArray import GlTextureVertexArray
from PyOpenGLng.Math.Geometry import Point, Offset, Segment, Rectangle
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

        # Require compatibility profile
        GL.glEnable(GL.GL_POINT_SMOOTH)
        GL.glEnable(GL.GL_LINE_SMOOTH)
        
        self._init_shader()
        self.create_vertex_array_objects()

    ##############################################

    def _init_shader(self):

        self.logger.debug('Initialise Shader')

        import ShaderProgramesV4 as ShaderProgrames
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

        # To test NVPath API
        # See also DSA http://www.opengl.org/registry/specs/EXT/direct_state_access.txt
        #compat# GL.glMatrixMode(GL.GL_PROJECTION)
        #compat# GL.glLoadIdentity()
        #GLU# GLU.gluOrtho2D(* self.glortho2d.ortho2d_bounding_box())

        viewport_uniform_buffer_data = self.glortho2d.viewport_uniform_buffer_data(self.size())
        self.logger.debug('Viewport Uniform Buffer Data '
                          '\n' + str(viewport_uniform_buffer_data))
        self._viewport_uniform_buffer.set(viewport_uniform_buffer_data)

    ##############################################

    def create_vertex_array_objects(self):

        self.create_grid()
        if nvpath is not None:
            self.create_path()
        self.create_lines()
        self.create_textures()
        self.create_text()

    ##############################################

    def create_grid(self):

        step = 100
        x_min, x_max = -1000, 1000
        y_min, y_max = -1000, 1000
       
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

    def create_path(self):

        self.path_object = nvpath.glGenPathsNV(1)
        # six.print_(self.path_object)
        start_ps_path = """ 100 180 moveto 40 10 lineto 190 120 lineto 10 120 lineto 160 10 lineto closepath   """
        nvpath.glPathStringNV(self.path_object, nvpath.GL_PATH_FORMAT_PS_NV, len(start_ps_path), start_ps_path)
        nvpath.glPathParameteriNV(self.path_object, nvpath.GL_PATH_JOIN_STYLE_NV, nvpath.GL_ROUND_NV)
        nvpath.glPathParameterfNV(self.path_object, nvpath.GL_PATH_STROKE_WIDTH_NV, 6.5)

    ##############################################

    def create_lines(self):

        def simple_square_generator(radius):
            p1 = Point(-radius, -radius)
            p2 = Point(-radius,  radius)
            p3 = Point( radius,  radius)
            p4 = Point( radius, -radius)
            return (Segment(p1, p2),
                    Segment(p2, p3),
                    Segment(p3, p4),
                    Segment(p4, p1),
                    )

        segments = simple_square_generator(radius=10)
        self.simple_square_vertex_array = GlSegmentVertexArray(segments)
        self.simple_square_vertex_array.bind_to_shader(self.position_shader_interface.attributes.position)

        def segment_generator(radius):
            p1 = Point(-radius, -radius)
            p2 = Point(      0,  radius)
            p3 = Point( radius, -radius)
            return (Segment(p1, p2),
                    Segment(p2, p3),
                    Segment(p3, p1),
                    )

        segments = segment_generator(radius=5)
        self.segment_vertex_array1 = GlSegmentVertexArray(segments)
        self.segment_vertex_array1.bind_to_shader(self.position_shader_interface.attributes.position)

        segments2 = segment_generator(radius=10)
        self.segment_vertex_array2 = GlSegmentVertexArray(segments2)
        self.segment_vertex_array2.bind_to_shader(self.position_shader_interface.attributes.position)

        segments3 = (Segment(Point(-5, 0), Point(5, 0)),
                     Segment(Point(-5, 1), Point(5, 1)),
                     Segment(Point(0, -5), Point(0, 5)),
                     Segment(Point(1, -5), Point(1, 5)),
                     )
        self.segment_vertex_array3 = GlSegmentVertexArray(segments3)
        self.segment_vertex_array3.bind_to_shader(self.position_shader_interface.attributes.position)


        rectangles = (Rectangle(Point(0, 0), Offset(5, 5)),
                      Rectangle(Point(-5, -5), Offset(6, 6)),
                      )
        self.rectangle_vertex_array = GlRectangleVertexArray(rectangles)
        self.rectangle_vertex_array.bind_to_shader(self.position_shader_interface.attributes.position)
        
        centred_rectangles = (Rectangle(Point(0, 0), Offset(1, 1)),
                              )
        self.centred_rectangle_vertex_array = GlRectangleVertexArray(centred_rectangles)
        self.centred_rectangle_vertex_array.bind_to_shader(self.position_shader_interface.attributes.position)

        segments = (Segment(Point(0,0), Point(5,5)),
                    )
        self.line_vertex_array1 = GlSegmentVertexArray(segments)
        self.line_vertex_array1.bind_to_shader(self.position_shader_interface.attributes.position)

        segments = (Segment(Point(-5,5), Point(5,-5)),
                    )
        self.line_vertex_array2 = GlSegmentVertexArray(segments)
        self.line_vertex_array2.bind_to_shader(self.position_shader_interface.attributes.position)

        # stipple_pattern = 01111111111111111
        # stipple_pattern = 01100110011001111
        stipple_pattern = 0xFF00
        self.stipple_texture = GlStippleTexture(stipple_pattern)

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
        # six.print_(data)
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
        self.texture_vertex_array2 = GlTextureVertexArray(position=Point(-10, -10), dimension=Offset(width, height))
        self.texture_vertex_array2.set(image=data, integer_internal_format=integer_internal_format)
        self.texture_vertex_array2.bind_to_shader(self.shader_manager.texture_shader_program.interface.attributes)

        height, width = 50, 50
        data = np.zeros((height, width, number_of_planes),
                        data_type)
        # data[...] = intensity_max
        data[10:20,10:20,0] = 1
        data[30:50,30:50,1] = 2
        self.texture_vertex_array3 = GlTextureVertexArray(position=Point(15, 15), dimension=Offset(width, height))
        self.texture_vertex_array3.set(image=data, integer_internal_format=integer_internal_format)
        self.texture_vertex_array3.bind_to_shader(self.shader_manager.texture_label_shader_program.interface.attributes)
        # self.texture_vertex_array3.bind_to_shader(self.shader_manager.texture_shader_program.interface.attributes)

    ##############################################

    def create_text(self):

        self.font = TextureFont('./Vera.ttf')
        self.font_size = self.font[25]
        self.font_size.load_all_glyphs()
        self.font.atlas.save('atlas.png')
        self.font_atlas_texture = ImageTexture(self.font.atlas.data)

        self.text_vertex_array = TextVertexArray(self.font_atlas_texture)
        self.text_vertex_array.add(text="| A Quick Brown Fox Jumps Over The Lazy Dog fi ffl Va",
                                   font_size=self.font_size,
                                   colour=(1.0, 1.0, .0, 1.0),
                                   x=0, y=0,
                                   anchor_x='left', anchor_y='baseline',
                                   )
        self.text_vertex_array.add(text="| Foo Bar",
                                   font_size=self.font_size,
                                   colour=(.0, 1.0, .0, 1.0),
                                   x=200, y=100,
                                   anchor_x='left', anchor_y='baseline',
                                   )
        self.text_vertex_array.upload()
        self.text_vertex_array.bind_to_shader(self.shader_manager.text_shader_program.interface.attributes)

    ##############################################

    def paint(self):

        self.paint_grid()
        if nvpath is not None:
            self.paint_path()
        self.paint_textures()
        self.paint_lines()
        self.paint_text()

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

        GL.glLineWidth(1.)
        shader_program.uniforms.colour = (1., 1., 1.)
        self.grid_vertex_array.draw()

        GL.glLineWidth(10.)
        x = 150
        GlFixedPipeline.draw_rectangle(-x, -x, x, x)

        shader_program.unbind()

    ##############################################

    def paint_path(self):

        # Unbind shader /!\

        # GL.glClearStencil(0)
        # GL.glClearColor(0,0,0,0)
        # # GL.glClear(GL.GL_COLOR_BUFFER_BIT)
        # GL.glStencilMask(~0)
        # GL.glClear(GL.GL_COLOR_BUFFER_BIT | GL.GL_STENCIL_BUFFER_BIT)

        filling = False # /!\ clear framebuffer
        even_odd = True
        stroking = True

        if filling:
            nvpath.glStencilFillPathNV(self.path_object, nvpath.GL_COUNT_UP_NV, 0x1F)
            GL.glEnable(GL.GL_STENCIL_TEST)
            if even_odd:
                GL.glStencilFunc(GL.GL_NOTEQUAL, 0, 0x1)
            else:
                GL.glStencilFunc(GL.GL_NOTEQUAL, 0, 0x1F)
            GL.glStencilOp(GL.GL_KEEP, GL.GL_KEEP, GL.GL_ZERO)
            GL.glColor3f(0,1,0) #  green
            nvpath.glCoverFillPathNV(self.path_object, nvpath.GL_BOUNDING_BOX_NV)

        if stroking:
            nvpath.glStencilStrokePathNV(self.path_object, 0x1, ~0)
            GL.glColor3f(1,1,0) # yellow
            nvpath.glCoverStrokePathNV(self.path_object, nvpath.GL_CONVEX_HULL_NV)

    ##############################################

    def paint_lines(self):

        shader_program = self.shader_manager.fixed_shader_program
        shader_program.bind()

        GL.glLineWidth(1.)
        shader_program.uniforms.colour = (0., 0., 1.)
        self.simple_square_vertex_array.draw()

        # try:
        GL.glLineWidth(5.)
        shader_program.uniforms.colour = (0., 0., 1.)
        self.segment_vertex_array1.draw()
        # del self.segment_vertex_array1
        # except:
        #    pass
        
        GL.glLineWidth(2.)
        shader_program.uniforms.colour = (0., 1., 1.)
        self.segment_vertex_array2.draw()
        
        GL.glLineWidth(2.)
        shader_program.uniforms.colour = (1., 0., 0.)
        # six.print_('colour', shader_program.uniforms.colour)
        self.segment_vertex_array3.draw()
        
        shader_program = self.shader_manager.rectangle_shader_program
        shader_program.bind()
        GL.glLineWidth(2.)
        shader_program.uniforms.colour = (1., 0., 1.)
        self.rectangle_vertex_array.draw()
        
        shader_program = self.shader_manager.centred_rectangle_shader_program
        shader_program.bind()
        GL.glLineWidth(2.)
        shader_program.uniforms.colour = (8., 3., .5)
        self.centred_rectangle_vertex_array.draw()

        shader_program = self.shader_manager.wide_line_shader_program
        shader_program.bind()
        shader_program.uniforms.line_width = 2
        shader_program.uniforms.colour = (1., 1., 1.)
        self.line_vertex_array1.draw()

        shader_program = self.shader_manager.stipple_line_shader_program
        shader_program.bind()
        shader_program.uniforms.line_width = 4
        shader_program.uniforms.stipple_factor = 4
        shader_program.uniforms.colour = (1., .8, .8)
        self.stipple_texture.bind()
        self.line_vertex_array2.draw()
        self.stipple_texture.unbind()

        shader_program.unbind()

    ##############################################

    def paint_textures(self):

        shader_program = self.shader_manager.texture_shader_program
        shader_program.bind()
        shader_program.uniforms.scale = float(2**16 - 1)
        self.texture_vertex_array1.draw()
        shader_program.uniforms.scale = float(2**8 - 1)
        self.texture_vertex_array2.draw()
        shader_program.unbind()

        shader_program = self.shader_manager.texture_label_shader_program
        # shader_program = self.shader_manager.texture_shader_program
        shader_program.bind()
        self.texture_vertex_array3.draw()
        shader_program.unbind()

    ##############################################

    def paint_text(self):

        shader_program = self.shader_manager.text_shader_program
        # shader_program.bind()
        # shader_program.uniforms. ...
        self.text_vertex_array.draw(shader_program)
        # shader_program.unbind()

####################################################################################################
#
# End
#
####################################################################################################
