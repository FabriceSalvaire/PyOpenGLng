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

""" This modules provides classes to manager OpenGL Shader.
"""

####################################################################################################
#
#                                              Audit
#
# - 15/01/2013 Fabrice
#  location versus index, binding point
#
####################################################################################################

####################################################################################################
#
# glGetUniformBlockIndex: retrieve the index of a named uniform block
# glGetUniformIndices: retrieves the indices of a number of uniforms within program
# 
####################################################################################################

####################################################################################################

from six.moves import xrange

####################################################################################################

import logging
import os
import re

import numpy as np

####################################################################################################

from . import GL
from . import Type as GlType
from ..Tools.AttributeDictionaryInterface import (AttributeDictionaryInterface, AttributeDictionaryInterfaceDescriptor)
from ..Tools.Singleton import SingletonMetaClass

####################################################################################################

_module_logger = logging.getLogger(__name__)

####################################################################################################

class GlShader(object):

    """ This class defines a shader source code.

    Instances have an internal source code buffer to accumulate the source code before to compile
    it.  We can get the content of this buffer using the :func:`str`.  And we can test if the shader
    is compiled using a Boolean evaluation of the instance.

    The shader type can be passed to the constructor or retrieved from a source file, where a
    comment line with the following pattern must be present::
        
          // #shader_type SHADER_TYPE
        
    where *SHADER_TYPE* could be either *vertex*, *fragment* and *geometry*. It is case insensitive.

    Source files are preprocessed so as to replace line of the form::

      #include(file.glsl)
    
    the path is relative to the parent source file.
    """

    _logger = _module_logger.getChild('GlShader')

    # Fixme: use enumerate class?
    FRAGMENT_SHADER = GL.GL_FRAGMENT_SHADER
    if hasattr(GL, 'GL_GEOMETRY_SHADER'):
        GEOMETRY_SHADER = GL.GL_GEOMETRY_SHADER
    else:
        GEOMETRY_SHADER = None # Fixme: from wrapper TypeError: an integer is required
    VERTEX_SHADER = GL.GL_VERTEX_SHADER
    # TESSELATION_CONTROL_SHADER = GL.GL_TESS_CONTROL_SHADER
    # TESSELATION_EVALUATION_SHADER = GL.GL_TESS_EVALUATION_SHADER

    SHADER_TYPES = (VERTEX_SHADER,
                    FRAGMENT_SHADER,
                    GEOMETRY_SHADER,
                    # TESSELATION_CONTROL_SHADER,
                    # TESSELATION_EVALUATION_SHADER,
                    )

    ##############################################
    
    def __init__(self, shader_type=None, file_name=None, source_code=None):

        if shader_type is not None:
            self._set_shader_type(shader_type)
        else:
            self._shader_type = None

        self.clear_source()
        if source_code is not None:
            self.load_from_string(source_code)
        elif file_name is not None:
            self.load_from_file(file_name)

        self._shader_id = GL.glCreateShader(self._shader_type)

    ##############################################
    
    def __delx__(self):

        # Fixme: delx

        self._logger("Delete Shader %u" % (self._shader_id))
        GL.glDeleteShader(self._shader_id)

    ##############################################
    
    def __bool__(self):

        return self._compiled

    ##############################################
    
    def __str__(self):

        return self._source

    ##############################################
    
    def clear_source(self):

        """ Clear the internal source code buffer. """

        self._source = ''
        self._compiled = False

    ##############################################

    def _set_shader_type(self, shader_type):

        """ Set the shader type.  It raise an exception if the shader is already set. """

        if self._shader_type is not None:
            raise NameError("Shader type is already defined")
        if shader_type not in self.SHADER_TYPES:
            raise ValueError("Wrong shader type")
        self._shader_type = shader_type

    ##############################################

    def _set_shader_type_from_source_code(self):

        """ Set the shader type from the source code. """

        shader_type_pattern = '// #shader_type'
        start_position = self._source.find(shader_type_pattern)
        if start_position >= 0:
            stop_position = self._source.find('\n', start_position)
            shader_type_name = self._source[start_position + len(shader_type_pattern):stop_position].strip()
            shader_type = getattr(self, shader_type_name.upper() + '_SHADER')
            self._set_shader_type(shader_type)

    ##############################################
    
    def load_from_string(self, source):

        """ Append the source string to the internal buffer. """

        self._source += source
        self._compiled = False

    ##############################################
    
    def _preprocessor(self, source_code, path):

        """ Preprocess the source code. """

        # Fixme: remove commented lines!
        include_start_pattern = '#include('
        include_stop_pattern = ')'
        current_position = 0
        while True:
            include_start_position = source_code.find(include_start_pattern, current_position)
            if include_start_position >= 0:
                include_stop_position = source_code.find(include_stop_pattern, include_start_position)
                if include_stop_position:
                    include_file_name = source_code[include_start_position + len(include_start_pattern):include_stop_position]
                    self._logger.debug("Include GLSL file %s" % (include_file_name))
                    # Fixme: implement -I like search path
                    include_source_code = self._load_from_file(os.path.join(path, include_file_name))
                    current_position = include_stop_position +1
                    source_code = source_code[:include_start_position] \
                        + '/* Begin include ' + include_file_name + ' */\n' \
                        + include_source_code \
                        + '/* End include ' + include_file_name + ' */\n' \
                        + source_code[current_position:]
                else:
                    line_count = source_code.count('\n', end=include_start_position)
                    raise ValueError("Malformed include at line %u" % (line_count))
            else:
                break
                    
        return source_code

    ##############################################
    
    def _load_from_file(self, file_name):

        """ Load source code from file and preprocess it. """

        with open(file_name, 'r') as f:
            source_code = f.read()
        source_code = self._preprocessor(source_code, path=os.path.dirname(file_name))

        return source_code

    ##############################################
    
    def load_from_file(self, file_name):

        """ Load the source code from the file given by *file_name*, preprocess it and append it to
        the internal buffer. The shader type is determined from the source.
        """

        self.load_from_string(self._load_from_file(file_name))
        self._set_shader_type_from_source_code()

    ##############################################
    
    def compile(self):

        """ Compile the shader. """

        if not self._source:
            raise ValueError('Empty source code shader')

        GL.glShaderSource(self._shader_id, self._source)
        GL.glCompileShader(self._shader_id)

        log, length = GL.glGetShaderInfoLog(self._shader_id, 1000)
        message = """
Compile Shader:
  -----------------------------------------------------------------------------
%s
  -----------------------------------------------------------------------------
Log:
  -----------------------------------------------------------------------------
%s
  -----------------------------------------------------------------------------
"""
        self._logger.debug(message % (self._source, log))

        # Fixme: high level function
        # Fixme: shader doesn't have name
        if not GL.glGetShaderiv(self._shader_id, GL.GL_COMPILE_STATUS):
            source_lines = self._source.splitlines()
            last_line = len(source_lines) -1
            # Fixme: count digit of last_line
            source_lines = ['%3u| ' % (location) + source_lines[location]
                            for location in xrange(last_line +1)]
            self._logger.info('Source:\n' + '\n'.join(source_lines))
            self._logger.error(log)
            for line in log.splitlines():
                match = re.match(r'\d\((\d+)\) : error', line)
                # intel: # 0:18(10): error: no precision specified this scope for type `vec4'
                if match is not None:
                    location = int(match.group(1))
                    context_size = 1
                    lower_location = max(0, location-context_size)
                    upper_location = min(location+context_size, last_line)
                    context_source_lines = source_lines[lower_location:upper_location +1]
                    self._logger.error('\n' + line + '\n\n' + '\n'.join(context_source_lines))
            raise ValueError('GLSL Compilation Error')

        self._compiled = True

