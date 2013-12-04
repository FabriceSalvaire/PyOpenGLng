####################################################################################################
#
# PyOpenGLV4 - An OpenGL V4 layer on top of PyOpengl.
# Copyright (C) 2013 Salvaire Fabrice
#
####################################################################################################

####################################################################################################

import logging    
import os

####################################################################################################
#
# Logging
#

logging.basicConfig(
    format='\033[1;32m%(asctime)s\033[0m - \033[1;34m%(name)s.%(funcName)s\033[0m - \033[1;31m%(levelname)s\033[0m - %(message)s',
    level=logging.INFO,
    )

####################################################################################################

from PyOpenGLV4.GlApi.GlSpecParser import GlSpecParser, ApiNumber
from PyOpenGLV4.GlApi.CtypeWrapper import CtypeWrapper

####################################################################################################

# api_path = ops.path/join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'doc', 'registry-api')
api_path = '/home/gv/fabrice/unison-osiris/inactive-projects/PyOpenGLV4/doc/registry-api'

gl_xml_file_path = os.path.join(api_path, 'gl.xml')

# trang -I rnc -O rng registry.rnc registry-rng.xml
relax_ng_file_path = os.path.join(api_path, 'registry-rng.xml')

gl_spec = GlSpecParser(gl_xml_file_path, relax_ng_file_path)

api = 'gl'
# api_number = ApiNumber('4.4')
api_number = ApiNumber('3.0')
profile = 'core'

if True:
    api_enums, api_commands = gl_spec.generate_api(api, api_number, profile)

    # for enum in api_enums:
    #     print repr(enum)
    for command in api_commands.itervalues():
        # print repr(command)
        # print command.prototype()
        # print command.argument_types()
        # print command.name, command.return_type.c_type, command.argument_types()

wrapper = None
if False:
    wrapper = CtypeWrapper(gl_spec, api, api_number, profile)

####################################################################################################
# 
# End
# 
####################################################################################################
