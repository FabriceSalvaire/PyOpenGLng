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

import os

####################################################################################################

from PyOpenGLng.HighLevelApi.Shader import GlShaderManager, GlShaderProgramInterface
from PyOpenGLng.HighLevelApi.RandomTexture import GlRandomTexture, GlRandomTextureShaderProgram

####################################################################################################

class ConfigPath(object):

    module_path = os.path.dirname(__file__)

    ##############################################

    @staticmethod
    def glsl(file_name):

        return os.path.join(ConfigPath.module_path, 'glslv4', file_name)

####################################################################################################

shader_manager = GlShaderManager()

position_shader_program_interface = GlShaderProgramInterface(uniform_blocks=('viewport',),
                                                             attributes=('position',))

texture_shader_program_interface = GlShaderProgramInterface(uniform_blocks=('viewport',),
                                                            attributes=('position',
                                                                        'position_uv'))

text_shader_program_interface = GlShaderProgramInterface(uniform_blocks=('viewport',),
                                                         attributes=('position',
                                                                     'glyph_size',
                                                                     'position_uv',
                                                                     'colour'))

random_texture = GlRandomTexture(size=1000, texture_unit=1)

if shader_manager.has_visual():
    
    for shader_path in (
        #
        'vertex-shader/fixed_colour_vertex_shader',
        #
        'fragment-shader/simple_fragment_shader',
        'fragment-shader/stipple_line_fragment_shader',
        #
        'geometry-shader/fixed_colour_vertex_shader_in',
        #
        'geometry-shader/centred_rectangle_geometry_shader',
        'geometry-shader/rectangle_geometry_shader',
        'geometry-shader/stipple_line_geometry_shader',
        'geometry-shader/wide_line_geometry_shader',
        #
        'texture-shader/texture_vertex_shader',
        'texture-shader/texture_fragment_shader',
        'texture-shader/texture_label_fragment_shader',
        #
        'text-shader/text_vertex_shader',
        'text-shader/text_geometry_shader',
        'text-shader/text_fragment_shader',
        ):
        shader_name = os.path.basename(shader_path)
        shader_manager.load_from_file(shader_name, ConfigPath.glsl(shader_path + '.glsl'))
    
    for args in (
        {'program_name':'fixed_shader_program',
         'shader_list':('fixed_colour_vertex_shader',
                        'simple_fragment_shader'),
         'program_interface':texture_shader_program_interface,
         },
    
        {'program_name':'texture_shader_program',
         'shader_list':('texture_vertex_shader',
                        'texture_fragment_shader'),
         'program_interface':texture_shader_program_interface,
         },

        {'program_name':'texture_label_shader_program',
         'shader_list':('texture_vertex_shader',
                        'texture_label_fragment_shader'),
         'program_interface':texture_shader_program_interface,
         'shader_program_class':GlRandomTextureShaderProgram,
         'shader_program_args':(random_texture,),
         },

        {'program_name':'text_shader_program',
         'shader_list':('text_vertex_shader',
                        'text_geometry_shader',
                        'text_fragment_shader'),
         'program_interface':text_shader_program_interface,
         },
    
        {'program_name':'rectangle_shader_program',
         'shader_list':('fixed_colour_vertex_shader_in',
                        'rectangle_geometry_shader',
                        'simple_fragment_shader'),
         'program_interface':position_shader_program_interface,
         },
    
        {'program_name':'centred_rectangle_shader_program',
         'shader_list':('fixed_colour_vertex_shader_in',
                        'centred_rectangle_geometry_shader',
                        'simple_fragment_shader'),
         'program_interface':position_shader_program_interface,
         },
    
        {'program_name':'wide_line_shader_program',
         'shader_list':('fixed_colour_vertex_shader_in',
                        'wide_line_geometry_shader',
                        'simple_fragment_shader'),
         'program_interface':position_shader_program_interface,
         },
    
        {'program_name':'stipple_line_shader_program',
         'shader_list':('fixed_colour_vertex_shader_in',
                        'stipple_line_geometry_shader',
                        'stipple_line_fragment_shader'),
         'program_interface':position_shader_program_interface,
         },
    
        ):
        shader_manager.link_program(**args)

####################################################################################################
# 
# End
# 
####################################################################################################