####################################################################################################

def sorted_by_location(a_list):
    return sorted(a_list, key=lambda a: a._location)

def sorted_by_offset(a_list):
    return sorted(a_list, key=lambda a: a._offset)

####################################################################################################

class GlVariable(object):

    """ This class is a base class for Attributes and Uniforms. """

    #: This attribute is used to set the variable label: attribute or uniform.
    VARIABLE_LABEL = None

    ##############################################
    
    def __init__(self, shader_program, name, location, gl_type, size,
                 within_uniform_block=False, offset=-1,
                 ):

        """ The argument *shader_program* is the :class:`GlShaderProgram` instance, *name* is the
        name of the uniform in the source code, *location* is the location of the uniform, *gl_type*
        the OpenGL data type and *size* is the number of elements of the uniform.
        """

        self._shader_program = shader_program
        self._name = name
        self._location = location
        self._gl_type = gl_type
        self._size = size
        self._within_uniform_block = within_uniform_block
        self._offset = offset

    ##############################################
    
    def __repr__(self):

        if self._size > 1:
            size_text = '[%u]' % self._size
        else:
            size_text = ''
        template = ' %(_name)s = %(_gl_type)s'
        if self._within_uniform_block:
            template = '[offset: %(_offset)3u]' + template
        else:
            template = self.VARIABLE_LABEL + '[%(_location)2u]' + template

        return (template % self.__dict__) + size_text

