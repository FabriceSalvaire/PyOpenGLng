####################################################################################################
# 
# PyOpenGLng - An OpenGL V4 layer on top of PyOpengl.
# Copyright (C) 2013 Salvaire Fabrice
# 
####################################################################################################
    
__basic_api__ = """
 const char* glGetString(int name);
 """
 
from cffi import FFI
ffi = FFI()
ffi.cdef(__basic_api__)
libGL = ffi.dlopen(libGL_name)
version_string = ffi.string(libGL.glGetString(__GL.GL_VERSION__))

####################################################################################################
# 
# End
# 
####################################################################################################
