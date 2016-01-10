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

"""This module implements a CFFI wrapper for OpenGL based on information provided by the OpenGL
API :class:`PyOpenGLng.GlApi`.
"""

####################################################################################################

import collections
import ctypes
import logging
import os
import subprocess
import sys
import types

import numpy as np

from cffi import FFI
ffi = FFI()

####################################################################################################

from .PythonicWrapper import PythonicWrapper
import PyOpenGLng.Config as Config

####################################################################################################

_module_logger = logging.getLogger(__name__)

####################################################################################################

# Fixme: unsigned comes from typedef
#  not gl, but translated c type in fact
__to_ctypes_type__ = {
    'char':ctypes.c_char,
    'int8_t':ctypes.c_byte, # c_int8
    'uint8_t':ctypes.c_ubyte, # c_uint8
    'unsigned char':ctypes.c_ubyte,
    'short':ctypes.c_short,
    'unsigned short':ctypes.c_ushort,
    'int32_t':ctypes.c_int32,
    'int':ctypes.c_int32, # not 64-bit integer!
    'unsigned int':ctypes.c_uint32,
    'int64_t':ctypes.c_int64,
    'uint64_t':ctypes.c_uint64,
    'float':ctypes.c_float,
    'float_t':ctypes.c_float,
    'double':ctypes.c_double,
    'intptr_t':ctypes.c_void_p, # ?
    'ptrdiff_t':ctypes.c_void_p, # int64 ?
    'ssize_t':ctypes.c_uint64, # ?
    }

__numpy_to_ctypes_type__ = {
    '<u1':ctypes.c_uint8,
    '<u2':ctypes.c_uint16,
    '<u4':ctypes.c_uint32,
    '<u8':ctypes.c_uint64,
    '<i1':ctypes.c_int8,
    '<i2':ctypes.c_int16,
    '<i4':ctypes.c_int32,
    '<i8':ctypes.c_int64,
    '<f4':ctypes.c_float,
    '<f8':ctypes.c_double,
    }

def to_ctypes_type(parameter):
    """ Return the ctypes type corresponding to a parameter. """
    if parameter.is_generic_pointer():
        return ctypes.c_void_p
    else:
        c_type = str(parameter.c_type)
        return __to_ctypes_type__[c_type]

def numpy_to_ctypes_type(array):
    """ Return the ctypes type corresponding to a Numpy array data type. """
    return __numpy_to_ctypes_type__.get(array.dtype.str, None)

def to_cffi_type(parameter):
    """ Return the ctypes type corresponding to a parameter. """
    if parameter.is_generic_pointer():
        return 'void *'
    else:
        return str(parameter.c_type)

####################################################################################################

__command_directives__ = {
    'glShaderSource':{'length':None,},
    # length = NULL for null terminated string and solve len(pointer_parameters) == 2
    }

####################################################################################################

def check_numpy_type(array, ctypes_type):
    """ Check the Numpy array data type is same as *ctypes_type*. """
    #!# if numpy_to_ctypes_type(array) != ctypes_type:
    #!#     raise ValueError("Type mismatch: %s instead of %s" % (array.dtype, ctypes_type.__name__))
    return True

####################################################################################################

class GlEnums(object):

    ##############################################

    def __iter__(self):

        for attribute in sorted(self.__dict__.keys()):
            if attribute.startswith('GL_'):
                yield attribute

####################################################################################################

class GlCommands(object):

    ##############################################

    def __iter__(self):

        # for attribute, value in self.__dict__.iteritems():
        #     if attribute.startswith('gl'):
        #         yield value

        for attribute in sorted(self.__dict__.keys()):
            if attribute.startswith('gl'):
                yield getattr(self, attribute)

####################################################################################################

class ParameterWrapperBase(object):

    # Fixme: wrapper, translator

    """ Base class for parameter wrapper. """

    ##############################################

    def repr_string(self, parameter):

        return self.__class__.__name__ + '<' + parameter.format_gl_type() + '> ' + parameter.name

    ##############################################

    def __repr__(self):

        return self.repr_string(self._parameter)

####################################################################################################