####################################################################################################

class GlUniform(GlVariable):

    """ This class defines a uniform within a shader program. """

    VARIABLE_LABEL = 'Uniform'

    ##############################################
    
    def get(self):

        """ Return the uniform value(s). """

        # Fixme check
        return self._gl_type.uniform_get_v(self._shader_program.program_id, self._location)

    ##############################################
    
    def set(self, value):

        """ Set the uniform value(s). """

        value = np.asarray([value], dtype=self._gl_type.dtype)
        self._gl_type.program_uniform_set_v(self._shader_program.program_id, self._location, value)
        # self._gl_type.uniform_set(self._location, value) # require binding

####################################################################################################

class GlUniformSampler(GlUniform):

    """ This class defines a sampler uniform. """

    pass

####################################################################################################

class GlUniformVariable(GlUniform):

    """ This class defines a variable uniform. """

    pass

####################################################################################################

class GlUniformNd(GlUniform):

    """ This class is a base class for vector and matrix uniforms. """

    ##############################################
    
    def get(self):

        """ Return the uniform value(s). """

        value = np.zeros(self._gl_type.shape, dtype=self._gl_type.dtype)
        self._gl_type.uniform_get_v(self._shader_program.program_id, self._location, value)

        return value

    ##############################################
    
    def _check_value(self, value):

        """ Check the value dimension and shape. """

        if value.ndim != self._gl_type.number_of_dimensions:
            raise ValueError("Wrong array dimension for %s = %s" % (self._gl_type, value))
        if value.shape != self._gl_type.shape:
            raise ValueError("Wrong array shape for %s = %s" % (self._gl_type, value))

####################################################################################################

class GlUniformVector(GlUniformNd):

    """ This class defines a vector uniform. """

    ##############################################
    
    def set(self, value):

        """ Set the uniform value(s). """

        if len(value) or not isinstance(value, np.ndarray):
            value = np.asarray(value, dtype=self._gl_type.dtype)
        self._check_value(value)

        #!# self._gl_type.program_uniform_set_v(self._shader_program.program_id, self._location, 1, value)
        self._gl_type.uniform_set_v(self._location, value) # require binding

####################################################################################################

class GlUniformMatrix(GlUniformNd):

    """ This class defines a matrix uniform. """

    ##############################################
    
    def set(self, value):

        """ Set the uniform value(s). """

        value = np.asarray(value, dtype=self._gl_type.dtype)
        self._check_value(value)

        # tranpose = True
        self._gl_type.program_uniform_set_v(self._shader_program.program_id, self._location, 1, True, value)
        # self._gl_type.uniform_set_v(self._location, 1, True, value) # require binding

####################################################################################################

class GlShaderProgramUniforms(AttributeDictionaryInterfaceDescriptor):

    """ This class is a wrapper to access the uniforms within a shader program. """

    ##############################################
    
    def __init__(self, shader_program):

        super(GlShaderProgramUniforms, self).__init__()

        program_id = shader_program.program_id
        number_of_active_uniforms = GL.glGetProgramiv(program_id, GL.GL_ACTIVE_UNIFORMS)
        for i in xrange(number_of_active_uniforms):

            name, length, size, gl_type_id = GL.glGetActiveUniform(program_id, i, 1000)
            location = GL.glGetUniformLocation(program_id, name)
            if location == -1: # uniform block
                continue

            gl_type = GlType.gl_types[gl_type_id]

            if size > 1:
                raise NotImplementedError("Array uniform is not implemented")

            if isinstance(gl_type, GlType.GlVariableType):
                cls = GlUniformVariable
            elif isinstance(gl_type, GlType.GlVectorType):
                cls = GlUniformVector
            elif isinstance(gl_type, GlType.GlMatrixType):
                cls = GlUniformMatrix
            elif isinstance(gl_type, GlType.GlSamplerType):
                cls = GlUniformSampler
            else:
                raise NotImplementedError()

            instance = cls(shader_program, name, location, gl_type, size)
            self._dictionary[name] = instance

