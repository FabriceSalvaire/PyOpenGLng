####################################################################################################
# 
# PyOpenGLng - An OpenGL Python Wrapper with a High Level API.
# Copyright (C) 2013 Salvaire Fabrice
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
