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

""" The CFFI wrapper is not yed implemented. """

####################################################################################################

from cffi import FFI

####################################################################################################
    
__basic_api__ = """
 const char* glGetString(int name);
"""
 
ffi = FFI()
ffi.cdef(__basic_api__)

# libGL = ffi.dlopen(libGL_name)
# version_string = ffi.string(libGL.glGetString(__GL.GL_VERSION__))

####################################################################################################
# 
# End
# 
####################################################################################################