####################################################################################################

class GlUniformBlock(AttributeDictionaryInterface):

    """ This class defines an uniform block. """

    ##############################################
    
    def __init__(self, name, location, uniforms):

        super(GlUniformBlock, self).__init__()

        object.__setattr__(self, '_uniform_block_name', name)
        object.__setattr__(self, '_uniform_block_location', location)

        for uniform in uniforms:
            self._dictionary[uniform._name] = uniform

    ##############################################
    
    def uniform_block_name(self):

        return self._uniform_block_name

    ##############################################
    
    def uniform_block_location(self):

        return self._uniform_block_location

    ##############################################
    
    def __str__(self):

        text = 'Uniform Block[%2u]: %s\n' % (self.uniform_block_location(), self.uniform_block_name())
        for uniform in sorted_by_offset(self):
            text += ' - %s\n' % (uniform)
        text += '\n'

        return text

####################################################################################################

class GlShaderProgramUniformBlocks(AttributeDictionaryInterface):

    """ This class is a wrapper to access the uniform blocks within a shader program. """

    ##############################################
    
    def __init__(self, shader_program):

        super(GlShaderProgramUniformBlocks, self).__init__()

        program_id = shader_program.program_id

        number_of_active_uniform_blocks = GL.glGetProgramiv(program_id, GL.GL_ACTIVE_UNIFORM_BLOCKS)
        for uniform_block_location in xrange(number_of_active_uniform_blocks):
            uniform_block_name = GL.glGetActiveUniformBlockName(program_id, uniform_block_location)
            indices = GL.glGetActiveUniformBlockiv(program_id, uniform_block_location,
                                                   GL.GL_UNIFORM_BLOCK_ACTIVE_UNIFORM_INDICES)
            # Fixme:
            if isinstance(indices, np.int32):
                indices = (int(indices),)
            uniforms = []
            for i in indices:
                # Fixme: Mesa ?
                if i == -1:
                    continue

                name, length, size, gl_type_id = GL.glGetActiveUniform(program_id, i, 1000)
                offset = GL.glGetActiveUniformsiv(program_id, i, GL.GL_UNIFORM_OFFSET)
                gl_type = GlType.gl_types[gl_type_id]

                if size > 1:
                    raise NotImplementedError("Array uniform is not implemented")

                if isinstance(gl_type, GlType.GlVariableType):
                    cls = GlUniformVariable
                elif isinstance(gl_type, GlType.GlVectorType):
                    cls = GlUniformVector
                elif isinstance(gl_type, GlType.GlMatrixType):
                    cls = GlUniformMatrix
                elif isinstance(gl_type, GlType.GlSamplerType):
                    cls = GlUniformSampler
                else:
                    raise NotImplementedError()

                instance = cls(shader_program, name, -1, gl_type, size,
                               within_uniform_block= True, offset=offset)
                uniforms.append(instance)
            self._dictionary[uniform_block_name] = GlUniformBlock(uniform_block_name, uniform_block_location, uniforms)

####################################################################################################

class GlVertexAttribute(GlVariable):

    """ This class defines a vertex attributes. """

    VARIABLE_LABEL = 'Attribute'

    ##############################################
    
    def bind_to_buffer(self, vbo):

        """ Bind the vertex attribute to a Vertex Buffer Object. """

        vbo.bind_at_location(self._location)

####################################################################################################

class GlShaderProgramAttributes(AttributeDictionaryInterface):

    """ This class is a wrapper to access the vertex attributes within a shader program. """

    ##############################################
    
    def __init__(self, shader_program):

        super(GlShaderProgramAttributes, self).__init__()

        program_id = shader_program.program_id
        
        number_of_active_attributes = GL.glGetProgramiv(program_id, GL.GL_ACTIVE_ATTRIBUTES)
        for i in xrange(number_of_active_attributes):
            name, length, size, gl_type_id =  GL.glGetActiveAttrib(program_id, i, 1000)
            location = GL.glGetAttribLocation(program_id, name)
            gl_type = GlType.gl_types[gl_type_id]
            self._dictionary[name] = GlVertexAttribute(shader_program, name, location, gl_type, size)

    ##############################################
    
    def __setattr__(self, name, value):

        raise NotImplementedError()

