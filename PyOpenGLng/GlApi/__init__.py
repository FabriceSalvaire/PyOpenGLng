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

"""This module implements an Oriented Object interface to the OpenGL Registry XML file which
describe the OpenGL API and theses official extensions.

To generate the API of a particular OpenGL version uses for example this code snippet::

  xml_file_path = default_api_path('gl') # path to gl.xml
  gl_spec = GlSpecParser(xml_file_path)
  api_enums, api_commands = gl_spec.generate_api('gles', ApiNumber('2.0'), 'core')
  api_enums, api_commands = gl_spec.generate_api('gl', ApiNumber('4.4'), 'core')

Then you will get an instance of the class :class:`Enums` and :class:`Commands` corresponding to the
requested API.

The :command:`query-opengl-api` tool in the :file:`bin` directory provides some functions to query
the OpenGL API. You could look at its source code to learn how to use this module. See the
:ref:`tools section <tools-page>`.

"""

####################################################################################################

import os
import logging

from lxml import etree

####################################################################################################

from .ApiNumber import ApiNumber

####################################################################################################

_module_logger = logging.getLogger(__name__)

####################################################################################################

def default_api_path(file_name):
    """ Return the path to the file stored in the module directory. The ".xml" extension is
    concatened to the file name.
    """
    api_path = os.path.join(os.path.dirname(os.path.realpath(__file__)))
    return os.path.join(api_path, file_name + '.xml')

####################################################################################################

class NameDict(dict):

    """ This class extend the Python dictionnary class with two methods :meth:`register` and
    :meth:`unregister`.
    """

    ##############################################

    def register(self, item):
        
        """ Add the object to the dictionnary using its *name* attribute as a key. """

        if item.name in self:
            raise IndexError("item %s is already registered" % (item.name))

        self[item.name] = item

    ##############################################

    def unregister(self, item_name):

        """ Remove the given key. """

        del self[item_name]

    ##############################################

    def iter_sorted(self):

        # Fixme: iter(), sorted dict?
        # OrderedDict(sorted(d.items(), key=lambda t: t[0]))
        return sorted(self.itervalues(), cmp=lambda a, b: cmp(a.name, b.name))

####################################################################################################

class Types(object):

    """ This class registers the API types.

    Public Attributes:

      :attr:`c_types`
            dictionnary of types indexed by their names

      :attr:`types`
            list of types

    XML Registry Documentation:

        The ``<types>`` tag contains individual ``<type>`` tags describing each of the derived types
        used in the API.

    """

    ##############################################

    def __init__(self):

        # Fixme: attribute names
        self.types = []
        self.c_types = {} # fixme: name is not uniq, e.g. GLbyte is defined 3 times

    ##############################################

    def register(self, type_):

        """ Register a type. """

        self.types.append(type_)
        # Fixme: gles ...
        if type_.c_type is not None and type_.requires != 'khrplatform':
            if type_.name not in self.c_types:
                self.c_types[type_.name] = type_
            else:
                raise NameError("%s is already registered" % (type_.name))

    ##############################################

    def translate_gl_type(self, gl_type):

        # Fixme: name -> type instance

        # return self.c_types.get(gl_type, gl_type)

        if gl_type in self.c_types:
            return self.c_types[gl_type]
        else:
            # Fixme: None ?
            return gl_type
            # raise NameError("Failed to translate type %s" % (gl_type))

####################################################################################################

class Type(object):

    """ This class defines an OpenGL type.

    Public Attributes:

        :attr:`api`
            API name

        :attr:`api_entry`
            Boolean, cf. supra

        :attr:`c_code`
            correponding C type declaration (without name), e.g. ``typedef unsigned int``

        :attr:`c_type`
            correponding C type, e.g. ``int``

        :attr:`comment`
           cf. supra

        :attr:`name`
             e.g. ``GLenum``

        :attr:`pointer`
            Boolean

        :attr:`requires`
           cf. supra

        :attr:`unsigned`
            Boolean

    XML Registry Documentation:

        Each ``<type>`` tag contains legal C code, with attributes or embedded tags denoting the
        type name.
        
        Attributes of ``<type>`` tags:
        
            requires
                another type name this type requires to complete its definition.
            
            name
                name of this type (if not defined in the tag body).
            
            api
                an API name (see ``<feature>`` below) which specializes this definition of the named
                type, so that the same API types may have different definitions for e.g. GL ES and
                GL.
            
            comment
                arbitrary string (unused).

        Contents of ``<group>`` tags:
        
            ``<type>`` contains text which is legal C code for a type declaration. It may also
            contain embedded tags:
            
                ``<apientry/>``
                    insert a platform calling convention macro here during header generation, used
                    mostly for function pointer types.
            
                ``<name>``
                    contains the name of this type (if not defined in the tag attributes).

    """

    #: List of C types
    _C_TYPES = (
        # integer types
        'char',
        'int8_t',
        'uint8_t',
        'short',
        'int32_t',
        'int',
        'int64_t',
        'uint64_t',
        # float types
        'float',
        'float_t',
        'double',
        # pointer types
        'intptr_t',
        'ptrdiff_t',
        'ssize_t',
        'void',
        )

    ##############################################

    def __init__(self,
                 name,
                 c_declaration_head=None, c_declaration_tail='',
                 requires=None, api=None, comment=None, api_entry=False,
                 ):

        self.name = name
        # Fixme: -> concat name? /!\ function pointer
        self.c_declaration_head = c_declaration_head
        self.c_declaration_tail = c_declaration_tail
        self.api_entry = api_entry
        self.requires = requires
        self.api = api
        self.comment = comment

        # Parse the C type declaration
        self.unsigned = False
        self.pointer = False
        self.c_type = None
        if (self.c_declaration_head is not None
            and self.c_declaration_head.count('\n') == 0
            and self.c_declaration_head.startswith('typedef')
            and not self.c_declaration_head.endswith('(')):
            for token in self.c_declaration_head.split()[1:]:
                if token.startswith('khronos_'):
                    token = token[len('khronos_'):]
                if token == 'unsigned':
                    self.unsigned = True
                elif token == 'signed':
                    self.unsigned = False
                elif token == '*':
                    self.pointer = True
                elif token in self._C_TYPES:
                    self.c_type = token
        else:
            if self.c_declaration_head is not None:
                c_declaration = self.c_declaration_head
            else:
                c_declaration = ''
            c_declaration += self.name + self.c_declaration_tail
            _module_logger.warn("Unsupported type declaration for %s", c_declaration)
            # Fixme:
            # raise NameError("Unsupported type declaration for %s" % (name))

    ##############################################

    def __repr__(self):

        """ Return the C type string, e.g. ``unsigned int *``. """

        # Fixme: str ?

        if self.unsigned:
            type_string = 'unsigned '
        else:
            type_string = ''
        type_string += self.c_type # if None?
        if self.pointer:
            type_string += ' *'

        return type_string