class ParameterWrapper(ParameterWrapperBase):

    """ Translate a fundamental type. """

    ##############################################

    def __init__(self, parameter):

        self._parameter = parameter
        self._location = parameter.location # Fixme: doublon?
        self._type = to_cffi_type(parameter)

    ##############################################

    def from_python(self, parameter, c_parameters, keepalive):

        c_parameters[self._location] = ffi.cast(self._type, parameter)

        return None

####################################################################################################

class PointerWrapper(ParameterWrapperBase):

    """ Translate a pointer.

    This wrapper handle all the case which are not managed by a :class:`ReferenceWrapper`, an
    :class:`InputArrayWrapper` or an :class:`OutputArrayWrapper`.

    These parameters are identified in the prototype as a pointer that doesn't have a size parameter
    or a computed size.

    If the pointer type is *char* then user must provide a string or a Python object with a
    :meth:`__str__` method, else a Numpy array must be provided and the data type is only checked if
    the pointer is not generic.

    If the parameter value is :obj:`None`, the value is passed as is.
    """

    _logger = _module_logger.getChild('PointerWrapper')

    ##############################################

    def __init__(self, parameter):

        # Fixme: same as ...
        self._parameter = parameter
        self._location = parameter.location
        self._type = to_cffi_type(parameter)

    ##############################################

    def from_python(self, parameter, c_parameters, keepalive):

        if self._type == 'char' and self._parameter.const: # const char *
            self._logger.debug('const char *')
            ctypes_parameter = ffi.new('char []', str(parameter))
        elif isinstance(parameter, np.ndarray):
            self._logger.debug('ndarray')
            if self._type != 'void *':
                check_numpy_type(parameter, self._type)
            ctypes_parameter = ffi.cast(self._type + ' *',   parameter.__array_interface__['data'][0]) # buffer interface ???
        elif parameter is None:
            self._logger.debug('None')
            ctypes_parameter = ffi.NULL # already done
        else:
            raise NotImplementedError
        c_parameters[self._location] = ctypes_parameter

        return None

####################################################################################################

class ReferenceWrapper(ParameterWrapperBase):

    """ Translate a parameter passed by reference.

    A parameter passed by reference is identified in the prototype as a non const pointer of a fixed
    size of 1.

    A reference parameter is removed in the Python prototype and the value set by the command is
    pushed out in the return.
    """

    ##############################################

    def __init__(self, parameter):

        # Fixme: same as ...
        self._parameter = parameter
        self._location = parameter.location
        self._type = to_cffi_type(parameter)

    ##############################################

    def from_python(self, c_parameters, keepalive):

        ctypes_parameter = ffi.new(self._type + ' *')
        c_parameters[self._location] = ctypes_parameter
        to_python_converter = ValueConverter(ctypes_parameter)

        return to_python_converter

####################################################################################################

class ArrayWrapper(ParameterWrapperBase):

    """ Base class for Array Wrapper. """

    ##############################################

    def __init__(self, size_parameter):

        # Fixme: size_multiplier

        # excepted some particular cases
        pointer_parameter = size_parameter.pointer_parameters[0] 

        # Fixme: for debug
        self._size_parameter = size_parameter
        self._pointer_parameter = pointer_parameter

        self._size_location = size_parameter.location
        self._size_type = to_cffi_type(size_parameter)
        self._pointer_location = pointer_parameter.location
        self._pointer_type = to_cffi_type(pointer_parameter)

    ##############################################

    def __repr__(self):

        return self.repr_string(self._pointer_parameter)

####################################################################################################

