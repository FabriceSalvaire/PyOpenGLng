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
