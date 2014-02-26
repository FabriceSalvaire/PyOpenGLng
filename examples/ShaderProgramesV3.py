####################################################################################################
# 
# PyOpenGLng - An OpenGL Python Wrapper with a High Level API.
# Copyright (C) 2013 Salvaire Fabrice
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