class OutputArrayWrapper(ArrayWrapper):

    """ Translate an output array parameter.
    
    If the pointer is generic, then the array is passed as an Numpy array and the size is specified
    in byte. <<CHECK>>

    If the pointer is of \*char type, then the size is passed by the user and a string is returned.

    If the user passes an Numpy array, then the data type is checked and the size is set by the
    wrapper.

    If the user passes a size, then a Numpy (or a list) array is created and returned.
    <<size_parameter_threshold>>

    """

    _logger = _module_logger.getChild('OutputArrayWrapper')

    size_parameter_threshold = 20

    ##############################################

    def from_python(self, parameter, c_parameters, keepalive):

        # print self._pointer_parameter.long_repr(), self._pointer_type, type(parameter)

        if self._pointer_type == 'void *':
            self._logger.debug('void *')
            # Generic pointer: thus the array data type is not specified by the API
            if isinstance(parameter, np.ndarray):
                # The output array is provided by user and the size is specified in byte
                array = parameter
                c_parameters[self._size_location] = ffi.cast(self._size_type, array.nbytes)
                ctypes_parameter = ffi.cast('void *',   array.__array_interface__['data'][0])
                c_parameters[self._pointer_location] = ctypes_parameter
                return None
            else:
                raise NotImplementedError
        elif self._pointer_type == 'char':
            self._logger.debug('char *')
            # The array size is provided by user
            size_parameter = parameter
            c_parameters[self._size_location] = ffi.cast(self._size_type, size_parameter)
            ctypes_parameter = ffi.new('char []', size_parameter)
            c_parameters[self._pointer_location] = ctypes_parameter
            to_python_converter = StringConverter(ctypes_parameter)
            return to_python_converter
        elif isinstance(parameter, np.ndarray):
            self._logger.debug('ndarray')
            # Typed pointer
            # The output array is provided by user
            array = parameter
            check_numpy_type(array, self._pointer_type)
            c_parameters[self._size_location] = ffi.cast(self._size_type, array.size)
            ctypes_parameter = ffi.cast(self._pointer_type + ' *',   array.__array_interface__['data'][0])
            c_parameters[self._pointer_location] = ctypes_parameter
            return None
        else:
            self._logger.debug('else')
            # Typed pointer
            # The array size is provided by user
            size_parameter = parameter
            c_parameters[self._size_location] = ffi.cast(self._size_type, size_parameter)
            if size_parameter >= self.size_parameter_threshold:
                ctypes_pointer_type = to_ctypes_type(self._pointer_parameter)
                array = np.zeros((size_parameter), dtype=ctypes_pointer_type)
                ctypes_parameter = ffi.cast(self._pointer_type + ' *',   array.__array_interface__['data'][0])
                to_python_converter = IdentityConverter(array)
            else:
                #!# array_type = self._pointer_type * size_parameter #!# ???
                ctypes_parameter = ffi.new(self._pointer_type + '[]', size_parameter)
                to_python_converter = ListConverter(ctypes_parameter)
            c_parameters[self._pointer_location] = ctypes_parameter
            return to_python_converter

####################################################################################################

class InputArrayWrapper(ArrayWrapper):

    _logger = _module_logger.getChild('InputArrayWrapper')

    ##############################################

    def from_python(self, array, c_parameters, keepalive):

        # print array
        # print self._pointer_parameter.long_repr()
        # print self._pointer_type

        if self._pointer_parameter.pointer == 2:
            if self._pointer_type == 'char': # Fixme: should be c_char_p
                if isinstance(array, str):
                    self._logger.debug('string -> const char **')
                    size_parameter = 1
                    strings = [ffi.new('char[]', array)]
                else:
                    self._logger.debug('string array -> const char **')
                    size_parameter = len(array)
                    strings = [ffi.new("char[]", line) for line in array]
                string_array = ffi.new("char *[]", strings)
                keepalive.append(strings)
                ctypes_parameter = string_array
            else:
                raise NotImplementedError
        elif isinstance(array, np.ndarray):
            self._logger.debug('ndarray')
            if self._pointer_type == 'void *':
                size_parameter = array.nbytes
            elif self._pointer_type == 'float': # fixme
                size_parameter = 1 # array.shape[0]
            # else:
            #     size_parameter = array.nbytes
            # ctypes_parameter = array.ctypes.data_as(ctypes.c_void_p)
            ctypes_parameter = ffi.cast(self._pointer_type + ' *',   array.__array_interface__['data'][0])
        elif isinstance(array, collections.Iterable):
            size_parameter = len(array)
            ctypes_parameter = ffi.new(self._pointer_type + '[]', array)
        else:
            raise ValueError(str(array))

        c_parameters[self._size_location] = ffi.cast(self._size_type, size_parameter)
        c_parameters[self._pointer_location] = ctypes_parameter

        return None

####################################################################################################

class ToPythonConverter(object):

    """ Base class for C to Python converter. """

    ##############################################

    def __init__(self, c_object):

        """ The parameter *c_object* is a ctype object. """

        self._c_object = c_object

####################################################################################################

class IdentityConverter(ToPythonConverter):
    """ Identity converter. """
    def __call__(self):
        return self._c_object

