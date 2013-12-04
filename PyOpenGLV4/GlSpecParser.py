####################################################################################################
#
# PyOpenGLV4 - An OpenGL V4 layer on top of PyOpengl.
# Copyright (C) 2013 Salvaire Fabrice
#
####################################################################################################

"""
#. Create an openGL context
#. Query OpenGL to get the version
#. Build the API (gl/gles, api_number, profile)
   Check OpenGL version >= api_number
#. Install wrapper ?

void glGenBuffers(GLsizei n,  GLuint * buffers)

* const => input
* len=1 => input via pointer
* len=n => output array
"""

# Fixme: Python keyword
#   len, type

####################################################################################################

from lxml import etree

####################################################################################################

class NameDict(dict):

   ##############################################

    def register(self, item):
        
        if item.name in self:
            raise IndexError("item %s already registered" % (item.name))

        self[item.name] = item

   ##############################################

    def unregister(self, item_name):
        
        del self[item_name]

####################################################################################################

class ApiNumber(object):

    ##############################################

    def __init__(self, number):

        self.major, self.minor = [int(x) for x in number.split('.')]

    ##############################################

    def __int__(self):

        return self.major * 1000 + self.minor

    ##############################################

    def __str__(self):

        return "%u.%u" % (self.major, self.minor)

    ##############################################

    def __le__(self, api_number):

        return int(self) <= int(api_number)

####################################################################################################

class Types(object):

    """
    API types (<types> tag)
    
    The <types> tag contains individual <type> tags describing each of the derived types used in the
    API.
    """

   ##############################################

    def __init__(self):

        self.types = [] # name is not uniq
        self.c_types = {}

   ##############################################

    def register(self, type_):

        self.types.append(type_)
        # Fixme: gles ...
        if type_.c_type is not None and type_.requires != 'khrplatform':
            if type_.name not in self.c_types:
                self.c_types[type_.name] = type_
            else:
                raise NameError("%s" % (type_.name))

    ##############################################

    def translate_gl_type(self, gl_type):

        if gl_type in self.c_types:
            return self.c_types[gl_type]
        else:
            # None ?
            return gl_type
        # raise NameError("Failed to translate type %s" % (gl_type))

####################################################################################################


class Type(object):

    """
    Each <type> tag contains legal C code, with attributes or embedded tags denoting the type name.
    
    Attributes of <type> tags
    -------------------------
    
        requires
            another type name this type requires to complete its definition.
        
        name
            name of this type (if not defined in the tag body).
        
        api
            an API name (see <feature> below) which specializes this definition
            of the named type, so that the same API types may have different definitions for
            e.g. GL ES and GL.
        
        comment
            arbitrary string (unused).
    
     Contents of <type> tags
     ------------------------
    
    <type> contains text which is legal C code for a type declaration. It may also contain embedded
    tags:
    
        <apientry/>
            insert a platform calling convention macro here during header generation, used mostly
            for function pointer types.
    
        <name>
            contains the name of this type (if not defined in the tag attributes).
    """

    c_types = (
        'char',
        'int8_t',
        'uint8_t',
        'short',
        'int32_t',
        'int',
        'int64_t',
        'uint64_t',
        'float',
        'float_t',
        'double',
        'intptr_t',
        'ptrdiff_t',
        'ssize_t',
        'void',
        )

    ##############################################

    def __init__(self,
                 name,
                 c_code=None, requires=None, api=None, comment=None, apientry=False,
                 ):

        self.name = name
        self.c_code = c_code
        self.apientry = apientry
        self.requires = requires
        self.api = api
        self.comment = comment

        self.unsigned = False
        self.pointer = False
        self.c_type = None

        if (self.c_code is not None
            and self.c_code.count('\n') == 0
            and self.c_code.startswith('typedef')
            and not self.c_code.endswith('(')):
            for token in self.c_code.split()[1:]:
                if token.startswith('khronos_'):
                    token = token[len('khronos_'):]
                if token == 'unsigned':
                    self.unsigned = True
                elif token == 'signed':
                    self.unsigned = False
                elif token == '*':
                    self.pointer = True
                elif token in self.c_types:
                    self.c_type = token

    ##############################################

    def __repr__(self):

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

    """
    Enumerant Groups (<groups> tag)
    
    The <groups> tags contain individual <group> tags describing some of the group annotations used
    for return and parameter types.
    
    Attributes of <groups> tags
    ---------------------------
    
    None
    
    Contents of <groups> tags
    -------------------------
    
    Each <groups> block contains zero or more <group> tags, in arbitrary order (although they are
    typically ordered by group name, to improve human readability).
    """

