####################################################################################################
#
# PyOpenGLV4 - An OpenGL V4 layer on top of PyOpengl.
# Copyright (C) 2013 Salvaire Fabrice
#
####################################################################################################

####################################################################################################

import ctypes
import logging

####################################################################################################

_module_logger = logging.getLogger(__name__)

####################################################################################################

class GlEnums(object):
    pass

####################################################################################################

# class OutputArrayWrapper(object):
# 
#     ##############################################
# 
#     def __init__(self, type_):
# 
#         self.type = type_
# 
#     ##############################################
# 
#     def from_parameter(self, size):
# 
#         return self.type * size

####################################################################################################

class GlCommandWrapper(object):

    # Fixme: unsigned comes from typedef
    __gl_to_ctypes_type__ = {
        'char':ctypes.c_char,
        'int8_t':ctypes.c_byte,
        'uint8_t':ctypes.c_ubyte,
        'unsigned char':ctypes.c_ubyte,
        'short':ctypes.c_short,
        'unsigned short':ctypes.c_ushort,
        'int32_t':ctypes.c_long, # ?
        'int':ctypes.c_longlong, # ?
        'unsigned int':ctypes.c_ulonglong, # ?
        'int64_t':ctypes.c_longlong,
        'uint64_t':ctypes.c_ulonglong,
        'float':ctypes.c_float,
        'float_t':ctypes.c_float,
        'double':ctypes.c_double,
        'intptr_t':ctypes.c_void_p, # ?
        'ptrdiff_t':ctypes.c_void_p, # ?
        'ssize_t':ctypes.c_ulonglong, # ?
        'void': None, # ?
        }

    ##############################################

    def __init__(self, wrapper, command):

        self._wrapper = wrapper
        self._command = command

        gl_spec_types = wrapper._gl_spec.types

        try:
            self._function = getattr(self._wrapper._libGL, str(command))
        except AttributeError:
            raise NameError("OpenGL function %s was no found in libGL" % (str(command)))

        argument_types = []
        for parameter in command.parameters:
            if parameter.pointer:
                if parameter.const: # input parameter
                    pass # raise NotImplementedError
                else: # output parameter
                    if parameter.computed_size: 
                        pass # raise NotImplementedError
                    else:
                        pass # raise NotImplementedError
            else:
                c_type = parameter.translate_gl_type(gl_spec_types)
                ctypes_type = self.__gl_to_ctypes_type__[str(c_type)]
                argument_types.append(ctypes_type)
        if argument_types:
            self._function.argtypes = argument_types

        return_type = command.return_type
        if return_type.type != 'void':
            c_type = return_type.translate_gl_type(gl_spec_types)
            ctypes_type = self.__gl_to_ctypes_type__[str(c_type)]
            # print str(command), c_type, ctypes_type, return_type.pointer
            if return_type.pointer:
                if ctypes_type == ctypes.c_ubyte: # return type is char *
                    ctypes_type = ctypes.c_char_p
                else:
                    raise NotImplementedError
            self._function.restype = ctypes_type

    ##############################################

    def __call__(self, *args, **kwargs):

        print 'Call', repr(self)

        result = self._function(*args)

        if 'check_error' in kwargs and kwargs['check_error']:
            error_code = self._wrapper.glGetError()
            if error_code:
                pythonic_wrapper = self._wrapper._pythonic_wrapper
                error_message = pythonic_wrapper.error_code_message(error_code)
                raise NameError(error_message)

        return result

    ##############################################

    def __repr__(self):

        return str(self._command.name) + ' ' + str(self._function.argtypes) + ' -> ' + str(self._function.restype)

####################################################################################################

class CtypeWrapper(object):

   ##############################################

    def __init__(self, gl_spec, api, api_number, profile=None):

        self._gl_spec = gl_spec

        api_enums, api_commands = self._gl_spec.generate_api(api, api_number, profile)

        self._libGL = ctypes.cdll.LoadLibrary('libGL.so')
        self._init_enums(api_enums)
        self._init_commands(api_commands)

        self._pythonic_wrapper = PythonicWrapper(self)

    ##############################################

    def _init_enums(self, api_enums):

        gl_enums = GlEnums()
        for enum in api_enums:
            setattr(gl_enums, str(enum), int(enum))
        # self._gl_enums = gl_enums
        self.GL = gl_enums # Fixme: namespace?

    ##############################################

    def _init_commands(self, api_commands):

        for command in api_commands.itervalues():
            setattr(self, str(command), GlCommandWrapper(self, command))

####################################################################################################

class PythonicWrapper(object):

    ##############################################

    def __init__(self, wrapper):

        self._wrapper = wrapper

    ##############################################

    def error_code_message(self, error_code):

        # glGetError

        if not error_code:
            # GL_NO_ERROR: The value of this symbolic constant is guaranteed to be 0.
            return 'No error has been recorded.'
        else:
            GL = self._wrapper.GL
            if error_code == GL.GL_INVALID_ENUM:
                return 'An unacceptable value is specified for an enumerated argument.'
            elif error_code == GL.GL_INVALID_VALUE:
                return 'A numeric argument is out of range.'
            elif error_code == GL.GL_INVALID_OPERATION:
                return 'The specified operation is not allowed in the current state.'
            elif error_code == GL.GL_INVALID_FRAMEBUFFER_OPERATION:
                return 'The framebuffer object is not complete.'
            elif error_code == GL.GL_OUT_OF_MEMORY:
                return 'There is not enough memory left to execute the command.'
            elif error_code == GL.GL_STACK_UNDERFLOW:
                return 'An attempt has been made to perform an operation that would cause an internal stack to underflow.'
            elif error_code == GL.GL_STACK_OVERFLOW:
                return 'An attempt has been made to perform an operation that would cause an internal stack to overflow.'
            else:
                raise NotImplementedError

####################################################################################################
#
# End
#
####################################################################################################