class ListConverter(ToPythonConverter):
    """ Convert the C object to a Python list. """
    def __call__(self):
        return list(self._c_object)

class ValueConverter(ToPythonConverter):
    """ Get the Python value of the ctype object. """
    def __call__(self):
        return self._c_object[0] #!#

class StringConverter(ToPythonConverter):
    """ Get the Python value of the ctype object. """
    def __call__(self):
        return ffi.string(self._c_object)

####################################################################################################

class CommandNotAvailable(Exception):
    pass

####################################################################################################

class GlCommandWrapper(object):

    _logger = _module_logger.getChild('GlCommandWrapper')

    ##############################################

    def __init__(self, wrapper, command):

        self._wrapper = wrapper
        self._command = command
        self._number_of_parameters = command.number_of_parameters
        self._call_counter = 0

        try:
            self._function = getattr(self._wrapper.libGL, str(command))
        except AttributeError:
            raise CommandNotAvailable("OpenGL function %s was no found in libGL" % (str(command)))

        # Only for simple prototype
        # argument_types = [to_ctypes_type(parameter) for parameter in command.parameters]
        # if argument_types:
        #     self._function.argtypes = argument_types

        command_directive = __command_directives__.get(str(command), None)

        self._parameter_wrappers = []
        self._reference_parameter_wrappers = []
        self._return_type_converter = None
        for parameter in command.parameters:
            if parameter.type in ('GLsync', 'GLDEBUGPROC'):
                raise NotImplementedError
            parameter_wrapper = None
            if command_directive and parameter.name in command_directive:
                # Fixme: currently used for unspecified parameters (value set to 0)
                pass # skip and will be set to None
            elif parameter.pointer:
                if parameter.size_parameter is None and parameter.array_size == 1:
                    # not const, array_size = 1 must be sufficient
                    parameter_wrapper = ReferenceWrapper(parameter)
                elif parameter.size_parameter is None or parameter.computed_size:
                    parameter_wrapper = PointerWrapper(parameter)
                else:
                    pass # skip and will be set by pointer parameter
            elif parameter.pointer_parameters: # size parameter
                # Fixme: len(pointer_parameters) > 1
                #   Only theses functions have len(pointer_parameters) > 1
                #     glAreTexturesResident
                #     glGetDebugMessageLog
                #     glPrioritizeTextures 
                #     glShaderSource
                pointer_parameter = parameter.pointer_parameters[0]
                if pointer_parameter.const:
                    parameter_wrapper = InputArrayWrapper(parameter)
                else:
                    parameter_wrapper = OutputArrayWrapper(parameter)
            else:
                parameter_wrapper = ParameterWrapper(parameter)
            if parameter_wrapper is not None:
                if isinstance(parameter_wrapper, ReferenceWrapper):
                    parameter_list = self._reference_parameter_wrappers
                else:
                    parameter_list = self._parameter_wrappers
                parameter_list.append(parameter_wrapper)
                
        return_type = command.return_type
        if return_type.type == 'GLsync':
            raise NotImplementedError
        elif return_type.type != 'void': # Fixme: .type or .c_type?
            # Fixme: -> to func?
            ctypes_type = to_ctypes_type(return_type)
            if return_type.pointer:
                if ctypes_type == ctypes.c_ubyte: # return type is char *
                    #!# ctypes_type = ctypes.c_char_p
                    self._return_type_converter = ffi.string
                else:
                    raise NotImplementedError
            #!# self._function.restype = ctypes_type
            self._return_void = False
        else:
            #!# self._function.restype = None
            self._return_void = True # Fixme: required or doublon?

        manual_page = self._manual_page()
        if manual_page is not None:
            doc = '%s - %s\n\n' % (self._command, manual_page.purpose)
        else:
            doc = ''
        parameter_doc = ', '.join([repr(parameter_wrapper) for parameter_wrapper in self._parameter_wrappers])
        self.__doc__ = doc + "%s (%s)" % (self._command, parameter_doc)

    ##############################################

    def __call__(self, *args, **kwargs):

        self._call_counter += 1

        if len(self._parameter_wrappers) != len(args):
            self._logger.warning("%s requires %u arguments, but %u was given\n  %s\n  %s",
                                 str(self._command), len(self._parameter_wrappers), len(args),
                                 self._command.prototype(),
                                 str([parameter_wrapper.__class__.__name__
                                      for parameter_wrapper in self._parameter_wrappers]))

        # Initialise the input/output parameter array
        c_parameters = [ffi.NULL]*self._number_of_parameters
        to_python_converters = []
        # Set the input parameters and append python converters for output
        keepalive = []
        # first process the given parameters
        for parameter_wrapper, parameter in zip(self._parameter_wrappers, args):
            to_python_converter = parameter_wrapper.from_python(parameter, c_parameters, keepalive)
            if to_python_converter is not None:
                to_python_converters.append(to_python_converter)
        # second process the parameters by reference
        for parameter_wrapper in self._reference_parameter_wrappers:
            to_python_converter = parameter_wrapper.from_python(c_parameters, keepalive)
            if to_python_converter is not None:
                to_python_converters.append(to_python_converter)

        self._logger.info('Call\n'
                          '  ' + self._command.prototype() + '\n'
                          '  ' + str([parameter_wrapper.__class__.__name__
                                      for parameter_wrapper in self._parameter_wrappers]) + '\n'
                          '  ' + str(c_parameters) + '\n'
                          '  ' + str([to_python_converter.__class__.__name__
                                      for to_python_converter in to_python_converters])
                          )

        result = self._function(*c_parameters)
        #!# CFFI: string must be converted
        if self._return_type_converter is not None:
            result = self._return_type_converter(result)

        # Check error
        if kwargs.get('check_error', False):
            self._wrapper.check_error()

        # Manage return
        if to_python_converters:
            output_parameters = [to_python_converter() for to_python_converter in to_python_converters]
            if self._return_void:
                # Extract uniq element
                # Fixme: to func?, gives some cases to explain
                if len(output_parameters) == 1:
                    output_parameter = output_parameters[0]
                    if isinstance(output_parameter, list) and len(output_parameter) == 1: # uniq output parameter is [a,]
                        # Fixme: could be worst than simpler, if we really expect a list
                        return output_parameter[0]
                    else:
                        return output_parameter
                else:
                    return output_parameters
            else:
                return [result] + output_parameters
        else:
            if not self._return_void:
                return result

    ##############################################

    def __repr__(self):

        return str(self._command.name) #!# + ' ' + str(self._function.argtypes) + ' -> ' + str(self._function.restype)

    ##############################################

    def _manual_page(self):

        command_name = str(self._command)
        for name in ['man' + str(i) for i in range(4, 1, -1)]:
            # Fixme: use API version mapping
            manual = self._wrapper._manuals[name]
            if command_name in manual:
                return manual[command_name]
        else:
            return None

    ##############################################

    def _xml_manual_name(self):

        # some commands are merged together: e.g. glVertexAttrib.xml
        page = self._manual_page()
        if page is not None:
            page_name = page.page_name
        else:
            page_name = str(self._command)
        return page_name + '.xml'

    ##############################################

    def xml_manual_path(self):

        return os.path.join(Config.Path.manual_path(self._wrapper.api_number), self._xml_manual_name())

    ##############################################

    def xml_manual_url(self, local=False):

        if local:
            return 'file://' + self.xml_manual_path()
        else:
            return 'http://www.opengl.org/sdk/docs/man/xhtml/' + self._xml_manual_name()

    ##############################################

    def manual(self, local=False):

        if sys.platform.startswith('linux'):
            url = self.xml_manual_url(local)
            browser = 'xdg-open'
            subprocess.Popen([browser, url])
            # import webbrowser
            # webbrowser.open(url)
        else:
            raise NotImplementedError

    ##############################################

    def help(self):

        # Fixme: help(instance)
        print(self.__doc__)

    ##############################################

    @property
    def call_counter(self):
        return self._call_counter

    ##############################################

    def reset_call_counter(self):
        self._call_counter = 0

