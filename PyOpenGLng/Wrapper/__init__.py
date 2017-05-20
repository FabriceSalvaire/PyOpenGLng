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

import logging
import re
import sys

####################################################################################################

from ..GlApi.ApiNumber import ApiNumber
from ..GlApi.ManualParser import Manual
from ..Tools.Timer import TimerContextManager

####################################################################################################

_module_logger = logging.getLogger(__name__)

####################################################################################################

def init(wrapper='ctypes', api='gl', api_number=None, profile='core', check_api_number=True):

    """ Initialise the OpenGL wrapper.

    If the parameter *api_number* is :obj:`None` or the flag *check_api_number* is True, then this
    procedure must be called after an OpenGl context is active, else the OpenGl implementation's
    version cannot be retrieved. On Linux, see the source of the Mesa 3D Graphics Library tool
    *glxinfo* for more details.

    ..  On Fedora: package mesa-demos and file src/xdemos/glxinfo.c
    """

    if api not in ('gl', 'gles'):
        raise ValueError("api must be 'gl' or 'gles'")

    if wrapper == 'ctypes':
        from .CtypeWrapper import CtypeWrapper
        Wrapper = CtypeWrapper
    elif wrapper == 'cffi':
        from .CffiWrapper import CffiWrapper
        Wrapper = CffiWrapper
    else:
        ValueError("wrapper must be 'ctypes' or 'cffi'")

    if sys.platform.startswith('linux'):
        libGL_name = 'libGL.so'
    else:
        raise NotImplementedError

    # Fixme: store ApiNumber in CtypeWrapper
    # Fixme: called before context for example ???
    with TimerContextManager(_module_logger, 'Load GL library'):
        version_string = Wrapper.load_library(libGL_name)

    if check_api_number:
        if version_string is None:
            raise ValueError("An OpenGL context is required to retrieve the OpenGL implementation version")

        match = re.match(r'^(?P<major>\d+)\.(?P<minor>\d+).*', version_string)
        if match is not None:
            __api_number__ = ApiNumber('.'.join(match.groups()))
        else:
            raise ValueError("Can't decode GL Version String: " + version_string)

    if api_number is not None:
        api_number = ApiNumber(api_number)
        if check_api_number and __api_number__ < api_number:
            raise NameError("required API [%s %s profile=%s]"
                            " is not supported by OpenGL implementation (version is %s)" %
                            (api, api_number, profile, __api_number__))
    else:
        api_number = __api_number__

    from ..GlApi import GlSpecParser, CachedGlSpecParser, default_api_path
    with TimerContextManager(_module_logger, 'GlSpecParser'):
        # gl_spec_class = GlSpecParser
        gl_spec_class = CachedGlSpecParser
        gl_spec = gl_spec_class(default_api_path('gl'))

    with TimerContextManager(_module_logger, 'Load Manual'):
        manuals = Manual.load()

    with TimerContextManager(_module_logger, 'Wrapper'):
        GL = Wrapper(gl_spec, api, api_number, profile, manuals)

    return GL

####################################################################################################
# 
# End
# 
####################################################################################################
