####################################################################################################
#
# PyOpenGLng - An OpenGL V4 layer on top of PyOpengl.
# Copyright (C) 2013 Salvaire Fabrice
#
####################################################################################################

""" This module provides tools for software versionning.
"""

####################################################################################################

__all__ = ['RevisionVersion']

####################################################################################################

import collections
import re

####################################################################################################

class RevisionVersion(object):

    """ This class implements a revision version of the form vx.y.z-suffix where x, y and z are the
    major, minor and revision number, respectively.

    The version numbers can be accessed via the attributes :attr:`major,` :attr:`minor`,
    :attr:`revision`, :attr:`suffix`.

    The version string can be formated using :meth:`str` function.

    Two instances can be compared using these operators: ``==``, ``<``, ``>``, ``<=``, ``>=``.  To
    compare two versions, the version numbering (x, y, z) is converted to an integer in a
    pre-defined base using the following formulae: (x * base + y) * base + z. Thus x, y and z must
    be less than the :attr:`base`.
    """

    #: Base
    base = 10**3 # 32 bits
    # base = 10**6 # 64 bits

    ##############################################

    def __init__(self, version):

        """ The parameter *version* could be a version string, an iterable or a dictionnary. The
        suffix is optional. 

        Examples::

          RevisionVersion('v0.1.2')
          RevisionVersion('v0.1.2-r123')
          RevisionVersion((0,1,2))
          RevisionVersion((0,1,2,'r123'))
          RevisionVersion({'major':0, 'minor':1, 'revision':2, suffix:'r123'})
        """

        # Fixme: RevisionVersion(0,1,2,'r123')
        # Fixme: RevisionVersion(version)

        if isinstance(version, str):
            match = re.match('v([0-9]+)\.([0-9]+)\.([0-9]+)(-.*)?', version)
            if match is not None:
                groups = match.groups()
                self.major, self.minor, self.revision = [int(x) for x in groups[:3]]
                self.suffix = groups[3]
            else:
                raise ValueError('Bad version string %s' % (version))
        elif isinstance(version, dict): # dict is iterable
            self.major, self.minor, self.revision = [version.get(key, 0) for key in 'major', 'minor', 'revision']
            self.suffix = version.get('suffix', None)
        elif isinstance(version, collections.Iterable):
            self.major = version[0]
            self.minor = version[1] if len(version) == 2 else 0
            self.revision = version[2] if len(version) == 3 else 0
            self.suffix = version[3] if len(version) == 4 else None
        else:
            raise ValueError('Bad argument')
        
        # Check the given values
        for x in self.major, self.minor, self.revision:
            if x >= self.base:
                raise ValueError('Version %s must be less than %u' % (str(self), self.base))

    ##############################################

    def clone(self):

        return self.__class__(self.__dict__)

    ##############################################

    def __int__(self):

        """ Compute an integer from the revision numbering """
        
        return (self.major * self.base + self.minor) * self.base + self.revision           

    ##############################################

    def __eq__(a, b):

        """ Test if Va == Vb """

        return a.major == b.major and a.minor == b.minor and a.revision == b.revision 

    ##############################################

    def __ge__(a, b):

        """ Test if Va >= Vb """

        return int(a) >= int(b)

    ##############################################

    def __gt__(a, b):

        """ Test if Va > Vb """

        return int(a) > int(b)

    ##############################################

    def __le__(a, b):

        """ Test if Va <= Vb """

        return int(a) <= int(b)

    ##############################################

    def __lt__(a, b):

        """ Test if Va < Vb """

        return int(a) < int(b)
   
    ##############################################

    def version_string(self):

        """ Format the version as vx.y.z """

        return 'v%u.%u.%u' % (self.major, self.minor, self.revision)

    ##############################################

    def __str__(self):

        """ Format the version as vx.y.z-suffix """

        version_string = self.version_string()
        if self.suffix is not None:
            version_string += self.suffix

        return version_string

    ##############################################

    def to_tuple(self):

        """ Return the tuple (major, minor, revision, suffix) """ 

        return (self.major, self.minor, self.revision, self.suffix)

####################################################################################################
#
# End
#
####################################################################################################
