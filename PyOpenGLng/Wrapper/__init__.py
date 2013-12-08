####################################################################################################
# 
# PyOpenGLng - An OpenGL Python Wrapper with a High Level API.
# Copyright (C) 2013 Salvaire Fabrice
# 
####################################################################################################

import logging
import re
import sys

####################################################################################################

from ..GlApi.ApiNumber import ApiNumber
from ..GlApi.ManualParser import Manual

####################################################################################################

_module_logger = logging.getLogger(__name__)

####################################################################################################

def init(wrapper='ctypes', api='gl', api_number=None, profile='core', check_api_number=True):

    """ Initialise the OpenGL wrapper.

    It must be called after an OpenGl context was created in order to check the OpenGL implementation
    version.
    """

    if api not in ('gl', 'gles'):
        raise ValueError("api must be 'gl' or 'gles'")

    if wrapper == 'ctypes':
        from .CtypeWrapper import CtypeWrapper
        Wrapper = CtypeWrapper
    elif wrapper == 'cffi':
        raise NotImplementedError
    else:
        ValueError("wrapper must be 'ctypes' or 'cffi'")

    if sys.platform.startswith('linux'):
        libGL_name = 'libGL.so'
    else:
        raise NotImplementedError

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

    from ..GlApi import GlSpecParser, default_api_path
    gl_spec = GlSpecParser(default_api_path('gl'))

    manuals = Manual.load()

    GL = Wrapper(gl_spec, api, api_number, profile, manuals)
        
    return GL

####################################################################################################
# 
# End
# 
####################################################################################################
