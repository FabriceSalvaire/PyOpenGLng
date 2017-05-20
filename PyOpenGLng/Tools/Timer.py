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

import time

####################################################################################################

class TimerContextManager(object):

    ##############################################

    def __init__(self, logger, title):

        self._logger = logger
        self._title = title

    ##############################################

    def __enter__(self):

        self._start = time.clock()

    ##############################################
    
    def __exit__(self, type_, value, traceback):

        dt = time.clock() - self._start
        self._logger.info("{} dt = {} s".format(self._title, dt))

####################################################################################################
# 
# End
# 
####################################################################################################
