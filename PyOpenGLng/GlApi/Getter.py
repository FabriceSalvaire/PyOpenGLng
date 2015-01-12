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

####################################################################################################
#
# void glGetFloatv(GLenum pname, GLfloat * data);
# void glGetFloati_v(GLenum target, GLuint index, GLfloat * data);
# 
#  <command>
#      <proto>void <name>glGetFloati_v</name></proto>
#      <param group="TypeEnum"><ptype>GLenum</ptype> <name>target</name></param>
#      <param><ptype>GLuint</ptype> <name>index</name></param>
#      <param len="COMPSIZE(target)"><ptype>GLfloat</ptype> *<name>data</name></param>
#  </command>
#
#  <command>
#      <proto>void <name>glGetProgramiv</name></proto>
#      <param><ptype>GLuint</ptype> <name>program</name></param>
#      <param><ptype>GLenum</ptype> <name>pname</name></param>
#      <param len="COMPSIZE(pname)"><ptype>GLint</ptype> *<name>params</name></param>
#      <glx type="single" opcode="199"/>
#  </command>
#
# <command>
#     <proto>void <name>glGetTexLevelParameterfv</name></proto>
#     <param group="TextureTarget"><ptype>GLenum</ptype> <name>target</name></param>
#     <param group="CheckedInt32"><ptype>GLint</ptype> <name>level</name></param>
#     <param group="GetTextureParameter"><ptype>GLenum</ptype> <name>pname</name></param>
#     <param len="COMPSIZE(pname)"><ptype>GLfloat</ptype> *<name>params</name></param>
#     <glx type="single" opcode="138"/>
# </command>
#
# command/enum => type => command prefix
#                 size    
#
####################################################################################################

####################################################################################################

import six

####################################################################################################

import ctypes
import json
import logging
import numpy as np
import os

####################################################################################################

_module_logger = logging.getLogger(__name__)

####################################################################################################

# _letter_to_ctypes = {
#     'B': ctypes.c_ubyte, # GLboolean
#     'D': ctypes.c_double, # GLdouble
#     'E': ctypes.c_uint32, # GLenum
#     'F': ctypes.c_float, # GLfloat
#     'H': ctypes.c_uint32, # GLhandleARB excepted __APPLE__
#     'I': ctypes.c_int32, # GLint
#     'I64': ctypes.c_int64, # GLint64
#     'P': ctypes.c_void_p, # void *
#     'S': ctypes.c_char_p, # C string
#     'X': None, # To be determined, merely an enum
# }

_letter_to_ctypes = {
    'B': np.uint8, # GLboolean
    'D': np.double, # GLdouble
    'E': np.uint32, # GLenum
    'F': np.float32, # GLfloat
    'H': np.uint32, # GLhandleARB excepted __APPLE__
    'I': np.int32, # GLint
    'I64': np.int64, # GLint64

    'P': np.intp, # void *
    'S': np.char, # C string
    'X': None, # To be determined, merely an enum
}

_letter_to_prefix = {
    'B': 'b', # GLboolean
    'D': 'd', # GLdouble
    'E': '', # GLenum
    'F': 'f', # GLfloat
    'H': '', # GLhandleARB
    'I': 'i', # GLint
    'I64': 'i64', # GLint64
    'P': '', # void *
    'S': '', # C string
    'X': '',
}

####################################################################################################

getter_json_path = os.path.join(os.path.join(os.path.dirname(os.path.realpath(__file__))),
                                'getter.json')

with open(getter_json_path) as f:
    commands_dict = json.load(f)

from PyOpenGLng.GlApi import GlSpecParser, default_api_path
gl_spec = GlSpecParser(default_api_path('gl'))

enum_dict = {}
for enums in gl_spec.enums_list:
    for enum in enums:
        enum_dict[enum.name] = enum

# Update types
for command in six.itervalues(commands_dict):
    for enum in six.itervalues(command):
        enum[0] = _letter_to_ctypes[enum[0]]

####################################################################################################
# 
# End
# 
####################################################################################################
