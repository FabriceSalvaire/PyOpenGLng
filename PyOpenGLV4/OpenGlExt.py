####################################################################################################
# 
# PyOpenGLV4 - An OpenGL V4 layer on top of PyOpengl..
# Copyright (C) 2013 Salvaire Fabrice
# 
####################################################################################################

""" This module provides missing PyOpenGL functions, cf. :file:`OpenGL/GL/ARB/shader_objects.py`.
"""

####################################################################################################

import OpenGL
import OpenGL.GL as GL
import ctypes

####################################################################################################

def glGetActiveUniformBlockName(program, index):

    """ Retrieve the name of an active uniform block. """

    number_of_uniform_blocks = int(GL.glGetProgramiv(program, GL.GL_ACTIVE_UNIFORM_BLOCKS))
    max_name_length = int(GL.glGetProgramiv(program, GL.GL_ACTIVE_UNIFORM_BLOCK_MAX_NAME_LENGTH))
    if 0 <= index < number_of_uniform_blocks:
        name = ctypes.create_string_buffer(max_name_length)
        name_length = OpenGL.arrays.GLsizeiArray.zeros((1,))
        GL.glGetActiveUniformBlockName(program, index, max_name_length, name_length, name)
        return name.value[:int(name_length[0])]
    else:
        raise IndexError, "Index %s out of range 0 to %i" % (index, number_of_uniform_blocks -1, )

####################################################################################################

def glGetActiveUniformBlockiv(program, index, pname):

    """ Query information about an active uniform block. """

    number_of_uniform_blocks = int(GL.glGetProgramiv(program, GL.GL_ACTIVE_UNIFORM_BLOCKS))
    if 0 <= index < number_of_uniform_blocks:
        if pname != GL.GL_UNIFORM_BLOCK_ACTIVE_UNIFORM_INDICES:
            array_size = 1
        else:
            array_size = glGetActiveUniformBlockiv(program, index, GL.GL_UNIFORM_BLOCK_ACTIVE_UNIFORMS)
        params = OpenGL.arrays.GLintArray.zeros((array_size,))
        GL.glGetActiveUniformBlockiv(program, index, pname, params)
        if array_size > 1: 
            return list(params)
        else:
            return params[0]
    else:
        raise IndexError, 'Index %s out of range 0 to %i' % (index, number_of_uniform_blocks -1, )

####################################################################################################

def glGetActiveUniformsiv(program, indices, pname):

    """ Returns information about several active uniform variables for the specified program
    object.
    """

    number_of_uniform_blocks = int(GL.glGetProgramiv(program, GL.GL_ACTIVE_UNIFORMS))
    try:
        indices = list(indices)
    except TypeError:
        indices = (indices,)
    for index in indices:
        if index < 0 or index > number_of_uniform_blocks:
            raise IndexError, 'Index %s out of range 0 to %i' % (index, number_of_uniform_blocks -1, )
    gl_indices = OpenGL.arrays.GLintArray.zeros((len(indices),))
    gl_indices[:] = indices
    params = OpenGL.arrays.GLintArray.zeros((len(indices),))
    GL.glGetActiveUniformsiv(program, len(indices), indices, pname, params)
    if len(indices) > 1:
        return list(params)
    else:
        return params[0]

####################################################################################################
# 
# End
# 
####################################################################################################