####################################################################################################

class Groups(NameDict):

    """ This class registers Enumerant Groups.

    XML Registry Documentation:

        The ``<groups>`` tags contain individual ``<group>`` tags describing some of the group
        annotations used for return and parameter types.
        
        Attributes of ``<groups>`` tags: None
        
        Contents of ``<groups>`` tags:
        
            Each ``<groups>`` block contains zero or more ``<group>`` tags, in arbitrary order
            (although they are typically ordered by group name, to improve human readability).

    """

####################################################################################################

class Group(object):

    """ This class defines an Enumerant Group, e.g. *TextureMagFilter* regroups the relevant
    enumerant for texture magnification filter

    Public Attributes:

        :attr:`comment`

        :attr:`name`

    XML Registry Documentation:
    
        Each ``<group>`` tag defines a single group annotation.
        
        Attributes of ``<group>`` tags:
        
            name
                group name, an arbitrary string for grouping a set of enums together within a
                broader namespace.
        
        Contents of ``<group>`` tags:
        
            ``<group>`` tags may contain zero or more ``<enum>`` tags. Each ``<enum>`` tag may
            contain only a name attribute, which should correspond to a ``<enum>`` definition in an
            ``<enums>`` block.
        
        Meaning of ``<group>`` tags:
        
            If a ``<proto>`` or ``<param>`` tag of a ``<command>`` has a group attribute defined,
            and that attribute matches a ``<group>`` name, then the return type or parameter type is
            considered to be constrained to values defined by the corresponding ``<group>``. C
            language bindings do not attempt to enforce this constraint in any way, but other
            language bindings may try to do so.
    """

    ##############################################

    def __init__(self,
                 name, enum_name_list,
                 comment=None,
                 ):

        self.name = name
        self.comment = comment

        self._enum_name_list = enum_name_list

    ##############################################

    def __iter__(self):

        return iter(self._enum_name_list)

####################################################################################################

