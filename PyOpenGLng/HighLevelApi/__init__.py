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

import logging

####################################################################################################

import PyOpenGLng.Wrapper as GlWrapper

####################################################################################################

_module_logger = logging.getLogger(__name__)

# Fixme: initialisation
#  Type requires GL
# GL = None

_module_logger.info("Initialise OpenGL Wrapper")
# GL = GlWrapper.init(api_number='3.1', profile='core', check_api_number=False)
# GL = GlWrapper.init(api_number='4.4', profile='core', check_api_number=False)
GL = GlWrapper.init(api_number='4.4', profile='compat', check_api_number=False)

####################################################################################################
# 
# End
# 
####################################################################################################