####################################################################################################

class GlShaderProgramInterfaceUniformBlock(object):

    """ This class defines a programming interface for an uniform block as a pair (name,
    binding_point)
    """

    ##############################################
    
    def __init__(self, name, binding_point):

        self.name = name
        self.binding_point = binding_point

####################################################################################################

class GlShaderProgramInterfaceAttribute(object):

    """ This class defines a programming interface for an attribute as a pair (name, location)
    """

    ##############################################
    
    def __init__(self, name, location):

        self.name = name
        self.location = location

    ##############################################
    
    def bind_to_buffer(self, vbo):

        """ Bind the vertex attribute to a Vertex Buffer Object. """

        vbo.bind_at_location(self.location)

####################################################################################################

class GlShaderProgramInterface(object):

    """ This class defines a programming interface for a program.
    """

    ##############################################
    
    def __init__(self, uniform_blocks, attributes):

        self._init_uniform_blocks(uniform_blocks)
        self._init_attributes(attributes)

    ##############################################
    
    def _init_uniform_blocks(self, uniform_blocks):

        self.uniform_blocks = AttributeDictionaryInterface()
        for binding_point, name in enumerate(uniform_blocks):
            pair = GlShaderProgramInterfaceUniformBlock(name, binding_point)
            self.uniform_blocks._dictionary[name] = pair

    ##############################################
    
    def _init_attributes(self, attributes):

        self.attributes = AttributeDictionaryInterface()
        for location, name in enumerate(attributes):
            pair = GlShaderProgramInterfaceAttribute(name, location)
            self.attributes._dictionary[name] = pair

####################################################################################################

class GlShaderProgram(object):

    """ This class defines a shader program.

    We can access the uniforms and vertex attributes defined in the shader program using the two
    class attributes: *uniforms* and *attributes*, respectively.  Both act as class that has an
    attribute for each uniform and vertex attribute.

    For example we can set a *colour* uniform using::

      shader_program.uniforms.colour = (1., 1., 1.)

    and get back its values using::

      shader_program.uniforms.colour

    We can also use a dictionary interface::

       # to set the values
       shader_program.uniforms['colour'] = (1., 1., 1.)
       # to get the values
       shader_program.uniforms['colour']

    Moreover we can test if an uniform is defined using::

      'colour' in shader_program.uniforms

    Similarly, we can access a vertex attribute using::

      shader_program.attributes.positions

    For example to attach a VBO::

      shader_program.attributes.positions.bind_to_buffer(positions_vbo)

    """

    _logger = _module_logger.getChild('GlShaderProgram')

    ##############################################
    
    def __init__(self, name):

        self._name = name
        self.program_id = GL.glCreateProgram()
        self.interface = None
        self._linked = False
        self._active = False

        self.uniforms = None
        self.uniform_blocks = None
        self.attributes = None

    ##############################################
    
    def __delx__(self):

        self._logger("Delete Program %u" % (self.program_id))
        GL.glDeleteProgram(self.program_id)

    ##############################################
    
    def attach_shader(self, shader):

        """ Attach a shader. """

        if not bool(shader):
            shader.compile()

        GL.glAttachShader(self.program_id, shader._shader_id)

    ##############################################
    
    def link(self):

        """ Link the program. """

        GL.glLinkProgram(self.program_id)

        length = GL.glGetProgramiv(self.program_id, GL.GL_INFO_LOG_LENGTH)
        log, length = GL.glGetProgramInfoLog(self.program_id, length)
        message = """
Link program '%s'
Log:
  -----------------------------------------------------------------------------
%s
  -----------------------------------------------------------------------------
"""
        self._logger.debug(message % (self._name, log))
        if not GL.glGetProgramiv(self.program_id, GL.GL_LINK_STATUS):
            raise ValueError(log)

        self._linked = True

        self.uniforms = GlShaderProgramUniforms(self)
        self.uniform_blocks = GlShaderProgramUniformBlocks(self)
        self.attributes = GlShaderProgramAttributes(self)

        self._logger.debug(str(self))

    ##############################################
    
    def unbind(self):

        """ Unbind the shader. """

        GL.glUseProgram(0)
        self._active = False

    ##############################################
    
    def bind(self):

        """ Bind the shader. """

        GL.glUseProgram(self.program_id)
        self._active = True

    ##############################################
    
    def bind_attribute_location_array(self, name, location):

        """ Bind an attribute location. The program should not be linked. """

        if self._linked:
            raise NameError("Attribute location binding must be done before linking.")

        GL.glBindAttribLocation(self.program_id, location, name)

    ##############################################
    
    def set_program_interface(self, program_interface):

        """ Set the programming interface. """

        self.interface = program_interface
        for attribute in self.interface.attributes:
            self.bind_attribute_location_array(attribute.name, attribute.location)

    ##############################################
    
    def set_uniform_block_binding(self, name, binding_point):

        """ Set the binding point for an uniform block. """

        location = self.uniform_blocks[name].uniform_block_location()
        GL.glUniformBlockBinding(self.program_id, location, binding_point)

    ##############################################
    
    def set_uniform_block_bindings(self):

        """ Set the uniform block binding points as defined by the programming interface. """

        for uniform_block in self.interface.uniform_blocks:
            self.set_uniform_block_binding(uniform_block.name, uniform_block.binding_point)

    ##############################################
    
    def __repr__(self):

        text = "Shader Program '%s':\n" % (self._name)
        text += 'Uniform Blocks:\n'
        for uniform_block in self.uniform_blocks:
            text += str(uniform_block)
        text += 'Uniforms:\n'
        for uniform in sorted_by_location(self.uniforms):
            text += ' - %s\n' % (uniform)
        text += '\n'
        text += 'Attributes:\n'
        for attribute in sorted_by_location(self.attributes):
            text += ' - %s\n' % (attribute)

        return text