class Enums(object):

    """ This class defines a list of enumerants.

    Public Attributes:

        :attr:`comment`

        :attr:`end`

        :attr:`group`

        :attr:`namespace`

        :attr:`start`

        :attr:`type`

        :attr:`vendor`

    XML Registry Documentation:

        The ``<enums>`` tags contain individual ``<enum>`` tags describing each of the token
        (enumerant) names used in the API.
        
        Attributes of ``<enums>`` tags:
        
            namespace
                a string for grouping many different enums together, currently unused but typically
                something like GL for all enums in the OpenGL / OpenGL ES shared namespace. Multiple
                ``<enums>`` tags can share the same namespace.
            
            type 
                a string describing the data type of the values of this group of enums, currently
                unused. The only string used at present in the is bitmask.
            
            start, end
                 integers defining the start and end of a reserved range of enumerants for a
                 particular vendor or purpose. start must be <= end. These fields define formal
                 enumerant allocations within a namespace, and are made by the Khronos Registrar on
                 request from implementers following the enum allocation policy.
            
            vendor
                 string describing the vendor or purposes to whom a reserved range of enumerants is
                 allocated.
            
            comment
                 arbitrary string (unused)
            
            group
                group name, an arbitrary string.    
        
        Contents of ``<enums>`` tags:
        
            Each ``<enums>`` block contains zero or more ``<enum>`` and ``<unused>`` tags, in
            arbitrary order (although they are typically ordered by sorting on enumerant values, to
            improve human readability).
    """

    ##############################################

    def __init__(self,
                 namespace,
                 group=None, type_=None, start=None, end=None, vendor=None, comment=None,
                 ):

        self.namespace = namespace
        self.group = group
        self.type = type_
        self.start = start
        self.end = end
        self.vendor = vendor
        self.comment = comment

        self._enum_name_dict = {}
        self._enum_value_dict = {}

    ##############################################

    def __iter__(self):

        """ Return an iterator over the enumerant instances. """

        return self._enum_name_dict.itervalues()

    ##############################################

    def iter_sorted(self):

        """ """

        # Fixme: iter(), sorted dict?
        return sorted(self._enum_name_dict.itervalues(), cmp=lambda a, b: cmp(a.name, b.name))

    ##############################################

    def __len__(self):

        """ Return the number of enumerants. """

        return len(self._enum_name_dict)

    ##############################################

    def __getitem__(self, key):

        """ Return the enumerant instance for the given name or value. """

        try:
            return self._enum_name_dict[key]
        except KeyError:
            try:
                return self._enum_value_dict[key]
            except KeyError:
                raise KeyError("Any enum having this name or value: " + str(key))

    ##############################################

    def register(self, enum, primary_registration=True):
        
        """ Register an enumerant. If the flag *primary_registration* is set then the enumerant back
        reference is set.
        """

        if enum.name in self._enum_name_dict:
            try:
                namespace = enum.enums.namespace
            except AttributeError:
                namespace = '(namespace not yed defined)'
            raise IndexError("enum %s already registered in %s" % (enum.name, namespace))

        self._enum_name_dict[enum.name] = enum
        self._enum_value_dict[enum.value] = enum

        if primary_registration:
            if enum.enums is not None:
                raise NameError('Back reference is already affected for enum %s' % (enum.name))
            else:
                enum.enums = self

    ##############################################

    def unregister(self, enum_name):

        """ Remove an enumerant. """

        enum = self._enum_name_dict[enum_name]
        del self._enum_value_dict[enum.value]
        del self._enum_name_dict[enum_name]

    ##############################################

    def merge(self, api, enums):

        """ Add the enumerants from *enums* that match *api*. """

        for enum in enums._enum_name_dict.itervalues():
            if enum.api is None or enum.api == api:
                self.register(enum, primary_registration=False)

####################################################################################################

class Enum(object):

    """ This class defines an enumerant.

    The name of an enumerant can be retrieved using ``str(enumerant)`` and its value using
    ``int(enumerant)``.

    Public Attributes:

        :attr:`alias`

        :attr:`api`

        :attr:`comment`

        :attr:`enums`
             back reference to the :class:`Enums` instance

        :attr:`name`

        :attr:`type`
            cf. supra

        :attr:`value`

    XML Registry Documentation:

        Each ``<enum>`` tag defines a single GL (or other API) token.
        
        Attributes of ``<enum>`` tags:
        
            value
                enumerant value, a legal C constant (usually a hexadecimal integer).
            
            name
                enumerant name, a legal C preprocessor token name.
            
            api
                an API name which specializes this definition of the named enum, so that different
                APIs may have different values for the same token (used to address a few accidental
                incompatibilities between GL and GL ES).
            
            type
                legal C suffix for the value to force it to a specific type. Currently only u and
                ull are used, for unsigned 32- and 64-bit integer values, respectively.  Separated
                from the value field since this eases parsing and sorting of values, and is rarely
                used.
            
            alias
                name of another enumerant this is an alias of, used where token names have been
                changed as a result of profile changes or for consistency purposes.  An enumerant
                alias is simply a different name for the exact same value. At present, enumerants
                which are promoted from extension to core API status are not tagged as aliases -
                just enumerants tagged as aliases in the Changed Tokens sections of appendices to
                the OpenGL Specification. This might change in the future.
            
            comment
                arbitrary string (unused).
        
        Contents of ``<enum>`` tags:
       
            ``<enum>`` tags have no allowed contents. All information is contained in the
            attributes.

    """

    ##############################################

    def __init__(self,
                 name, value,
                 type_=None, alias=None, comment=None, api=None,
                 ):

        self.name = name
        self.value = value
        self.type = type_
        self.alias = alias
        self.comment = comment
        self.api = api
        self.enums = None

    ##############################################

    def __str__(self):

        return self.name

    ##############################################

    def __int__(self):

        return self.value

    ##############################################

    def __repr__(self):

        return "Enum %s = %s" % (self.name, hex(self.value))

    ##############################################

    def long_repr(self):

        return repr(self) + " (type: %(type)s, alias: %(alias)s, api: %(api)s, comment: %(comment)s)" % self.__dict__

####################################################################################################

class Commands(NameDict):

    """ This class stores the OpenGL commands.

    XML Registry Documentation:

        The ``<commands>`` tag contains definitions of each of the functions (commands) used in the
        API.
        
        Attributes of ``<commands>`` tags:
        
            namespace
                a string defining the namespace in which commands live, currently unused but
                typically something like GL.
        
        Contents of ``<commands>`` tags:
        
            Each ``<commands>`` block contains zero or more ``<command>`` tags, in arbitrary order
            (although they are typically ordered by sorting on the command name, to improve human
            readability).
    """

####################################################################################################

