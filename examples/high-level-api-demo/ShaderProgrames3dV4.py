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

####################################################################################################

class ConfigPath(object):

    module_path = os.path.dirname(__file__)

    ##############################################

    @staticmethod
    def glsl(file_name):

        return os.path.join(ConfigPath.module_path, 'glslv4', file_name)

####################################################################################################

shader_manager = GlShaderManager()

basic_shader_program_interface = GlShaderProgramInterface(uniform_blocks=('viewport',),
                                                          attributes=('position',
                                                                      'normal',
                                                                      'colour'))

if shader_manager.has_visual():
    
    for shader_path in (
        #
        'vertex-shader/fixed_colour_vertex_shader_3d',
        'vertex-shader/varying_colour_vertex_shader_3d',
        'vertex-shader/lighting_vertex_shader',
        #
        'fragment-shader/simple_fragment_shader',
        'fragment-shader/lighting_fragment_shader',
        ):
        shader_name = os.path.basename(shader_path)
        shader_manager.load_from_file(shader_name, ConfigPath.glsl(shader_path + '.glsl'))
    
    for args in (
        {'program_name':'basic_shader_program',
         'shader_list':('varying_colour_vertex_shader_3d',
                        'simple_fragment_shader'),
         'program_interface':basic_shader_program_interface,
         },
        {'program_name':'fixed_colour_shader_program',
         'shader_list':('fixed_colour_vertex_shader_3d',
                        'simple_fragment_shader'),
         'program_interface':basic_shader_program_interface,
         },
        {'program_name':'lighting_shader_program',
         'shader_list':('lighting_vertex_shader',
                        'lighting_fragment_shader'),
         'program_interface':basic_shader_program_interface,
         },
    
        ):
        shader_manager.link_program(**args)

####################################################################################################
# 
# End
# 
####################################################################################################
