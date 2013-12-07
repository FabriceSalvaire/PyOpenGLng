####################################################################################################
# 
# PyOpenGLng - An OpenGL Python Wrapper with a High Level API.
# Copyright (C) 2013 Salvaire Fabrice
# 
####################################################################################################

####################################################################################################

class ExtendedDictionaryInterface(dict):

    """ This class implements an extended dictionary interface.

      :attr:`clear`
      :attr:`copy`
      :attr:`fromkeys`
      :attr:`get`
      :attr:`has_key`
      :attr:`items`
      :attr:`iteritems`
      :attr:`iterkeys`
      :attr:`itervalues`
      :attr:`keys`
      :attr:`pop`
      :attr:`popitem`
      :attr:`setdefault`
      :attr:`update`
      :attr:`values`
      :attr:`viewitems`
      :attr:`viewkeys`
      :attr:`viewvalues`

    """

    ##############################################
    
    def __setitem__(self, key, value):

        if key not in self and key not in self.__dict__:
            super(ExtendedDictionaryInterface, self).__setitem__(key, value)
            self.__dict__[key] = value
        else:
            raise KeyError

####################################################################################################

class AttributeDictionaryInterface(object):

    """ This class implements an attribute and dictionary interface. """

    ##############################################
    
    def __init__(self):

        object.__setattr__(self, '_dictionary', dict())

    ##############################################
    
    def __getattr__(self, name):

        """ Get the value from its name. """

        return self._dictionary[name]

    ##############################################
    
    def __setattr__(self, name, value):

        """ Set the value from its name. """

        self._dictionary[name] = value

    ##############################################

    __getitem__ = __getattr__
    __setitem__ = __setattr__

    ##############################################
    
    def __iter__(self):

        """ Iterate over the dictionary. """

        for uniform in self._dictionary.values():
            yield uniform

    ##############################################
    
    def __contains__(self, name):

        """ Test it a uniform called *name* exists. """

        return name in self._dictionary

####################################################################################################

class AttributeDictionaryInterfaceDescriptor(AttributeDictionaryInterface):

    ##############################################
    
    def _get_descriptor(self, name):

        return self._dictionary[name]

    ##############################################
    
    def __getattr__(self, name):

        return self._get_descriptor(name).get()

    ##############################################
    
    def __setattr__(self, name, value):

        return self._get_descriptor(name).set(value)

    ##############################################

    __getitem__ = __getattr__
    __setitem__ = __setattr__

####################################################################################################
# 
# End
# 
####################################################################################################
