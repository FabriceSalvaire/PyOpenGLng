####################################################################################################
# 
# PyOpenGLng - An OpenGL Python Wrapper with a High Level API.
# Copyright (C) 2013 Salvaire Fabrice
# 
####################################################################################################

""" This module provides missing PyOpenGL functions, cf. :file:`OpenGL/GL/ARB/shader_objects.py`.
"""

####################################################################################################

import ctypes

import numpy as np

####################################################################################################

from . import GL

####################################################################################################

def glGetShaderiv(program, pname):
    data = np.zeros(1, dtype=np.int32)
    GL.glGetShaderiv(program, pname, data)
    return data[0]

####################################################################################################

def glGetProgramiv(program, pname):
    data = np.zeros(1, dtype=np.int32)
    GL.glGetProgramiv(program, pname, data)
    return data[0]

####################################################################################################

def glGetActiveUniformBlockiv(program, pname):
    data = np.zeros(1, dtype=np.int32)
    GL.glGetActiveUniformBlockiv(program, pname, data)
    return data[0]

####################################################################################################

def glGetActiveUniformBlockName(program, index):

    """ Retrieve the name of an active uniform block. """

    number_of_uniform_blocks = int(glGetProgramiv(program, GL.GL_ACTIVE_UNIFORM_BLOCKS))
    max_name_length = int(glGetProgramiv(program, GL.GL_ACTIVE_UNIFORM_BLOCK_MAX_NAME_LENGTH))
    if 0 <= index < number_of_uniform_blocks:
        name, name_length = GL.glGetActiveUniformBlockName(program, index, 1000)
        return name
    else:
        raise IndexError, "Index %s out of range 0 to %i" % (index, number_of_uniform_blocks -1, )

####################################################################################################

def glGetActiveUniformBlockiv(program, index, pname):

    """ Query information about an active uniform block. """

    number_of_uniform_blocks = int(glGetProgramiv(program, GL.GL_ACTIVE_UNIFORM_BLOCKS))
    if 0 <= index < number_of_uniform_blocks:
        if pname != GL.GL_UNIFORM_BLOCK_ACTIVE_UNIFORM_INDICES:
            array_size = 1
        else:
            array_size = glGetActiveUniformBlockiv(program, index, GL.GL_UNIFORM_BLOCK_ACTIVE_UNIFORMS)
        params = np.zeros(array_size, dtype=np.int32)
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

    number_of_uniform_blocks = int(glGetProgramiv(program, GL.GL_ACTIVE_UNIFORMS))
    try:
        indices = list(indices)
    except TypeError:
        indices = (indices,)
    for index in indices:
        if index < 0 or index > number_of_uniform_blocks:
            raise IndexError, 'Index %s out of range 0 to %i' % (index, number_of_uniform_blocks -1, )
    gl_indices = np.array(indices, dtype=np.uint32)
    params = np.zeros(len(indices), dtype=np.int32)
    GL.glGetActiveUniformsiv(program, len(indices), gl_indices, pname, params)
    if len(indices) > 1:
        return list(params)
    else:
        return params[0]

####################################################################################################
# 
# End
# 
####################################################################################################