class Command(object):
    
    """ This class defines an OpenGL command.

    Public Attributes:

        :attr:`input_parameter`
            number of input parameters

        :attr:`name`
            command name

        :attr:`output_parameter`
            number of output parameters

        :attr:`parameter_dict`
             dictionnary of parameters

        :attr:`parameters`
             list of parameters

        :attr:`return_type`

    XML Registry Documentation:
    
        The ``<command>`` tag contains a structured definition of a single API command (function).
        
        Attributes of ``<command>`` tags:
        
            comment
                arbitrary string (unused).
        
        Contents of ``<command>`` tags:
        
            * ``<proto>`` must be the first element, and is a tag defining the C function prototype
              of a command as described below, up to the function name but not including function
              parameters.
            
            * ``<param>`` elements for each command parameter follow, defining its name and type, as
              described below. If a command takes no arguments, it has no ``<param>`` tags.
            
            Following these elements, the remaining elements in a ``<command>`` tag are optional and
            may be in any order:
            
            * ``<alias>`` has no attributes and contains a string which is the name of another
              command this command is an alias of, used when promoting a function from extension to
              ARB or ARB to API status. A command alias describes the case where there are two
              function names which resolve to the same client library code, so (for example) the
              case where a command is promoted but is also given different GLX protocol would not be
              an alias in this sense.
            
            * ``<vecequiv>`` has no attributes and contains a string which is the name of another
              command which is the vector equivalent of this command. For example, the vector
              equivalent of glVertex3f is glVertex3fv.
            
            * ``<glx>`` defines GLX protocol information for this command, as described below.  Many
              GL commands don't have GLX protocol defined, and other APIs such as EGL and WGL don't
              use GLX at all.
        
        Command prototype (``<proto>`` tags):
        
        The ``<proto>`` tag defines the return type and name of a command.
        
        Attributes of ``<proto>`` tags
        
            group
                group name, an arbitrary string.
        
        If the group name is defined, it may be interpreted as described in ``<ref>``.
        
        Contents of ``<proto>`` tags:
        
            The text elements of a ``<proto>`` tag, with all other tags removed, is legal C code
            describing the return type and name of a command. In addition it may contain two
            semantic tags:
            
            * The ``<ptype>`` tag is optional, and contains text which is a valid type name found in
              ``<type>`` tag, and indicates that this type must be previously defined for the
              definition of the command to succeed. Builtin C types, and any derived types which are
              expected to be found in other header files, should not be wrapped in ``<ptype>`` tags.
            
            * The ``<name>`` tag is required, and contains the command name being described.
    """

    ##############################################

    def __init__(self,
                 name, return_type,
                 parameters=(),
                 ):

        self.name = name
        self.return_type = return_type
        self.parameters = parameters

        self.parameter_dict = {}
        self.input_parameter = 0
        self.output_parameter = 0
        for parameter in parameters:
            self.parameter_dict[str(parameter)] = parameter
            if parameter.pointer:
                if parameter.const: # input parameter
                    self.input_parameter += 1
                else: # output parameter
                    self.output_parameter += 1
                # if parameter.computed_size: 
        # Set the parameter back references
        for parameter in parameters:
            # size parameter can be after pointer
            if parameter.size_parameter is not None and not parameter.computed_size:
                self.parameter_dict[parameter.size_parameter].pointer_parameters.append(parameter)

    ##############################################

    @property
    def number_of_parameters(self):
        return len(self.parameters)

    ##############################################

    def __str__(self):

        return self.name

    ##############################################

    def __repr__(self):

        return '%s %s (%s)' % (repr(self.return_type), self.name,
                               ', '.join([repr(parameter) for parameter in self.parameters]))

    ##############################################

    def prototype(self):

        """ Return the C function prototype. """

        return '%s %s (%s)' % (self.return_type.prototype(), self.name,
                               ', '.join([parameter.prototype() for parameter in self.parameters]))

    ##############################################

    def argument_types(self):

        return [parameter.format_gl_type() for parameter in self.parameters]

####################################################################################################

