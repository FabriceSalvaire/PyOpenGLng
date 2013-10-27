####################################################################################################
#
# PyOpenGLV4 - An OpenGL V4 layer on top of PyOpengl.
# Copyright (C) 2013 Salvaire Fabrice
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