####################################################################################################

class Group(object):

    """
    Enumerant Group (<group> tag)
    
    Each <group> tag defines a single group annotation.
    
    Attributes of <group> tags
    --------------------------
    
    name
        group name, an arbitrary string for grouping a set of enums together within a broader
        namespace.
    
    Contents of <group> tags
    ------------------------
    
    <group> tags may contain zero or more <enum> tags. Each <enum> tag may contain only a name
    attribute, which should correspond to a <enum> definition in an <enums> block.
    
    Meaning of <group> tags
    -----------------------
    
    If a <proto> or <param> tag of a <command> has a group attribute defined, and that attribute
    matches a <group> name, then the return type or parameter type is considered to be constrained
    to values defined by the corresponding <group>. C language bindings do not attempt to enforce
    this constraint in any way, but other language bindings may try to do so.
    """

    ##############################################

    def __init__(self,
                 name, enum_name_list,
                 comment=None,
                 ):

        self.name = name
        self.comment = comment

        self._enum_name_list = enum_name_list

####################################################################################################

class Enums(object):

    """
    Enumerant Blocks (<enums> tag)

    The <enums> tags contain individual <enum> tags describing each of the token (enumerant) names
    used in the API.

    Attributes of <enums> tags
    --------------------------

    namespace
        a string for grouping many different enums together, currently unused but typically
        something like GL for all enums in the OpenGL / OpenGL ES shared namespace. Multiple <enums>
        tags can share the same namespace.

    type 
       a string describing the data type of the values of this group of enums, currently unused. The
       only string used at present in the is bitmask.

    start, end
       integers defining the start and end of a reserved range of enumerants for a particular
       vendor or purpose. start must be <= end. These fields define formal enumerant allocations
       within a namespace, and are made by the Khronos Registrar on request from implementers
       following the enum allocation policy.

    vendor
         string describing the vendor or purposes to whom a reserved range of enumerants is
         allocated.

    comment
         arbitrary string (unused)

    group
        group name, an arbitrary string.    

    Contents of <enums> tags
    ------------------------

    Each <enums> block contains zero or more <enum> and <unused> tags, in arbitrary order (although
    they are typically ordered by sorting on enumerant values, to improve human readability).
    """

    ##############################################

    def __init__(self,
                 namespace,
                 group=None, type=None, start=None, end=None, vendor=None, comment=None,
                 ):

        self.namespace = namespace
        self.group = group
        self.type = type
        self.start = start
        self.end = end
        self.vendor = vendor
        self.comment = comment

        self._enum_name_dict = {}
        self._enum_value_dict = {}

    ##############################################

    def __iter__(self):

        return self._enum_name_dict.itervalues()

    ##############################################

    def __getitem__(self, key):

        try:
            return self._enum_name_dict[key]
        except KeyError:
            try:
                return self._enum_value_dict[key]
            except KeyError:
                raise KeyError("Any enum having this name or value: " + str(key))

   ##############################################

    def register(self, enum, primary_registration=True):
        
        if enum.name in self._enum_name_dict:
            try:
                namespace = enum.enums.namespace
            except Exception:
                namespace = '(namespace not yed defined)'
            raise IndexError("enum %s already registered in %s" % (enum.name, namespace))

        self._enum_name_dict[enum.name] = enum
        self._enum_value_dict[enum.value] = enum
        if primary_registration:
            if enum.enums is not None:
                raise NameError('Back enums reference is already affected')
            else:
                enum.enums = self

   ##############################################

    def unregister(self, enum_name):

        enum = self._enum_name_dict[enum_name]
        del self._enum_value_dict[enum.value]
        del self._enum_name_dict[enum_name]

    ##############################################

    def merge(self, api, enums):

        for enum in enums._enum_name_dict.itervalues():
            if enum.api is None or enum.api == api:
                self.register(enum, primary_registration=False)

