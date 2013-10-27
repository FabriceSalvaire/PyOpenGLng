####################################################################################################
# 
# PyOpenGLV4 - An OpenGL V4 layer on top of PyOpengl.
# Copyright (C) 2013 Salvaire Fabrice
# 
####################################################################################################

####################################################################################################

import os

####################################################################################################

from PyOpenGLV4.GlShader import GlShaderManager, GlShaderProgramInterface
from PyOpenGLV4.GlRandomTexture import GlRandomTexture, GlRandomTextureShaderProgram

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

random_texture = GlRandomTexture(size=1000, texture_unit=1)

if shader_manager.has_visual():
    
    for shader_name in (
        'centred_rectangle_geometry_shader',
        'fixed_colour_vertex_shader',
        'fixed_colour_vertex_shader_in',
        'rectangle_geometry_shader',
        'simple_fragment_shader',
        'stipple_line_fragment_shader',
        'stipple_line_geometry_shader',
        'texture_fragment_shader',
        'texture_label_fragment_shader',
        'texture_vertex_shader',
        'wide_line_geometry_shader',
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

        {'program_name':'texture_label_shader_program',
         'shader_list':('texture_vertex_shader',
                        'texture_label_fragment_shader'),
         'program_interface':texture_shader_program_interface,
         'shader_program_class':GlRandomTextureShaderProgram,
         'shader_program_args':(random_texture,),
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
