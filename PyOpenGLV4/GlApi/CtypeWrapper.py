####################################################################################################
#
# PyOpenGLV4 - An OpenGL V4 layer on top of PyOpengl.
# Copyright (C) 2013 Salvaire Fabrice
#
####################################################################################################

####################################################################################################

import collections
import ctypes
import logging

import numpy as np

####################################################################################################

_module_logger = logging.getLogger(__name__)

####################################################################################################

# Fixme: unsigned comes from typedef
__gl_to_ctypes_type__ = {
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

def gl_to_ctypes_type(parameter):
    c_type = str(parameter.c_type)
    if parameter.pointer and c_type == 'void':
        return ctypes.c_void_p
    else:
        return __gl_to_ctypes_type__[c_type]

def numpy_to_ctypes_type(array):
    return __numpy_to_ctypes_type__.get(array.dtype.str, None)

####################################################################################################

__command_directives__ = {
    'glShaderSource':{'length':None,},
    # length = NULL for null terminated string and solve len(back_ref) == 2
    }

####################################################################################################

def check_numpy_type(array, ctypes_type):
    if numpy_to_ctypes_type(array) != ctypes_type:
        raise ValueError("Type mismatch: %s instead of %s" % (array.dtype, ctypes_type.__name__))

####################################################################################################

class GlEnums(object):
    pass

####################################################################################################

class ParameterWrapper(object):

    ##############################################

    def __init__(self, parameter):

        self._location = parameter.location
        self._type = gl_to_ctypes_type(parameter)

    ##############################################

    def from_python(self, parameter, c_parameters):

        c_parameters[self._location] = self._type(parameter)

        return None

####################################################################################################

class PointerWrapper(object):

    ##############################################

    def __init__(self, parameter):

        self._location = parameter.location
        self._type = gl_to_ctypes_type(parameter)

    ##############################################

    def from_python(self, parameter, c_parameters):

        if isinstance(parameter, np.ndarray):
            array = parameter
            if self._type != ctypes.c_void_p:
                check_numpy_type(array, self._type)
            ctypes_parameter = array.ctypes.data_as(ctypes.POINTER(self._type))
            c_parameters[self._location] = ctypes_parameter
        else:
            raise NotImplementedError

        return None

####################################################################################################

class ReferenceWrapper(object):

    ##############################################

    def __init__(self, parameter):

        self._location = parameter.location
        self._type = gl_to_ctypes_type(parameter)

    ##############################################

    def from_python(self, c_parameters):

        ctypes_parameter = self._type()
        c_parameters[self._location] = ctypes.byref(ctypes_parameter)
        to_python_converter = ValueConverter(ctypes_parameter)

        return to_python_converter

####################################################################################################

class ArrayWrapper(object):

    ##############################################

    def __init__(self, size_parameter):

        # Fixme: size_multiplier

        # excepted some particular cases
        pointer_parameter = size_parameter.back_ref[0] 

        # Fixme: for debug
        self._size_parameter = size_parameter
        self._pointer_parameter = pointer_parameter

        self._size_location = size_parameter.location
        self._size_type = gl_to_ctypes_type(size_parameter)
        self._pointer_location = pointer_parameter.location
        self._pointer_type = gl_to_ctypes_type(pointer_parameter)

####################################################################################################

class OutputArrayWrapper(ArrayWrapper):

    size_parameter_threshold = 20

    ##############################################

    def from_python(self, parameter, c_parameters):

        # print self._pointer_parameter.long_repr(), self._pointer_type, type(parameter)

        if self._pointer_type == ctypes.c_void_p:
            # Generic pointer: thus the array data type is not specified by the API
            # The output array is provided by user
            array = parameter
            c_parameters[self._size_location] = self._size_type(array.size)
            ctypes_parameter = array.ctypes.data_as(ctypes.c_void_p)
            c_parameters[self._pointer_location] = ctypes_parameter
            return None
        if self._pointer_type == ctypes.c_char:
            # The array size is provided by user
            size_parameter = parameter
            c_parameters[self._size_location] = self._size_type(size_parameter)
            ctypes_parameter = ctypes.create_string_buffer(size_parameter)
            c_parameters[self._pointer_location] = ctypes_parameter
            to_python_converter = ValueConverter(ctypes_parameter)
            return to_python_converter
        elif isinstance(parameter, np.ndarray):
            # Typed pointer
            # The output array is provided by user
            array = parameter
            check_numpy_type(array, self._pointer_type)
            c_parameters[self._size_location] = self._size_type(array.size)
            ctypes_parameter = array.ctypes.data_as(ctypes.POINTER(self._pointer_type))
            c_parameters[self._pointer_location] = ctypes_parameter
            return None
        else:
            # Typed pointer
            # The array size is provided by user
            size_parameter = parameter
            c_parameters[self._size_location] = self._size_type(size_parameter)
            if size_parameter >= self.size_parameter_threshold:
                array = np.zeros((size_parameter), dtype=self._pointer_type)
                ctypes_parameter = array.ctypes.data_as(ctypes.POINTER(self._pointer_type))
                to_python_converter = IdentityConverter(array)
            else:
                array_type = self._pointer_type * size_parameter
                ctypes_parameter = array_type()
                to_python_converter = ListConverter(ctypes_parameter)
            c_parameters[self._pointer_location] = ctypes_parameter
            return to_python_converter

####################################################################################################

class InputArrayWrapper(ArrayWrapper):

    ##############################################

    def from_python(self, array, c_parameters):

        # print array
        # print self._pointer_parameter.long_repr()
        # print self._pointer_type

        if self._pointer_parameter.pointer == 2:
            if self._pointer_type == ctypes.c_char: # Fixme: should be c_char_p
                if isinstance(array, str):
                    size_parameter = 1
                    string_array_type = ctypes.c_char_p * 1
                    string_array = string_array_type(ctypes.c_char_p(array))
                else:
                    size_parameter = len(array)
                    string_array_type = ctypes.c_char_p * size_parameter
                    string_array = string_array_type(*[ctypes.c_char_p(x) for x in array])
                ctypes_parameter = string_array
            else:
                raise NotImplementedError
        elif isinstance(array, np.ndarray):
            if self._pointer_type == ctypes.c_void_p:
                size_parameter = array.size
            else:
                size_parameter = array.nbytes
            ctypes_parameter = array.ctypes.data_as(ctypes.c_void_p)
        elif isinstance(array, collections.Iterable):
            size_parameter = len(array)
            array_type = self._pointer_type * size_parameter
            ctypes_parameter = array_type(array)
        else:
            raise ValueError

        c_parameters[self._size_location] = self._size_type(size_parameter)
        c_parameters[self._pointer_location] = ctypes_parameter

        return None

####################################################################################################

class ToPythonConverter(object):

    ##############################################

    def __init__(self, c_object):

        self._c_object = c_object

####################################################################################################

class IdentityConverter(ToPythonConverter):
    def __call__(self):
        return self._c_object

class ListConverter(ToPythonConverter):
    def __call__(self):
        return list(self._c_object)

class ValueConverter(ToPythonConverter):
    def __call__(self):
        return self._c_object.value

####################################################################################################

class GlCommandWrapper(object):

    _logger = _module_logger.getChild('GlCommandWrapper')

    ##############################################

    def __init__(self, wrapper, command):

        self._wrapper = wrapper
        self._command = command
        self._number_of_parameters = command.number_of_parameters

        try:
            self._function = getattr(self._wrapper._libGL, str(command))
        except AttributeError:
            raise NameError("OpenGL function %s was no found in libGL" % (str(command)))

        # Only for simple prototype
        # argument_types = [gl_to_ctypes_type(parameter) for parameter in command.parameters]
        # if argument_types:
        #     self._function.argtypes = argument_types

        command_directive = __command_directives__.get(str(command), None)

        self._parameter_wrappers = []
        self._reference_parameter_wrappers = []
        for parameter in command.parameters:
            parameter_wrapper = None
            if command_directive and parameter.name in command_directive:
                # Fixme: purpose?
                pass
            elif parameter.pointer:
                if parameter.size_parameter is None and parameter.array_size == 1:
                    parameter_wrapper = ReferenceWrapper(parameter)
                elif parameter.size_parameter is None or parameter.computed_size:
                    parameter_wrapper = PointerWrapper(parameter)
                else:
                    pass
            elif parameter.back_ref:
                if parameter.back_ref[0].const:
                    # Only theses functions have len(back_ref) > 1
                    #   glAreTexturesResident
                    #   glGetDebugMessageLog
                    #   glPrioritizeTextures 
                    #   glShaderSource
                    parameter_wrapper = InputArrayWrapper(parameter)
                else:
                    parameter_wrapper = OutputArrayWrapper(parameter)
            else:
                parameter_wrapper = ParameterWrapper(parameter)
            if parameter_wrapper is not None:
                if isinstance(parameter_wrapper, ReferenceWrapper):
                    self._reference_parameter_wrappers.append(parameter_wrapper)
                else:
                    self._parameter_wrappers.append(parameter_wrapper)
                
        return_type = command.return_type
        if return_type.type != 'void':
            ctypes_type = gl_to_ctypes_type(return_type)
            if return_type.pointer:
                if ctypes_type == ctypes.c_ubyte: # return type is char *
                    ctypes_type = ctypes.c_char_p
                else:
                    raise NotImplementedError
            self._function.restype = ctypes_type
            self._return_void = False
        else:
            self._function.restype = None
            self._return_void = True

    ##############################################

    def __call__(self, *args, **kwargs):

        # Set the input parameters and append python converters for output
        c_parameters = [None]*self._number_of_parameters
        to_python_converters = []
        for parameter_wrapper, parameter in zip(self._parameter_wrappers, args):
            to_python_converter = parameter_wrapper.from_python(parameter, c_parameters)
            if to_python_converter is not None:
                to_python_converters.append(to_python_converter)
        for parameter_wrapper in self._reference_parameter_wrappers:
            to_python_converter = parameter_wrapper.from_python(c_parameters)
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

        # Check error
        if kwargs.get('check_error', False):
            self._wrapper.check_error()

        # Manage return
        if to_python_converters:
            output_parameters = [to_python_converter() for to_python_converter in to_python_converters]
            if self._return_void:
                # Extract uniq element
                # Fixme: to func?
                if len(output_parameters) == 1:
                    output_parameter = output_parameters[0]
                    if len(output_parameter) == 1:
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

        return str(self._command.name) + ' ' + str(self._function.argtypes) + ' -> ' + str(self._function.restype)

####################################################################################################

class CtypeWrapper(object):

   ##############################################

    def __init__(self, gl_spec, api, api_number, profile=None):

        self._gl_spec = gl_spec

        self._libGL = ctypes.cdll.LoadLibrary('libGL.so')
        api_enums, api_commands = self._gl_spec.generate_api(api, api_number, profile)
        self._init_enums(api_enums)
        self._init_commands(api_commands)

        self._pythonic_wrapper = PythonicWrapper(self)

    ##############################################

    def _init_enums(self, api_enums):

        gl_enums = GlEnums()
        for enum in api_enums:
            enum_name, enum_value = str(enum), int(enum)
            setattr(self, enum_name, enum_value)
            setattr(gl_enums, enum_name, enum_value)
        self.enums = gl_enums

    ##############################################

    def _init_commands(self, api_commands):

        for command in api_commands.itervalues():
            setattr(self, str(command), GlCommandWrapper(self, command))

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

####################################################################################################

class ErrorContextManager(object):

    ##############################################

    def __init__(self, wrapper):

        self._wrapper = wrapper

    ##############################################

    def __enter__(self):
        pass
    
    ##############################################
    
    def __exit__(self, type, value, traceback):

        self._wrapper.check_error()

####################################################################################################

class PythonicWrapper(object):

    ##############################################

    def __init__(self, wrapper):

        self._wrapper = wrapper

####################################################################################################
#
# End
#
####################################################################################################