class Parameter(object):

    """ This class defines a command parameter.

    Public Attributes:

        :attr:`array_size`
            array size or :obj:`None`

        :attr:`pointer_parameters`
            array of pointer parameters where this parameter acts as a size parameter

        :attr:`c_type`
            corresponding :class:`Type` instance or "void"

        :attr:`computed_size`
            Boolean

        :attr:`const`
            Boolean

        :attr:`group`
            group name

        :attr:`location`
            parameter position in the prototype

        :attr:`name`
            parameter name or :obj:`None` for return type

        :attr:`pointer`
            pointer level, i.e. 0 for a non-pointer parameter, 1 for ``*``, 2 for ``**``

        :attr:`size_multiplier`
            integer to be multiplied with the size parameter to get the size

        :attr:`size_parameter`
            name of the size parameter or :obj:`None`

        :attr:`type`
            parameter type without ``const and ``*``

    XML Registry Documentation:
    
        The ``<param>`` tag defines the type and name of a parameter.
        
        Attributes of ``<param>`` tags:
        
            group
                group name, an arbitrary string.
            
            len
                parameter length, either an integer specifying the number of elements of the
                parameter ``<ptype>``, or a complex string expression with poorly defined syntax,
                usually representing a length that is computed as a combination of other command
                parameter values, and possibly current GL state as well.
        
        If the group name is defined, it may be interpreted as described in ``<ref>``.
        
        Contents of ``<param>`` tags:
        
            The text elements of a ``<param>`` tag, with all other tags removed, is legal C code
            describing the type and name of a function parameter. In addition it may contain two
            semantic tags:
            
                * The ``<ptype>`` tag is optional, and contains text which is a valid type name
                  found in ``<type>`` tag, and indicates that this type must be previously defined
                  for the definition of the command to succeed. Builtin C types, and any derived
                  types which are expected to be found in other header files, should not be wrapped
                  in ``<ptype>`` tags.
                
                * The ``<name>`` tag is required, and contains the command name being described.
    """

    ##############################################

    def __init__(self,
                 gl_types,
                 location, name,
                 ptype=None, group=None, length=None,
                 const=False, pointer=0,
                 ):

        self.location = location
        self.name = name # None for return type
        self.type = ptype
        self.group = group
        self.const = const
        # Fixme: -> pointer_level / multiplicity ?
        self.pointer = pointer

        # for example: GLenum -> unsigned int
        self.c_type = gl_types.translate_gl_type(self.type)

        self.size_parameter = None
        self.pointer_parameters = [] # back ref for size parameter
        self.array_size = None # array size is known
        self.computed_size = False # array size is computed by OpenGL
        self.size_multiplier = 1
        try:
            self.array_size = int(length)
        except ValueError:
            self.computed_size = length.startswith('COMPSIZE')
            if not self.computed_size and '*' in length:
                # for example: 'n*2'
                tokens = length.split('*')
                self.size_parameter = tokens[0]
                self.size_multiplier = int(tokens[1])
            else:
                self.size_parameter = length
        except TypeError:
            pass
 
    ##############################################

    def __str__(self):

        return self.name

    ##############################################

    def _format_type(self, type_string):

        """ Format a type, add ``const``, ``*`` and ``[]`` if they are relevant. """
        
        if self.const:
            type_string = 'const ' + type_string
        if self.pointer:
            type_string += ' ' + '*'*self.pointer
        if self.size_parameter is not None:
            type_string += ' [%s]' % self.size_parameter
        elif self.array_size is not None:
            type_string += ' [%u]' % self.array_size
        
        return type_string

    ##############################################

    def format_gl_type(self):

        """ format the translated type parameter. """

        # Fixme: method name

        c_type = self.c_type
        if isinstance(c_type, Type):
            c_type = repr(self.c_type)
        # Fixme: void
        # else c_type = 'void'

        return self._format_type(c_type)

    ##############################################

    def __repr__(self):

        """ Return the C parameter declaration, e.g. ``GLint location``. """

        if self.name is not None:
            return '%s %s' % (self._format_type(self.type), self.name)
        else:
            return self._format_type(self.type)

    ##############################################

    def prototype(self):

        """ Return the C parameter declaration but with translated type. """

        # Fixme: method name

        if self.name is not None:
            return '%s %s' % (self.format_gl_type(), self.name)
        else:
            return self.format_gl_type()

    ##############################################

    def long_repr(self):

        template = """Parameter %(name)s
  location           %(location_)s
  type               %(type)s
  group              %(group)s
  const              %(const)s
  pointer            %(pointer)s
  c type             %(c_type)s
  size parameter     %(size_parameter)s
  pointer parameters %(pointer_parameters)s
  computed size      %(computed_size)s
  size_multiplier    %(size_multiplier)u
  array_size         %(array_size_)s
"""

        # Fixme:
        d = dict(self.__dict__)
        d['array_size_'] = str(self.array_size)
        d['location_'] = str(self.location)

        return template % d

    ##############################################

    def is_generic_pointer(self):

        """ Test if parameter is ``void *``. """

        return self.pointer and self.c_type == 'void'

####################################################################################################

class Feature(object):

    """ This class defines the features of an API.

    Features are provided as a list of required or removed interfaces (commands, enumerants and
    types).

    Public Attributes:

        :attr:`api`

        :attr:`api_number`

        :attr:`comment`

        :attr:`name`

        :attr:`protect`

    XML Registry Documentation:
    
        API features are described in individual ``<feature>`` tags. A feature is the set of
        interfaces (enumerants and commands) defined by a particular API and version, such as OpenGL
        4.0 or OpenGL ES 3.0, and includes all API profiles of that version.
        
        Attributes of ``<feature>`` tags:
        
            api
                API name this feature is for (see ``<ref>``), such as gl or gles2.
            
            name
                version name, used as the C preprocessor token under which the version's interfaces
                are protected against multiple inclusion. Example: GL_VERSION_4_2.
            
            protect
                an additional preprocessor token used to protect a feature definition. Usually
                another feature or extension name. Rarely used, for odd circumstances where the
                definition of a feature or extension requires another to be defined first.
            
            number
                feature version number, usually a string interpreted as
                majorNumber.minorNumber. Example: 4.2.
            
            comment
                arbitrary string (unused)
        
        Contents of ``<feature>`` tags:
        
            Zero or more ``<require>`` and ``<remove>`` tags (see ``<ref>``), in arbitrary order.
            Each tag describes a set of interfaces that is respectively required for, or removed
            from, this feature, as described below.
    """

    ##############################################

    def __init__(self,
                 api, name, number,
                 protect=None, comment=None,
                 ):

        self.api = api
        self.name = name
        # self.number = number
        self.protect = protect
        self.comment = comment

        self.api_number = ApiNumber(number)

        # Fixme: subclass list?
        self._interface_list = []

    ##############################################

    def __iter__(self):

        return iter(self._interface_list)

    ##############################################

    def append(self, interface):

        self._interface_list.append(interface)

####################################################################################################

