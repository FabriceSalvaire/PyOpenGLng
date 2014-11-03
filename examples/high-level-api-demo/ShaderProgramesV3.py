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

        return os.path.join(ConfigPath.module_path, 'glslv3', file_name)

####################################################################################################

shader_manager = GlShaderManager()

position_shader_program_interface = GlShaderProgramInterface(uniform_blocks=('viewport',),
                                                             attributes=('position',))

texture_shader_program_interface = GlShaderProgramInterface(uniform_blocks=('viewport',),
                                                            attributes=('position',
                                                                        'position_uv'))

if shader_manager.has_visual():
    
    for shader_name in (
        'fixed_colour_vertex_shader',
        'simple_fragment_shader',
        'texture_fragment_shader',
        'texture_vertex_shader',
        ):
        shader_manager.load_from_file(shader_name, ConfigPath.glsl(shader_name + '.glsl'))
    
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
        ):
        shader_manager.link_program(**args)

####################################################################################################
# 
# End
# 
####################################################################################################
