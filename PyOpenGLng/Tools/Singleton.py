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

""" Singleton snippets. """

####################################################################################################

import threading 

####################################################################################################

class SingletonMetaClass(type):

    """ A singleton metaclass.
    
    This implementation supports subclassing and is thread safe.
    """

    ##############################################

    def __init__(cls, class_name, super_classes, class_attribute_dict):

        # It is called just after cls creation in order to complete cls.

        # print('MetaSingleton __init__:', cls, class_name, super_classes, class_attribute_dict, sep='\n... ')

        type.__init__(cls, class_name, super_classes, class_attribute_dict)

        cls._instance = None
        cls._rlock = threading.RLock() # A factory function that returns a new reentrant lock object.

    ##############################################

    def __call__(cls, *args, **kwargs):

        # It is called when cls is instantiated: cls(...).
        # type.__call__ dispatches to the cls.__new__ and cls.__init__ methods.

        # print('MetaSingleton __call__:', cls, args, kwargs, sep='\n... ')

        with cls._rlock:
            if cls._instance is None:
                cls._instance = type.__call__(cls, *args, **kwargs)

        return cls._instance

####################################################################################################
#
# End
#
####################################################################################################