####################################################################################################

class Enum(object):

    """
    Enumerants (<enum> tag)

    Each <enum> tag defines a single GL (or other API) token.

    Attributes of <enum> tags
    -------------------------
    
    value
        enumerant value, a legal C constant (usually a hexadecimal integer).
    
    name
        enumerant name, a legal C preprocessor token name.
    
    api
        an API name which specializes this definition of the named enum, so that different APIs may
        have different values for the same token (used to address a few accidental incompatibilities
        between GL and GL ES).
    
    type
        legal C suffix for the value to force it to a specific type. Currently only u and ull are
        used, for unsigned 32- and 64-bit integer values, respectively.  Separated from the value
        field since this eases parsing and sorting of values, and is rarely used.
    
    alias
        name of another enumerant this is an alias of, used where token names have been changed as a
        result of profile changes or for consistency purposes.  An enumerant alias is simply a
        different name for the exact same value. At present, enumerants which are promoted from
        extension to core API status are not tagged as aliases - just enumerants tagged as aliases
        in the Changed Tokens sections of appendices to the OpenGL Specification. This might change
        in the future.
    
    comment
        arbitrary string (unused).

    Contents of <enum> tags
    -----------------------

    <enum> tags have no allowed contents. All information is contained in the attributes.
    """

    ##############################################

    def __init__(self,
                 name, value,
                 type=None, alias=None, comment=None, api=None,
                 ):

        self.name = name
        self.value = value
        self.type = type
        self.alias = alias
        self.comment = comment
        self.api = api
        self.enums = None

    ##############################################

    def __repr__(self):

        return "Enum %s = %s" % (self.name, hex(self.value))

    ##############################################

    def __str__(self):

        return self.name

    ##############################################

    def __int__(self):

        return self.value

    ##############################################

    def repr_long(self):

        return repr(self) + " (type: %(type)s, alias: %(alias)s, api: %(api)s, comment: %(comment)s)" % self.__dict__

####################################################################################################

class Commands(NameDict):

    """
    Command Blocks (<commands> tag)
    
    The <commands> tag contains definitions of each of the functions (commands) used in the API.
    
    Attributes of <commands> tags
    -----------------------------
    
    namespace
        a string defining the namespace in which commands live, currently unused but typically
        something like GL.
    
    Contents of <commands> tags
    ---------------------------
    
    Each <commands> block contains zero or more <command> tags, in arbitrary order (although they
    are typically ordered by sorting on the command name, to improve human readability).
    """

####################################################################################################