class Extension(object):

    """ This class defines the features of an extension.

    Features are provided as a list of required or removed interfaces (commands, enumerants and
    types).

    Public Attributes:

        :attr:`comment`

        :attr:`name`

        :attr:`protect`

        :attr:`supported`

    XML Registry Documentation:
    
        The ``<extensions>`` tag contains definitions of each of the extenions which are defined for
        the API.
        
        Attributes of ``<extensions>`` tags: None
        
        Contents of ``<extensions>`` tags:
        
            Each ``<extensions>`` block contains zero or more ``<extension>`` tags, each describing
            an API extension, in arbitrary order (although they are typically ordered by sorting on
            the extension name, to improve human readability).
        
        API Extensions (``<extension>`` tag):
        
        API extensions are described in individual ``<extension>`` tags. An extension is the set of
        interfaces defined by a particular API extension specification, such as
        ARB_multitexture. ``<extension>`` is similar to ``<feature>``, but instead of having version
        and profile attributes, instead has a supported attribute, which describes the set of API
        names which the extension can potentially be implemented against.
        
        Attributes of ``<extension>`` tags:
        
            supported
                a regular expression, with an implicit ^ and $ bracketing it, which should match the
                api tag of a set of ``<feature>`` tags.
            
            protect
                an additional preprocessor token used to protect an extension def- inition. Usually
                another feature or extension name. Rarely used, for odd cir- cumstances where the
                definition of an extension requires another to be defined first.
            
            comment
                arbitrary string (unused)
        
        Contents of ``<extension>`` tags:
        
            Zero or more ``<require>`` and ``<remove>`` tags (see ``<ref>``), in arbitrary order.
            Each tag describes a set of interfaces that is respectively required for, or removed
            from, this extension, as described below.
    """

    ##############################################

    def __init__(self,
                 name, supported,
                 protect=None, comment=None,
                 ):

        self.name = name
        self.supported = supported
        self.protect = protect
        self.comment = comment

        # Fixme: subclass list?
        self._interface_list = []

    ##############################################

    def __iter__(self):

        return iter(self._interface_list)

    ##############################################

    def append(self, interface):

        self._interface_list.append(interface)

####################################################################################################

class RequiredInterface(object):

    """ This class defines a required interface.

    Public Attributes:

        :attr:`api`

        :attr:`comment`

        :attr:`profile`

    XML Registry Documentation:
    
        A ``<require>`` block defines a set of interfaces (types, enumerants and commands) required
        by a ``<feature>`` or ``<extension>``. A ``<remove>`` block defines a set of interfaces
        removed by a ``<feature>`` (this is primarily useful for the OpenGL core profile, which
        removed many interfaces - extensions should never remove interfaces, although this usage is
        allowed by the schema). Except for the tag name and behavior, the contents of ``<require>``
        and ``<remove>`` tags are identical.
        
        Attributes of ``<require>`` and ``<remove>`` tags:
        
            profile
                string name of an API profile. Interfaces in the tag are only required (or removed)
                if the specified profile is being generated. If not specified, interfaces are
                required (or removed) for all API profiles.
            
            comment
                arbitrary string (unused)
            
            api
                an API name (see ``<ref>``). Interfaces in the tag are only required (or removed) if
                the specified API is being generated. If not specified, interfaces are required (or
                removed) for all APIs. The api attribute is only supported inside ``<extension>``
                tags, since ``<feature>`` tags already define a specific API.
        
        Contents of ``<require>`` and ``<remove>`` tags:
        
            Zero or more of the following tags, in any order:
            
            * ``<command>`` specifies an required (or removed) command defined in a ``<commands>``
              block. The tag has no content, but contains elements:
            
                  name
                      name of the command (required).
                  
                  comment
                      arbitrary string (optional and unused).
            
            * ``<enum>`` specifies an required (or removed) enumerant defined in a ``<enums>``
              block. The tag has no content, but contains elements:
            
                  name
                      name of the enumerant (required).
                  
                  comment
                      arbitrary string (optional and unused).
            
            * ``<type>`` specifies a required (or removed) type defined in a ``<types>`` block.
              Most types are picked up implicitly by using the ``<ptype>`` tags of commands, but in
              a few cases, additional types need to be specified explicitly (it is unlikely that a
              type would ever be removed, although this usage is allowed by the schema). The tag has
              no content, but contains elements:
            
                  name
                      name of the type (required).
                  
                  comment
                      arbitrary string (optional and unused).
    """

    _logger = _module_logger.getChild('RequiredInterface')

    ##############################################

    def __init__(self,
                 profile=None, comment=None, api=None,
                 ):

        self.profile = profile
        self.comment = comment
        self.api = api

        self._items = set()

    ##############################################

    def __iter__(self):

        return iter(self._items)

    ##############################################

    def append(self, item):

        self._items.add(item)

    ##############################################

    def append_new(self, **kwargs):

        """ Create and append a :class:`RequiredItem`. """

        item = RequiredItem(**kwargs)
        self.append(item)

    ##############################################

    def merge(self, interface):

        """ Merge with an interface. """

        if isinstance(interface, RemovedInterface):
            action = 'Remove'
            self._items = self._items.difference(interface._items)
        else:
            action = 'Add'
            self._items = self._items.union(interface._items)
        self._logger.debug('%s interface\n  (profile = %s) %s', action, interface.profile, interface.comment)

####################################################################################################

