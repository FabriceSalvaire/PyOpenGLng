# -*- coding: utf-8 -*-

####################################################################################################
#
# PyOpenGLng - An OpenGL Python Wrapper with a High Level API.
# Copyright (C) 2013 Salvaire Fabrice
#
####################################################################################################

""" This module provides classes to handle OpenGL Data Types.

It gives access to the following functions to set and get uniform values:

* glGetUniform{f|i|ui|d}v
* glUniform{1|2|3|4}{f|i|ui}
* glUniform{1|2|3|4}{f|i|ui}v
* glUniformMatrix{2|3|4|2x3|3x2|2x4|4x2|3x4|4x3}fv
* glProgramUniform{1|2|3|4}{f|i|ui}
* glProgramUniform{1|2|3|4}{f|i|ui}v
* glProgramUniformMatrix{2|3|4|2x3|3x2|2x4|4x2|3x4|4x3}fv 

GL data types:

    ======== =========== ====================================================================
    GL Type   Bit Width  Description
    ======== =========== ====================================================================
    boolean    1 or more Boolean
    byte       8         Signed two’s complement binary integer
    ubyte      8         Unsigned binary integer
    char       8         Characters making up strings
    short     16         Signed two’s complement binary integer
    ushort    16         Unsigned binary integer
    int       32         Signed two’s complement binary integer
    uint      32         Unsigned binary integer
    fixed     32         Signed two’s complement 16.16 scaled integer
    int64     64         Signed two’s complement binary integer
    uint64    64         Unsigned binary integer
    sizei     32         Non-negative binary integer size
    enum      32         Enumerated binary integer value
    intptr    ptrbits    Signed twos complement binary integer
    sizeiptr  ptrbits    Non-negative binary integer size
    sync      ptrbits    Sync object handle
    bitfield  32         Bit field
    half      16         Half-precision floating-point value encoded in an unsigned scalar
    float     32         Floating-point value
    clampf    32         Floating-point value clamped to [0, 1]
    double    64         Floating-point value
    clampd    64         Floating-point value clamped to [0, 1]
    ======== =========== ====================================================================

Correspondence of command suffix type descriptors to GL argument types:

    ===============  =====================
    Type Descriptor  Corresponding GL Type
    ===============  =====================
    b                byte
    s                short
    i                int
    i64              int64
    f                float
    d                double
    ub               ubyte
    us               ushort
    ui               uint
    ui64             uint64
    ===============  =====================

"""

####################################################################################################

# __all__ = ['gl_types', 'GlVariableType', 'GlVectorType', 'GlMatrixType', 'GlSamplerType']

####################################################################################################

import logging

import numpy as np

####################################################################################################

from . import GL
from ..Tools.EnumFactory import EnumFactory

####################################################################################################

_module_logger = logging.getLogger(__name__)

####################################################################################################

#: OpenGL data type, cf. OpenGL Specification Table 2.2: GL data types.
gl_data_type = EnumFactory('GlDataType',
                           ('bool',
                            'unsigned_int',
                            'int',
                            'float',
                            'double',
                            ))

#: OpenGL to Numpy data type
gl_to_numpy_data_type = {
    gl_data_type.bool: np.uint32, # np.bool ?
    gl_data_type.unsigned_int: np.uint32,
    gl_data_type.int: np.int32,
    gl_data_type.float: np.float32,
    gl_data_type.double: np.float64,
    }

#! OpenGL data type to the prototype letter
gl_data_type_to_prototype_letter =  {
    gl_data_type.bool: 'ui', # should be 'b'
    gl_data_type.unsigned_int: 'ui',
    gl_data_type.int: 'i',
    gl_data_type.float: 'f',
    gl_data_type.double: 'd',
    }

####################################################################################################

def get_gl_attr(name):
    """ Retrieve an attribute within the GL module. """
    try:
        return getattr(GL, name)
    except AttributeError:
        _module_logger.warn("Command %s is not available in the wrapper", name)
        return None

####################################################################################################

