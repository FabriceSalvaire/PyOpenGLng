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

"""This module defines some configuration variables relative to the installation.

"""

####################################################################################################

import os

####################################################################################################

def parent_directory_of(file_name, step=1):

    directory = os.path.realpath(file_name)
    for i in range(step):
        directory = os.path.dirname(directory)
    return directory

####################################################################################################

class Path(object):

    ##############################################

    @staticmethod
    def manual_path(api_number):

        return os.path.join(parent_directory_of(__file__, step=2),
                            'doc', 'man%u' % api_number.major, 'xhtml')

####################################################################################################
# 
# End
# 
####################################################################################################