####################################################################################################

class GlShaderManager(object):

    """ This class provides a shader manager where each shader or program are identified by a name
    and the shader sources are loaded from files.

    The shaders or programs can be accessed using an attribute or a dictionary interface. For
    example to get the shader *fixed_fragment* we can use either::

      shader_manager.fixed_fragment
      shader_manager.['fixed_fragment']

    We can test if an identifier exists using::

      'fixed_fragment' in shader_manager
    """

    __metaclass__ = SingletonMetaClass

    # Fixme: -> attributeDictionaryInterface

    ##############################################
    
    def __init__(self):

        self._shaders = {}
        self._programs = {}

    ##############################################
    
    def __contains__(self, name):

        return name in self._shaders or name in self._programs

    ##############################################
    
    def __getattr__(self, name):

        item = self._programs.get(name, None)
        if item is None:
            item = self._shaders.get(name, None)
            if item is None:
                raise KeyError(name)

        return item

    ##############################################
    
    __getitem__ = __getattr__

    ##############################################
    
    def has_visual(self):

        return bool(GL.glCreateShader)

    ##############################################
    
    def load_from_file(self, shader_name, shader_file_name):

        """ Load a shader from a source file and compile it. This shader is identified by
        *shader_name*.
        """

        if shader_name in self:
            raise NameError("Shader %s is already defined" % (shader_name))

        shader = GlShader(file_name=shader_file_name)
        shader.compile()
        self._shaders[shader_name] = shader

        return shader

    ##############################################
    
    def link_program(self, program_name, shader_list,
                     program_interface=None,
                     shader_program_class=GlShaderProgram,
                     shader_program_args=(),
                     ):

        """ Link a program with the given list of shader names. This program is identified by
        *shader_name*.  The argument *program_interface* can be used to set the program interface.
        """

        if program_name in self:
            raise NameError("Program %s is already defined" % (program_name))

        shader_program = shader_program_class(program_name, *shader_program_args)
        for shader_name in shader_list:
            shader_program.attach_shader(self[shader_name])
        # Fixme: move to link ?
        if program_interface is not None:
            shader_program.set_program_interface(program_interface)
        shader_program.link()
        if program_interface is not None:
            shader_program.set_uniform_block_bindings()
        self._programs[program_name] = shader_program

        return shader_program

####################################################################################################
#
# End
#
####################################################################################################