####################################################################################################

class CffiWrapper(object):

    libGL = None

    _logger = _module_logger.getChild('CffiWrapper')

    ##############################################

    @classmethod
    def load_library(cls, libGL_name):

        basic_api = """
        const char* glGetString(int name);
        """
        ffi.cdef(basic_api)
        cls.libGL = ffi.dlopen(libGL_name)
        GL_VERSION = int('0x1F02', 16)
        version_string = cls.libGL.glGetString(GL_VERSION)
        if version_string != ffi.NULL:
            version_string = ffi.string(version_string)
        else:
            version_string = None

        return version_string

    ##############################################

    def __init__(self, gl_spec, api, api_number, profile=None, manuals=None):

        self._gl_spec = gl_spec
        self.api_number = api_number
        self._manuals = manuals

        api_enums, api_commands = self._gl_spec.generate_api(api, api_number, profile)
        self._init_enums(api_enums)
        self._init_commands(api_commands)

        #!# self._pythonic_wrapper = PythonicWrapper(self)

    ##############################################

    def _init_enums(self, api_enums):

        gl_enums = GlEnums()
        for enum in api_enums:
            # We don't provide more information on enumerants, use GlAPI instead
            enum_name, enum_value = str(enum), int(enum)
            # store enumerants and commands at the same level
            setattr(self, enum_name, enum_value)
            # store enumerants in a dedicated place
            setattr(gl_enums, enum_name, enum_value)
        self.enums = gl_enums

    ##############################################

    def _reload_library(self, api_commands):

        api_definition = ''
        for command in api_commands.values():
            prototype = command.prototype(with_size=False)
            if 'GLDEBUGPROC' not in prototype and 'GLsync' not in prototype: # Fixme:
                api_definition += prototype + ';\n'
        ffi.cdef(api_definition, override=True)

    ##############################################

    def _init_commands(self, api_commands):

        self._reload_library(api_commands)

        gl_commands = GlCommands()
        for command in api_commands.values():
            try:
                command_name = str(command)
                command_wrapper = GlCommandWrapper(self, command)
                # store enumerants and commands at the same level
                if hasattr(PythonicWrapper, command_name):
                    method = getattr(PythonicWrapper, command_name)
                    rebinded_method = types.MethodType(method.__func__, self, self.__class__)
                    setattr(self, command_name, rebinded_method)
                else:
                    setattr(self, command_name, command_wrapper)
                # store commands in a dedicated place
                setattr(gl_commands, command_name, command_wrapper)
            except NotImplementedError:
                self._logger.warn("Command %s is not supported by the wrapper", str(command))
            except CommandNotAvailable:
                self._logger.warn("Command %s is not implemented", str(command))
        self.commands = gl_commands

    ##############################################

    def check_error(self):

        error_code = self.glGetError()
        if error_code:
            error_message = self._error_code_message(error_code)
            raise NameError(error_message)

    ##############################################

    def _error_code_message(self, error_code):

        if not error_code:
            # GL_NO_ERROR: The value of this symbolic constant is guaranteed to be 0.
            return 'No error has been recorded.'
        else:
            if error_code == self.GL_INVALID_ENUM:
                return 'An unacceptable value is specified for an enumerated argument.'
            elif error_code == self.GL_INVALID_VALUE:
                return 'A numeric argument is out of range.'
            elif error_code == self.GL_INVALID_OPERATION:
                return 'The specified operation is not allowed in the current state.'
            elif error_code == self.GL_INVALID_FRAMEBUFFER_OPERATION:
                return 'The framebuffer object is not complete.'
            elif error_code == self.GL_OUT_OF_MEMORY:
                return 'There is not enough memory left to execute the command.'
            elif error_code == self.GL_STACK_UNDERFLOW:
                return 'An attempt has been made to perform an operation that would cause an internal stack to underflow.'
            elif error_code == self.GL_STACK_OVERFLOW:
                return 'An attempt has been made to perform an operation that would cause an internal stack to overflow.'
            else:
                raise NotImplementedError

    ##############################################

    def error_checker(self):

        return ErrorContextManager(self)

    ##############################################

    def called_commands(self):
        
        return [command for command in self.commands if command.call_counter]

    ##############################################

    def reset_call_counter(self):
        
        for command in self.commands:
            command.reset_call_counter()

####################################################################################################

class ErrorContextManager(object):

    ##############################################

    def __init__(self, wrapper):

        self._wrapper = wrapper

    ##############################################

    def __enter__(self):
        pass
    
    ##############################################
    
    def __exit__(self, type_, value, traceback):

        self._wrapper.check_error()

####################################################################################################
#
# End
#
####################################################################################################