class GlType(object):

    """ This base class defines an OpenGL data type.

    Public attributes are:

      :attr:`token_name`
        OpenGL type name token, for example :attr:`GL.GL_FLOAT_VEC4`

      :attr:`keyword`
        GLSL type keyword, for example ``vec4``

      :attr:`data_type`
         OpenGL data type enumerate, for example :attr:`gl_data_type.float`

      :attr:`uniform_get_v`
        Function to get the uniform value, cf. glGetUniform<type>v functions.

      :attr:`uniform_set_v`
        Function to set the uniform from a pointer, cf. glUniform<type>v functions.

      :attr:`program_uniform_set_v`
        Function to set the uniform from a pointer for the given program, cf. glProgramUniform<type>v functions.

      :attr:`uniform_set`
        Function to set the uniform from arguments, cf. glUniform<type> functions.
        If it is irrelevant for the type, it is set to :obj:`None`.

      :attr:`dtype`
        corresponding Numpy data type

    Subclasses public attributes are:

      :attr:`number_of_dimensions`
        Number of dimensions of the type

      :attr:`shape`
        Shape of the array for vector and matrix type
    
    """

    ##############################################
    
    def __init__(self, token_name, keyword, data_type, uniform_get, uniform_set):

        self.keyword = keyword
        self.data_type = data_type

        self.token_name = get_gl_attr('GL_' + token_name)
        self.uniform_get_v = get_gl_attr('glGetUniform' + uniform_get + 'v')
        self.uniform_set_v = get_gl_attr('glUniform' + uniform_set + 'v')
        # Fixme: 'EXT' is not in the wrapper ???
        # cf. GL_EXT_direct_state_access extension
        self.program_uniform_set_v = get_gl_attr('glProgramUniform' + uniform_set + 'v') # 'vEXT'
        if isinstance(self, (GlVariableType, GlVectorType)):
            self.uniform_set = get_gl_attr('glUniform' + uniform_set)
        else:
            self.uniform_set = None

        self.dtype = gl_to_numpy_data_type[data_type]

    ##############################################
    
    def __str__(self):

        return self.keyword

    ##############################################
    
    def print_object(self):

        template = """
type %(token_name)s
  keyword               %(keyword)s
  data_type             %(data_type)s
  uniform_get_v         %(uniform_get_v)s
  uniform_set_v         %(uniform_set_v)s
  program_uniform_set_v %(program_uniform_set_v)s
  uniform_set           %(uniform_set)s
  dtype                 %(dtype)s
"""

        print template % self.__dict__

####################################################################################################

class GlVariableType(GlType):

    """ This class defines a variable type. """

    number_of_dimensions = 1
    shape = (1,)

    ##############################################
    
    def __init__(self, data_type):

        keyword = str(data_type)
        token_name = keyword.upper()
        uniform_get = gl_data_type_to_prototype_letter[data_type]
        uniform_set = '1' + uniform_get

        super(GlVariableType, self).__init__(token_name, keyword, data_type, uniform_get, uniform_set)

####################################################################################################

class GlVectorType(GlType):

    """ This class defines a vector type. """

    number_of_dimensions = 1

    ##############################################
    
    def __init__(self, data_type, size):

        letter = gl_data_type_to_prototype_letter[data_type]
        suffix = 'vec' + str(size)
        token_name = (str(data_type) + '_' + suffix).upper()
        if data_type == gl_data_type.bool:
            keyword = 'b' + suffix
        elif data_type == gl_data_type.float:
            keyword = suffix
        else:
            keyword = letter + suffix
        uniform_get = letter
        uniform_set = str(size) + uniform_get

        super(GlVectorType, self).__init__(token_name, keyword, data_type, uniform_get, uniform_set)
        
        self.shape = (size,)

####################################################################################################

class GlMatrixType(GlType):

    """ This class defines a matrix type. """

    number_of_dimensions = 2

    ##############################################
    
    def __init__(self, data_type, number_of_rows, number_of_columns):

        if number_of_rows == number_of_columns:
            dimension_string = str(number_of_columns)
        else:
            dimension_string = '%ux%u' % (number_of_rows, number_of_columns)

        token_name = str(data_type).upper() + '_MAT' + dimension_string
        keyword = 'mat' + dimension_string
        uniform_get = 'f'
        uniform_set = 'Matrix' + dimension_string + 'f'

        super(GlMatrixType, self).__init__(token_name, keyword, data_type, uniform_get, uniform_set)

        self.shape = number_of_rows, number_of_columns

####################################################################################################

class GlSamplerType(GlType):

    """ This class defines a sampler type. """

    ##############################################
    
    def __init__(self, data_type, token_name, keyword):

        if data_type != gl_data_type.float:
            token_name = (str(data_type) + '_' + token_name).upper()
            keyword = gl_data_type_to_prototype_letter[data_type] + keyword
        # A sampler corresponds to an unsigned integer.
        # Fixme: why i instead of ui
        uniform_data_type = gl_data_type.int
        uniform_get = 'i'
        uniform_set = '1i'

        super(GlSamplerType, self).__init__(token_name, keyword, uniform_data_type, uniform_get, uniform_set)

        # To distinguish between sampler and uniform data type
        self.sampler_data_type = data_type

####################################################################################################

class GlTypes(dict):

    """ This class stores the OpenGL types in a dictionary indexed by the token name. """

    ##############################################
    
    def __init__(self, gl_types):
    
        super(GlTypes, self).__init__()

        for gl_type in gl_types:
            self[gl_type.token_name] = gl_type

####################################################################################################
#
# Define the OpenGL Type
#

# Fixme: namespace pollution, use an init function, or a lazy initialisation

gl_type_list = []
dimensions = (2, 3, 4)

# Variable types
for data_type in (
    gl_data_type.bool,
    gl_data_type.unsigned_int,
    gl_data_type.int,
    gl_data_type.float,
    gl_data_type.double,
    ):
    gl_type_list.append(GlVariableType(data_type))
                        