class Command(object):
    
    """
    Commands (<command> tag)
    
    The <command> tag contains a structured definition of a single API command (function).
    
    Attributes of <command> tags
    ----------------------------
    
    comment
       arbitrary string (unused).
    
    Contents of <command> tags
    --------------------------
    
    * <proto> must be the first element, and is a tag defining the C function prototype of a command
        as described below, up to the function name but not including function parameters.
    
    * <param> elements for each command parameter follow, defining its name and type, as described
        below. If a command takes no arguments, it has no <param> tags.
    
    Following these elements, the remaining elements in a <command> tag are optional and may be in
    any order:
    
    * <alias> has no attributes and contains a string which is the name of another command this
        command is an alias of, used when promoting a function from extension to ARB or ARB to API
        status. A command alias describes the case where there are two function names which resolve
        to the same client library code, so (for example) the case where a command is promoted but
        is also given different GLX protocol would not be an alias in this sense.
    
    * <vecequiv> has no attributes and contains a string which is the name of another command which
        is the vector equivalent of this command. For example, the vector equivalent of glVertex3f
        is glVertex3fv.
    
    * <glx> defines GLX protocol information for this command, as described below.  Many GL commands
        don't have GLX protocol defined, and other APIs such as EGL and WGL don't use GLX at all.
    
    Command prototype (<proto> tags)
    --------------------------------
    
    The <proto> tag defines the return type and name of a command.
    
    Attributes of <proto> tags
    --------------------------
    
    group
        group name, an arbitrary string.
    
    If the group name is defined, it may be interpreted as described in <ref>.
    
    Contents of <proto> tags
    ------------------------
    
    The text elements of a <proto> tag, with all other tags removed, is legal C code describing the
    return type and name of a command. In addition it may contain two semantic tags:
    
    * The <ptype> tag is optional, and contains text which is a valid type name found in <type> tag,
        and indicates that this type must be previously defined for the definition of the command to
        succeed. Builtin C types, and any derived types which are expected to be found in other
        header files, should not be wrapped in <ptype> tags.
    
    * The <name> tag is required, and contains the command name being described.
    """

    ##############################################

    def __init__(self,
                 name, ptype,
                 parameters=(),
                 ):

        self.name = name
        self.return_type = ptype
        self.parameters = parameters

    ##############################################

    def __str__(self):

        return self.name

    ##############################################

    def __repr__(self):

        return '%s %s (%s)' % (self.return_type, self.name,
                               ', '.join([repr(parameter) for parameter in self.parameters]))

    ##############################################

    def prototype(self, types):

        if self.return_type != 'void':
            gl_type = types.translate_gl_type(self.return_type)
            return_type = repr(gl_type)
        else:
            return_type = 'void'

        return '%s %s (%s)' % (return_type, self.name,
                               ', '.join([parameter.prototype(types) for parameter in self.parameters]))

    ##############################################

    def argument_types(self, types):

        return [parameter.translate_gl_type(types) for parameter in self.parameters]

####################################################################################################

class Parameter(object):

    """
    Command parameter (<param> tags)
    --------------------------------
    
    The <param> tag defines the type and name of a parameter.
    
    Attributes of <param> tags
    --------------------------
    
    group
        group name, an arbitrary string.
    
    len
        parameter length, either an integer specifying the number of elements of the parameter
        <ptype>, or a complex string expression with poorly defined syntax, usually representing a
        length that is computed as a combination of other command parameter values, and possibly
        current GL state as well.
    
    If the group name is defined, it may be interpreted as described in <ref>.
    
    Contents of <param> tags
    ------------------------
    
    The text elements of a <param> tag, with all other tags removed, is legal C code describing the
    type and name of a function parameter. In addition it may contain two semantic tags:
    
    * The <ptype> tag is optional, and contains text which is a valid type name found in <type> tag,
        and indicates that this type must be previously defined for the definition of the command to
        succeed. Builtin C types, and any derived types which are expected to be found in other
        header files, should not be wrapped in <ptype> tags.
    
    * The <name> tag is required, and contains the command name being described.
    """

    ##############################################

    def __init__(self,
                 name,
                 ptype=None, group=None, length=None, const=False, pointer=0,
                 ):

        self.name = name
        self.type = ptype
        self.group = group
        self.const = const
        self.pointer = pointer

        self.size_parameter = None
        self.array_size = None
        try:
            self.array_size = int(length)
        except ValueError:
            self.computed_size = length.startswith('COMPSIZE')
            self.size_parameter = length
        except TypeError:
            pass

    ##############################################

    def _format_type(self, type_string):
        
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

    def __repr__(self):

        return '%s %s' % (self._format_type(self.type), self.name)

    ##############################################

    def prototype(self, types):

        return '%s %s' % (self.translate_gl_type(types), self.name)

    ##############################################

    def translate_gl_type(self, types):

        gl_type = types.translate_gl_type(self.type)
        return self._format_type(repr(gl_type))

