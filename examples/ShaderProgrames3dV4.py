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
        #
        'fragment-shader/simple_fragment_shader',
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
    
        ):
        shader_manager.link_program(**args)

####################################################################################################
# 
# End
# 
####################################################################################################
