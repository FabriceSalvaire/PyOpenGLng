####################################################################################################
#
# PyOpenGLV4 - An OpenGL V4 layer on top of PyOpengl.
# Copyright (C) 2013 Salvaire Fabrice
#
####################################################################################################

####################################################################################################

from lxml import etree

####################################################################################################

class Groups(object):

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

    ##############################################

    def __init__(self):

        self._group_list = []

   ##############################################

    def append(self, group):
        
        self._group_list.append(group)

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

        self._enum_list = []

   ##############################################

    def append(self, enum):
        
        self._enum_list.append(enum)
 
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

    ##############################################

    def __repr__(self):

        return "Enum %s = %s" % (self.name, hex(self.value))

    ##############################################

    def repr_long(self):

        return repr(self) + " (type: %(type)s, alias: %(alias)s, api: %(api)s, comment: %(comment)s)" % self.__dict__

####################################################################################################

class Commands(object):

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

    ##############################################

    def __init__(self):

        self._command_list = []

   ##############################################

    def append(self, group):
        
        self._command_list.append(group)

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
                 name,
                 return_type=None, parameters=(),
                 ):

        self.name = name
        self.return_type = return_type
        self.parameters = parameters

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
                 ptype=None, group=None, len=None,
                 ):

        self.name = name
        self.type = ptype
        self.group = group
        self.len = len

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
        self.number = number
        self.protect = protect
        self.comment = comment

        self._interface_list = []

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

        self._items = []

    ##############################################

    def append(self, **kwargs):

        item = RequiredItem(**kwargs)
        self._items.append(item)

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

####################################################################################################

class RemovedInterface(RequiredInterface):

    ##############################################

    def append(self, **kwargs):

        item = RemovedItem(**kwargs)
        self._items.append(item)

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

        self.enums_list = []
        self.groups = Groups()
        self.commands = Commands()
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

    def _parse(self):

        root = self._tree.getroot()
        if root.tag != 'registry':
            raise NameError("Bad root")

        for node in root:
            # print type(node), node.tag
            if node.tag == 'types':
                pass
            elif node.tag == 'groups':
                for group_node in node:
                    self._parse_group(group_node)
            elif node.tag == 'enums':
                self._parse_enums(node)
            elif node.tag == 'commands':
                for command_node in node:
                    self._parse_command(command_node)
            elif node.tag == 'feature':
                self._parse_feature(node)
            elif node.tag == 'extensions':
                for extension_node in node:
                    self._parse_extension(extension_node)

    ##############################################

    def _parse_group(self, group_node):

        if group_node.tag != 'group':
            raise ValueError("Bad group")

        enum_name_list = [enum_node.attrib['name'] for enum_node in group_node]
        group = Group(enum_name_list=enum_name_list, **group_node.attrib)
        self.groups.append(group)

    ##############################################

    def _parse_enums(self, node):

        attributes = self._convert_node_attributes(node, int_attributes=('start', 'stop'))
        enums = Enums(**attributes)
        self.enums_list.append(enums)

        for enum_node in node:
            if enum_node.tag == 'enum':
                attributes = self._convert_node_attributes(enum_node, int_attributes=('value',))
                enum = Enum(**attributes)
                enums.append(enum)
                # print enum

    ##############################################

    def _parse_command(self, command_node):

        if command_node.tag != 'command':
            raise ValueError("Bad group")

        return_type = None
        command_name = None
        parameters = []
        for node in command_node:
            if node.tag == 'proto':
                return_type = node.text
                if return_type is not None:
                    return_type = return_type.strip()
                if len(node) != 1 and node[0].tag == 'name':
                    raise ValueError("Bad proto")
                command_name = node[0].text
            elif node.tag == 'param':
                kwargs = dict(node.attrib)
                kwargs.update({child.tag:child.text for child in node})
                parameter = Parameter(**kwargs)
                parameters.append(Parameter)
        command = Command(command_name, return_type, parameters)
        self.commands.append(command)

    ##############################################

    def _parse_interface(self, interface_node, interface):

        for item_node in interface_node:
            if item_node.tag != etree.Comment:
                kwargs = dict(item_node.attrib)
                kwargs['type'] = item_node.tag
                interface.append(**kwargs)

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

####################################################################################################

if __name__ == '__main__':
    
    import os

    source_path = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
    print source_path
    gl_xml_file_path = os.path.join(source_path, 'doc/registry-api/gl.xml')
    # trang -I rnc -O rng doc/registry-api/registry.rnc doc/registry-api/registry-rng.xml
    relax_ng_file_path = os.path.join(source_path, 'doc/registry-api/registry-rng.xml')
    gl_spec_parser = GlSpecParser(gl_xml_file_path, relax_ng_file_path)

####################################################################################################
#
# End
#
####################################################################################################