####################################################################################################

class Feature(object):

    """
    API Features / Versions (<feature> tag)
    
    API features are described in individual <feature> tags. A feature is the set of interfaces
    (enumerants and commands) defined by a particular API and version, such as OpenGL 4.0 or OpenGL
    ES 3.0, and includes all API profiles of that version.
    
    Attributes of <feature> tags
    ----------------------------
    
    api
        API name this feature is for (see <ref>), such as gl or gles2.
    
    name
        version name, used as the C preprocessor token under which the version's interfaces are
        protected against multiple inclusion. Example: GL_VERSION_4_2.
    
    protect
        an additional preprocessor token used to protect a feature definition. Usually another
        feature or extension name. Rarely used, for odd circumstances where the definition of a
        feature or extension requires another to be defined first.
    
    number
        feature version number, usually a string interpreted as majorNumber.minorNumber. Example:
        4.2.
    
    comment
        arbitrary string (unused)
    
    Contents of <feature> tags
    --------------------------
    
    Zero or more <require> and <remove> tags (see <ref>), in arbitrary order.  Each tag describes a
    set of interfaces that is respectively required for, or removed from, this feature, as described
    below.
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

        self._interface_list = []

    ##############################################

    def __iter__(self):

        return iter(self._interface_list)

    ##############################################

    def append(self, interface):

        self._interface_list.append(interface)

####################################################################################################

class Extension(object):

    """
    Extension Blocks (<extensions> tag)
    
    The <extensions> tag contains definitions of each of the extenions which are defined for the
    API.
    
    Attributes of <extensions> tags
    -------------------------------
    
    None.
    
    Contents of <extensions> tags
    -----------------------------
    
    Each <extensions> block contains zero or more <extension> tags, each describing an API
    extension, in arbitrary order (although they are typically ordered by sorting on the extension
    name, to improve human readability).
    
    API Extensions (<extension> tag)
    --------------------------------
    
    API extensions are described in individual <extension> tags. An extension is the set of
    interfaces defined by a particular API extension specification, such as
    ARB_multitexture. <extension> is similar to <feature>, but instead of having version and profile
    attributes, instead has a supported attribute, which describes the set of API names which the
    extension can potentially be implemented against.
    
    Attributes of <extension> tags
    ------------------------------
    
    supported
        a regular expression, with an implicit ^ and $ bracketing it, which should match the api tag
        of a set of <feature> tags.
    
    protect
        an additional preprocessor token used to protect an extension def- inition. Usually another
        feature or extension name. Rarely used, for odd cir- cumstances where the definition of an
        extension requires another to be defined first.
    
    comment
        arbitrary string (unused)
    
    Contents of <extension> tags
    ----------------------------
    
    Zero or more <require> and <remove> tags (see <ref>), in arbitrary order.  Each tag describes a
    set of interfaces that is respectively required for, or removed from, this extension, as
    described below.
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

        self._interface_list = []

    ##############################################

    def append(self, interface):

        self._interface_list.append(interface)

####################################################################################################

