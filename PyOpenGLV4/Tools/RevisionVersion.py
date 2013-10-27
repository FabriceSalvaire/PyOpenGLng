####################################################################################################
#
# PyOpenGLV4 - An OpenGL V4 layer on top of PyOpengl.
# Copyright (C) 2013 Salvaire Fabrice
#
####################################################################################################

####################################################################################################

__all__ = ['RevisionVersion']

####################################################################################################

import re

####################################################################################################

class RevisionVersion(object):

    scale = 10**3 # 32 bits
    # scale = 10**6 # 64 bits

    ##############################################

    def __init__(self, version):

        if isinstance(version, str):
            match = re.match('v([0-9]+)\.([0-9]+)\.([0-9]+)(-.*)?', version)
            if match is not None:
                groups = match.groups()
                self.major, self.minor, self.revision = [int(x) for x in groups[:3]]
                self.suffix = groups[3]
            else:
                raise NameError('Bad version string %s' % (version))
        
        elif isinstance(version, (tuple, list)):
            self.major, self.minor, self.revision = version[:3]
            if len(version) == 4:
                self.suffix = version[3]
            else:
                self.suffix = None

        elif isinstance(version, dict):
            self.major, self.minor, self.revision = [version[key] for key in 'major', 'minor', 'revision']
            if 'suffix' in version:
                self.suffix = version['suffix']
            else:
                self.suffix = None

        else:
            raise NameError('parameter must be a string or a tuple')
        
        # Check the scale
        for x in self.major, self.minor, self.revision:
            if x >= self.scale:
                raise NameError('Version %s must be less than %u' % (str(self), self.scale))

    ##############################################

    def __eq__(a, b):

        return a.major == b.major and a.minor == b.minor and a.revision == b.revision 

    ##############################################

    def __ge__(a, b):

        return int(a) >= int(b)

    ##############################################

    def __gt__(a, b):

        return int(a) > int(b)

    ##############################################

    def __le__(a, b):

        return int(a) <= int(b)

    ##############################################

    def __lt__(a, b):

        return int(a) < int(b)
    
    ##############################################

    def __int__(self):
        
        return (self.major * self.scale + self.minor) * self.scale + self.revision           

    ##############################################

    def version_string(self):

        return 'v%u.%u.%u' % (self.major, self.minor, self.revision)

    ##############################################

    def __str__(self):

        version_string = self.version_string()
        if self.suffix is not None:
            version_string += self.suffix

        return version_string

    ##############################################

    def to_list(self):

        # Fixme: useful?

        return [self.major, self.minor, self.revision, self.suffix]

####################################################################################################
#
# End
#
####################################################################################################