# Vector types
for data_type in (
    gl_data_type.bool,
    gl_data_type.unsigned_int,
    gl_data_type.int,
    gl_data_type.float,
    gl_data_type.double,
    ):
    for i in dimensions:
        gl_type_list.append(GlVectorType(data_type, i))

# Matrix types
for data_type in (
    gl_data_type.float,
    gl_data_type.double,
    ):
    for i in dimensions:
        for j in dimensions:
            gl_type_list.append(GlMatrixType(data_type, i, j))

# Sampler types
for data_type in (
    gl_data_type.unsigned_int,
    gl_data_type.int,
    gl_data_type.float,
    ):
    for dimension, suffix in (
        ('1D', ''),
        ('1D', 'array'),
        ('2D', ''),
        ('2D', 'array'),
        ('2D', 'rect'),
        ('3D', ''),
        ('',   'buffer'),
        ('',   'cube'),
        ):
        token_name_parts = ['SAMPLER']
        if dimension:
            token_name_parts.append(dimension)
        if suffix:
            token_name_parts.append(suffix.upper())
        token_name = '_'.join(token_name_parts)
        keyword = 'sampler' + dimension + suffix.title()
        gl_type_list.append(GlSamplerType(data_type, token_name, keyword))

####################################################################################################
#    
# OpenGL 4.2 TODO
#
####################################################################################################

# GL_UNSIGNED_INT_SAMPLER_2D_MULTISAMPLE:'usampler2DMS',
# GL_UNSIGNED_INT_SAMPLER_2D_MULTISAMPLE_ARRAY:'usampler2DMSArray',
# GL_INT_SAMPLER_2D_MULTISAMPLE:'isampler2DMS',
# GL_INT_SAMPLER_2D_MULTISAMPLE_ARRAY:'isampler2DMSArray',
# GL_SAMPLER_2D_MULTISAMPLE:'sampler2DMS',
# GL_SAMPLER_2D_MULTISAMPLE_ARRAY:'sampler2DMSArray',

# GL_UNSIGNED_INT_IMAGE_1D:'uimage1D',
# GL_UNSIGNED_INT_IMAGE_1D_ARRAY:'uimage1DArray',
# GL_UNSIGNED_INT_IMAGE_2D:'uimage2D',
# GL_UNSIGNED_INT_IMAGE_2D_ARRAY:'uimage2DArray',
# GL_UNSIGNED_INT_IMAGE_2D_MULTISAMPLE:'uimage2DMS',
# GL_UNSIGNED_INT_IMAGE_2D_MULTISAMPLE_ARRAY:'uimage2DMSArray',
# GL_UNSIGNED_INT_IMAGE_2D_RECT:'uimage2DRect',
# GL_UNSIGNED_INT_IMAGE_3D:'uimage3D',
# GL_UNSIGNED_INT_IMAGE_BUFFER:'uimageBuffer',
# GL_UNSIGNED_INT_IMAGE_CUBE:'uimageCube',

# GL_INT_IMAGE_1D:'iimage1D',
# GL_INT_IMAGE_1D_ARRAY:'iimage1DArray',
# GL_INT_IMAGE_2D:'iimage2D',
# GL_INT_IMAGE_2D_ARRAY:'iimage2DArray',
# GL_INT_IMAGE_2D_MULTISAMPLE:'iimage2DMS',
# GL_INT_IMAGE_2D_MULTISAMPLE_ARRAY:'iimage2DMSArray',
# GL_INT_IMAGE_2D_RECT:'iimage2DRect',
# GL_INT_IMAGE_3D:'iimage3D',
# GL_INT_IMAGE_BUFFER:'iimageBuffer',
# GL_INT_IMAGE_CUBE:'iimageCube',

# GL_IMAGE_1D:'image1D',
# GL_IMAGE_1D_ARRAY:'image1DArray',
# GL_IMAGE_2D:'image2D',
# GL_IMAGE_2D_ARRAY:'image2DArray',
# GL_IMAGE_2D_MULTISAMPLE:'image2DMS',
# GL_IMAGE_2D_MULTISAMPLE_ARRAY:'image2DMSArray',
# GL_IMAGE_2D_RECT:'image2DRect',
# GL_IMAGE_3D:'image3D',
# GL_IMAGE_BUFFER:'imageBuffer',
# GL_IMAGE_CUBE:'imageCube',

# GL_UNSIGNED_INT_ATOMIC_COUNTER:'atomic_uint',

####################################################################################################

#: singleton for the :class:`GlTypes`
gl_types = GlTypes(gl_type_list)

####################################################################################################
#
# Print OpenGL Types
#
####################################################################################################

if __name__ == '__main__':

    for gl_type in gl_types.itervalues():
        gl_type.print_object()

####################################################################################################
#
# End
#
####################################################################################################