class RequiredInterface(object):

    """
    Required and Removed Interfaces (<require> and <remove> tags)
    
    A <require> block defines a set of interfaces (types, enumerants and commands) required by a
    <feature> or <extension>. A <remove> block defines a set of interfaces removed by a <feature>
    (this is primarily useful for the OpenGL core profile, which removed many interfaces -
    extensions should never remove interfaces, although this usage is allowed by the schema). Except
    for the tag name and behavior, the contents of <require> and <remove> tags are identical.
    
    Attributes of <require> and <remove> tags
    -----------------------------------------
    
    profile
        string name of an API profile. Interfaces in the tag are only re- quired (or removed) if the
        specified profile is being generated. If not specified, interfaces are required (or removed)
        for all API profiles.
    
    comment
        arbitrary string (unused)
    
    api
        an API name (see <ref>). Interfaces in the tag are only required (or removed) if the
        specified API is being generated. If not specified, interfaces are required (or removed) for
        all APIs. The api attribute is only supported inside <extension> tags, since <feature> tags
        already define a specific API.
    
    Contents of <require> and <remove> tags
    ---------------------------------------
    
    Zero or more of the following tags, in any order:
    
    * <command> specifies an required (or removed) command defined in a <commands> block. The tag
        has no content, but contains elements:
    
        name
            name of the command (required).
    
        comment
            arbitrary string (optional and unused).
    
    * <enum> specifies an required (or removed) enumerant defined in a <enums> block. The tag has no
        content, but contains elements:
    
        name
            name of the enumerant (required).
    
        comment
            arbitrary string (optional and unused).
    
    * <type> specifies a required (or removed) type defined in a <types> block.  Most types are
        picked up implicitly by using the <ptype> tags of commands, but in a few cases, additional
        types need to be specified explicitly (it is unlikely that a type would ever be removed,
        although this usage is allowed by the schema). The tag has no content, but contains
        elements:
    
        name
            name of the type (required).
    
        comment
            arbitrary string (optional and unused).
    """

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

        item = RequiredItem(**kwargs)
        self.append(item)

    ##############################################

    def merge(self, interface):

        if isinstance(interface, RequiredInterface):
            self._items = self._items.union(interface._items)
        else:
            self._items = self._items.difference(interface._items)

####################################################################################################

class RequiredItem(object):

    ##############################################

    def __init__(self,
                 type,
                 name, comment=None,
                 ):

        self.type = type
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

    ##############################################

    def append_new(self, **kwargs):

        item = RemovedItem(**kwargs)
        self.append(item)

####################################################################################################

class RemovedItem(RequiredItem):
    pass

####################################################################################################