class RequiredItem(object):

    """ This class represents a required command, enumerant or type for an interface.

    Public Attributes:

        :attr:`comment`

        :attr:`name`

        :attr:`type`
            can be "command", "enumerant" or "type"
    """

    ##############################################

    def __init__(self,
                 type_,
                 name, comment=None,
                 ):

        self.type = type_
        self.name = name
        self.comment = comment

    ##############################################

    def __hash__(self):

        return hash(self.name)

    ##############################################

    def __eq__(self, other):

        return self.name == other.name 

####################################################################################################

class RemovedInterface(RequiredInterface):

    """ This class defines a removed interface. """

    ##############################################

    def append_new(self, **kwargs):

        """ Create and append a :class:`RemovedItem`. """

        item = RemovedItem(**kwargs)
        self.append(item)

####################################################################################################

class RemovedItem(RequiredItem):
    """ This class represents a removed command, enumerant or type from an interface. """

####################################################################################################

class GlSpecParser(object):

    """ This class implements the OpenGL Registry XML file parser and the Oriented Object interface.

    Public Attributes:

      :attr:`commands`
          :class:`Commands` instance

      :attr:`enums_list`

      :attr:`extension_list`

      :attr:`feature_list`

      :attr:`groups`
          :class:`Groups` instance

      :attr:`types`
          :class:`Types` instance

    """

    # Fixme: class name

    _logger = _module_logger.getChild('GlSpecParser')

    ##############################################

    def __init__(self, xml_file_path, schema_file_path=None):

        self._tree = etree.parse(xml_file_path)

        if schema_file_path is not None:
            self._validate(schema_file_path)

        self.types = Types()
        self.groups = Groups()
        self.commands = Commands()
        self.enums_list = []
        self.feature_list = []
        self.extension_list = []

        self._parse()

    ##############################################

    def _validate(self, relax_ng_file_path):

        """ Validate the XML file using the given RelaxNG schema. """
        
        relax_ng = etree.RelaxNG(file=relax_ng_file_path)
        relax_ng.validate(self._tree)

    ##############################################

    @staticmethod
    def _copy_dict(source_dict, renaming=None):

        """Copy a dictionary.

        The parameter *renaming* can be specified to perform a key renaming during the copy. It must
        be a dictionary where the keys correspond to the source keys and the values to the
        destination keys.
        """
        
        new_dict = {}
        for key, value in source_dict.iteritems():
            if renaming is not None and key in renaming:
                key = renaming[key]
            new_dict[key] = value
        
        return new_dict

    ##############################################

    @staticmethod
    def _convert_node_attributes(node, int_attributes=(), renaming=None):

        """Convert node attributes.

        The parameter *int_attributes* specifies a list of attributes that must be converted to
        integers.

        The parameter *renaming* can be specified to perform a key renaming during the copy. It must
        be a dictionary where the keys correspond to the source keys and the values to the
        destination keys.
        """

        attributes = GlSpecParser._copy_dict(node.attrib, renaming)
        for key in int_attributes:
            if key in attributes:
                attributes[key] = int(attributes[key], base=0)

        return attributes

    ##############################################

    def _iter_on_node(self, node, tag, callback):

        """ Iter on nodes and call the callback function if the tag match. """

        for child in node:
            if child.tag == tag:
                callback(child)

    ##############################################

    def _parse(self):

        """ Parse the XML file and create the Oriented Object interface. """

        root = self._tree.getroot()
        if root.tag != 'registry':
            raise NameError("Bad root")

        for node in root:
            # print type(node), node.tag
            if node.tag == 'types':
                self._iter_on_node(node, 'type', self._parse_type)
            elif node.tag == 'groups':
                self._iter_on_node(node, 'group', self._parse_group)
            elif node.tag == 'enums':
                self._parse_enums(node)
            elif node.tag == 'commands':
                self._iter_on_node(node, 'command', self._parse_command)
            elif node.tag == 'feature':
                self._parse_feature(node)
            elif node.tag == 'extensions':
                self._iter_on_node(node, 'extension', self._parse_extension)

    ##############################################

    def _parse_type(self, type_node):

        """ Parse ``<type>`` tags. """

        kwargs = dict(type_node.attrib)
        if type_node.text:
            kwargs['c_declaration_head'] = type_node.text.strip()
        if type_node.tail:
            # Fixme:
            #   <type>typedef void (<apientry/> *<name>GLDEBUGPROC</name>)(GLenum source,GLenum type,GLuint id,GLenum severity,GLsizei length,const GLchar *message,const void *userParam);</type>
            kwargs['c_declaration_tail'] = type_node.tail.strip()
        for node in type_node:
            if node.tag == 'apientry':
                kwargs['api_entry'] = True
            elif node.tag == 'name':
                kwargs['name'] = node.text
        type_= Type(**kwargs)
        self.types.register(type_)

    ##############################################

    def _parse_group(self, group_node):

        """ Parse ``<group>`` tags. """

        enum_name_list = [enum_node.attrib['name'] for enum_node in group_node]
        group = Group(enum_name_list=enum_name_list, **group_node.attrib)
        self.groups.register(group)

    ##############################################

    def _parse_enums(self, node):

        """ Parse ``<enums>`` tags. """

        attributes = self._convert_node_attributes(node,
                                                   int_attributes=('start', 'stop'),
                                                   renaming={'type': 'type_'})
        enums = Enums(**attributes)
        self.enums_list.append(enums)

        for enum_node in node:
            if enum_node.tag == 'enum':
                attributes = self._convert_node_attributes(enum_node,
                                                           int_attributes=('value',),
                                                           renaming={'type': 'type_'})
                enum = Enum(**attributes)
                enums.register(enum)

    ##############################################

    def _parse_command(self, command_node):

        """ Parse ``<command>`` tags. """

        command_kwargs = {}
        parameter_location = 0
        parameters = []
        for node in command_node:
            if node.tag == 'proto':
                # Fixme: api ?
                return_type = self._parse_parameter(node)
                command_kwargs['name'] = return_type.name
                command_kwargs['return_type'] = return_type
                return_type.name = None
            elif node.tag == 'param':
                parameter = self._parse_parameter(node, parameter_location)
                parameters.append(parameter)
                parameter_location += 1
        command = Command(parameters=parameters, **command_kwargs)
        self.commands.register(command)

    ##############################################

    def _parse_ctype(self, text, kwargs):

        """ Parse a C type and look for ``const`` and pointer multiplicity.

        Return the type without ``const`` and ``*``.
        """

        text = text.strip()

        if text.startswith('const'):
            kwargs['const'] = True
            text = text[5:]

        if text.endswith('**'):
            kwargs['pointer'] = 2
            text = text[:-2]
        if text.endswith('*const*'):
            kwargs['pointer'] = 2
            text = text[:-7]
        elif text.endswith('*'):
            kwargs['pointer'] = 1
            text = text[:-1]

        return text.strip()

    ##############################################

    def _parse_parameter(self, node, parameter_location=None):

        """ Parse ``<param>`` tags.

        The parameter *parameter_location* is not specified for return type.
        """

        # Case without text and tail:
        #   <param group="TextureTarget"><ptype>GLenum</ptype> <name>target</name></param>
        #   
        # Case wit text:
        #   <param group="CompressedTextureARB" len="imageSize">const void *<name>data</name></param>
        #   
        # Case with tail:
        #   <param len="COMPSIZE(uniformCount)"><ptype>GLuint</ptype> *<name>uniformIndices</name></param>
        #
        # Case with text and tail:
        #   <param len="count">const <ptype>GLchar</ptype> *const*<name>path</name></param>

        kwargs = self._copy_dict(node.attrib, renaming={'len': 'length'})
        for child in node:
            kwargs[child.tag] = child.text
            if child.tail:
                self._parse_ctype(child.tail, kwargs)

        if node.text is not None:
            text = self._parse_ctype(node.text, kwargs)
            if 'ptype' not in kwargs: # Fixme: and text?
                # for example: 'const void *'
                kwargs['ptype'] = text

        return Parameter(gl_types=self.types, location=parameter_location, **kwargs)

    ##############################################

    def _parse_interface(self, interface_node, interface):

        """ Parse nodes in a ``<required>`` or ``<removed>`` tag. """

        for item_node in interface_node:
            if item_node.tag != etree.Comment:
                kwargs = dict(item_node.attrib)
                kwargs['type_'] = item_node.tag
                interface.append_new(**kwargs)

    ##############################################

    def _parse_feature(self, feature_node):

        """ Parse ``<feature>`` tags. """

        kwargs = dict(feature_node.attrib)
        feature = Feature(**kwargs)
        self.feature_list.append(feature)
        for interface_node in feature_node:
            kwargs = dict(interface_node.attrib)
            if interface_node.tag == 'require':
                interface = RequiredInterface(**kwargs)
            elif interface_node.tag == 'remove':
                interface = RemovedInterface(**kwargs)
            self._parse_interface(interface_node, interface)
            feature.append(interface)

    ##############################################

    def _parse_extension(self, extension_node):

        """ Parse ``<extension>`` tags. """
        
        kwargs = dict(extension_node.attrib)
        extension = Extension(**kwargs)
        self.extension_list.append(extension)
        for interface_node in extension_node:
            kwargs = dict(interface_node.attrib)
            if interface_node.tag == 'require':
                interface = RequiredInterface(**kwargs)
            else:
                raise ValueError("Bad interface")
            self._parse_interface(interface_node, interface)
            extension.append(interface)

    ##############################################

    def generate_api(self, api, api_number, profile=None):

        """ Generate the API for a given API type (GL, GLES), version and profile.

        Return the list of enumerants and commands.
        """

        # Fixme: how to load an extension?
        #  explicitely, but check it is available
        #  check additional functions in libGL

        if api not in ('gl', 'gles'):
            raise ValueError("api must be 'gl' or 'gles'")

        self._logger.info("Generate API %s %s profile:%s" % (api, api_number, profile))

        all_api_enums = Enums(namespace=None)
        for enums in self.enums_list:
            all_api_enums.merge(api, enums)

        required_interface = RequiredInterface()
        for feature in self.feature_list:
            if feature.api == api and feature.api_number <= api_number:
                self._logger.debug('Merge features of %s API %s', feature.api, str(feature.api_number))
                for interface in feature:
                    if (profile is None or interface.profile is None
                        or interface.profile == profile):
                        required_interface.merge(interface)

        api_enums = Enums(namespace=api + '-' + str(api_number)) # + profile
        api_commands = Commands()
        for item in required_interface:
            if item.type == 'enum':
                api_enums.register(all_api_enums[item.name], primary_registration=False)
            elif item.type == 'command':
                api_commands.register(self.commands[item.name])

        return api_enums, api_commands

####################################################################################################
#
# End
#
####################################################################################################
