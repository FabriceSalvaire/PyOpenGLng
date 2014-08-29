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

import glob
import os

from pygments.lexers import PythonLexer

####################################################################################################

class PythonFileAnalyser(object):

    ##############################################

    def __init__(self, file_path):

        self.file_path = file_path

        self.gl_functions = set()
        self.gl_constants = set()

        with open(self.file_path, 'r') as file_handler:
            # remove blank lines
            source_code = ''
            for line in file_handler.readlines():
                stripped_line = line.strip()
                if stripped_line:
                    source_code += stripped_line + '\n'
            # print source_code
            self._analyse_source_code(source_code)
        file_handler.close()

    ##############################################

    def _analyse_source_code(self, source_code):

        lexer = PythonLexer()
        token_source = lexer.get_tokens(source_code)
        for token_type, value in token_source:
            if len(value) > 3 and value.startswith('gl') and ord('A') <= ord(value[2]) <= ord('Z'):
                self.gl_functions.add(value)
            elif len(value) > 3 and value.startswith('GL_'):
                self.gl_constants.add(value)

####################################################################################################

gl_functions = set()
gl_constants = set()

for file_name in glob.glob('*.py'):
    analyser = PythonFileAnalyser(os.path.realpath(file_name))
    gl_functions = gl_functions.union(analyser.gl_functions)
    gl_constants = gl_constants.union(analyser.gl_constants)

for function in sorted(gl_functions):
    print function
for constant in sorted(gl_constants):
    print constant
    
####################################################################################################
#
# End
#
####################################################################################################