class GlSpecParser(object):

    ##############################################

    def __init__(self, xml_file_path, relax_ng_file_path=None):

        self._tree = etree.parse(xml_file_path)

        if relax_ng_file_path is not None:
            self._validate(relax_ng_file_path)

        self.types = Types()
        self.groups = Groups()
        self.commands = Commands()
        self.enums_list = []
        self.feature_list = []
        self.extension_list = []

        self._parse()

    ##############################################

    def _validate(self, relax_ng_file_path):

        relax_ng = etree.RelaxNG(file=relax_ng_file_path)
        relax_ng.validate(self._tree)

    ##############################################

    def _to_int(self, value):

        if value.startswith('0x'):
            base = 16
        else:
            base = 10

        return int(value, base)

    ##############################################

    def _convert_node_attributes(self, node, int_attributes=()):

        attributes = dict(node.attrib)
        for key in int_attributes:
            if key in attributes:
                attributes[key] = self._to_int(attributes[key])

        return attributes

    ##############################################

    def _iter_on_node(self, node, tag, callback):

        for child in node:
            if child.tag == tag:
                callback(child)

    ##############################################

    def _parse(self):

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

        kwargs = dict(type_node.attrib)
        if type_node.text is not None:
            kwargs['c_code'] = type_node.text.strip()
        for node in type_node:
            if node.tag == 'apientry':
                kwargs['apientry'] = True
            elif node.tag == 'name':
                kwargs['name'] = node.text
        type_= Type(**kwargs)
        self.types.register(type_)

    ##############################################

    def _parse_group(self, group_node):

        enum_name_list = [enum_node.attrib['name'] for enum_node in group_node]
        group = Group(enum_name_list=enum_name_list, **group_node.attrib)
        self.groups.register(group)

    ##############################################

    def _parse_enums(self, node):

        attributes = self._convert_node_attributes(node, int_attributes=('start', 'stop'))
        enums = Enums(**attributes)
        self.enums_list.append(enums)

        for enum_node in node:
            if enum_node.tag == 'enum':
                attributes = self._convert_node_attributes(enum_node, int_attributes=('value',))
                enum = Enum(**attributes)
                enums.register(enum)
                # print enum

    ##############################################

    def _parse_command(self, command_node):

        command_kwargs = None
        parameters = []
        for node in command_node:
            if node.tag == 'proto':
                command_kwargs = {child.tag:child.text.strip() for child in node}
                if 'ptype' not in command_kwargs:
                    command_kwargs['ptype'] = node.text.strip()
            elif node.tag == 'param':
                parameter = self._parse_parameter(node, command_kwargs)
                parameters.append(parameter)
        command = Command(parameters=parameters, **command_kwargs)
        self.commands.register(command)

    ##############################################

    def _parse_parameter(self, node, command_kwargs):

        kwargs = dict(node.attrib)
        # Fixme
        if 'len' in kwargs:
            kwargs['length'] = kwargs['len']
            del kwargs['len']
        for child in node:
            kwargs[child.tag] = child.text
            if child.tail:
                text = child.tail.strip()
                if text.endswith('**'):
                    kwargs['pointer'] = 2
                elif text.endswith('*'):
                    kwargs['pointer'] = 1

        # Fixme: debug, remove
        ### if command_kwargs['name'] == 'glGetAttribLocation':
        ###     print node.text, node.tail
        ###     for child in node:
        ###         print child.tag, child.text, child.tail

        if node.text is not None:
            text = node.text.strip()
            if 'ptype' not in kwargs:
                # for example: 'const void *'
                kwargs['ptype'] = node.text.strip()
            else:
                if text.startswith('const'):
                    kwargs['const'] = True

        return Parameter(**kwargs)

    ##############################################

    def _parse_interface(self, interface_node, interface):

        for item_node in interface_node:
            if item_node.tag != etree.Comment:
                kwargs = dict(item_node.attrib)
                kwargs['type'] = item_node.tag
                interface.append_new(**kwargs)

    ##############################################

    def _parse_feature(self, feature_node):

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

    def generate_api(self, api, api_number):

        all_api_enums = Enums(namespace=None)
        for enums in self.enums_list:
            all_api_enums.merge(api, enums)

        required_interface = RequiredInterface()
        for feature in self.feature_list:
            if feature.api == api and feature.api_number <= api_number:
                # print 'Merge %s %s' % (feature.api, str(feature.api_number))
                for interface in feature:
                    required_interface.merge(interface)

        api_enums = Enums(namespace=api + '-' + str(api_number))
        api_commands = Commands()
        for item in required_interface:
            if item.type == 'enum':
                api_enums.register(all_api_enums[item.name], primary_registration=False)
            elif item.type == 'command':
                api_commands.register(self.commands[item.name])

        if True:
            # for enum in api_enums:
            #     print repr(enum)
            for command in api_commands.itervalues():
                # print repr(command)
                # print command.prototype(self.types)
                # print command.argument_types(self.types)
                print command.name, self.types.translate_gl_type(command.return_type), command.argument_types(self.types)
                
####################################################################################################

if __name__ == '__main__':
    
    import os

    source_path = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
    # print source_path
    gl_xml_file_path = os.path.join(source_path, 'doc/registry-api/gl.xml')
    # trang -I rnc -O rng doc/registry-api/registry.rnc doc/registry-api/registry-rng.xml
    relax_ng_file_path = os.path.join(source_path, 'doc/registry-api/registry-rng.xml')
    gl_spec_parser = GlSpecParser(gl_xml_file_path, relax_ng_file_path)
    gl_spec_parser.generate_api(api='gl', api_number=ApiNumber('2.0'))

####################################################################################################
#
# End
#
####################################################################################################
