Prototype Translation
---------------------

The C language defines strictly by a prototype how to use the parameters and the output of a
function.

The OpenGL API only use fundamental types, pointer and array for parameters and return. The API do
not use structures or unions which are compound types. Example of fundamental types are integer,
float and char. Pointer or array are used to pass or return a multiple of a fundamental types. Also
the API use pointer parameters to return more than one items, as usual in C since a function can
only return one item at once. Pointers are also used to write data at a given place, which act as a
kind of input-output parameter <<???>>. We know if a pointer parameter is an input by the presence
of the *const* qualifier.

C Arrays do not embed their sizes, thus this information must be provided either implicitly, either
explicitly or using a sentinel, as for null-terminated string. The XML schema that defines the
OpenGL API provides partially this information. We can know exactly the size of an array, if the
array size is fixed or passed by a second parameter. However it the size depends of the context, for
example a query enum, the size is tagged as a computation from one or more parameters. But for these
cases the schema do not provide a formulae described by a meta-language.

The main concept of this wrapper is to use the XML data to generate a Python API with a natural
behaviour. 

Fundamental types
~~~~~~~~~~~~~~~~~

Prototypes which are only made of fundamental types, for example::

  void glBindBuffer (GLenum target, GLuint buffer)
  ->
  glBindBuffer (ParameterWrapper<unsigned int> target, ParameterWrapper<unsigned int> buffer)

are translated to :class:`ParameterWrapper` and passed by copy. These parameters are the input of
the function.

Input parameters passed as pointer
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Input parameters passed as pointer are necessarily qualified as const.

They are managed by an :class:`InputArrayWrapper` when the size is not tagged as computed in the XML
registry. For these cases, the pointer parameter takes the place of the size parameter and its
parameter slot is removed of the prototype in Python. The size is automatically filled by the
wrapper. For example::

  void glBufferData (GLenum target, GLsizeiptr size, const void * [size] data, GLenum usage)
  ->
  glBufferData (ParameterWrapper<unsigned int> target,
                InputArrayWrapper<const void * [size]> data,
                ParameterWrapper<unsigned int> usage)

  void glUniform3fv (GLint location, GLsizei count, const GLfloat * [count] value)
  ->
  glUniform3fv (ParameterWrapper<int> location, InputArrayWrapper<const float * [count]> value)

<<INVERSE Pointer <-> Size>> <<case with more than one pointer>>

The array can be passed as an iterable or a numpy array. A missing information in the actual schema
is due to the fact the size can represents the number of elements or a number of byte. Usually a
generic pointer indicates a size specified in byte. <<TO BE CHECKED>>

Some functions have ``**`` pointer parameters. The function *glShaderSource* is an interesting case
since it features this kind of pointer and the size parameter is used for two parameters::

  void glShaderSource (GLuint shader, GLsizei count, const GLchar ** [count] string, const GLint * [count] length)
  ->
  glShaderSource (ParameterWrapper<unsigned int> shader,
                  InputArrayWrapper<const char ** [count]> string)

According to the specification, the *string* parameter is an array of (optionally) null-terminated
strings and the *length* pointer must be set to NULL in this case.

Output parameters passed as pointer
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

These parameters are not qualified as const and are managed by an :class:`OutputArrayWrapper` when
the size is not tagged as computed.

The pointer parameter takes the place of the size parameter and its parameter slot is removed of
the prototype in Python. The size is automatically filled by the wrapper.

If the pointer is generic, then the array is passed as an Numpy array and the size is specified in
byte. For example::

  void glGetBufferSubData (GLenum target, GLintptr offset, GLsizeiptr size, void * [size] data)
  ->
  glGetBufferSubData (ParameterWrapper<unsigned int> target, ParameterWrapper<ptrdiff_t> offset,
                      OutputArrayWrapper<void * [size]> data)
  -> None

If the pointer is of \*char type, then the size is passed by the user and a string is returned. For
example::

  void glGetShaderSource (GLuint shader, GLsizei bufSize, GLsizei * [1] length, GLchar * [bufSize] source)
  ->
  glGetShaderSource (ParameterWrapper<unsigned int> shader, OutputArrayWrapper<char * [bufSize]> source)
  -> source

If the user passes an Numpy array, then the data type is checked and the size is set by the wrapper.
If the user passes a size, then a Numpy array (or a list) is created and then returned::

  void glGenBuffers (GLsizei n, GLuint * [n] buffers)
  ->
  glGenBuffers (OutputArrayWrapper<unsigned int * [n]> buffers)  

Parameter passed by reference
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

A parameter passed by reference is identified in the prototype as a non const pointer with a fixed
size of 1. Reference parameter are removed in the Python prototype and their values set by the
command are returned in their prototype order. For example, this function features 3 parameters
passed by reference::

  void glGetActiveUniform (unsigned int program, unsigned int index, int bufSize,
                           int * [1] length, int * [1] size, unsigned int * [1] type,
                           char * [bufSize] name)
  ->
  glGetActiveUniform (ParameterWrapper<unsigned int> program, ParameterWrapper<unsigned int> index,
                      OutputArrayWrapper<char * [bufSize]> name)
  -> name, length, size, type

Parameter passed as pointer
~~~~~~~~~~~~~~~~~~~~~~~~~~~

When the size is tagged as computed, parameters are managed by a :class:`PointerWrapper` and all the
parameters involved in the the size determination must be passed as input parameter::

  void glBindAttribLocation (GLuint program, GLuint index, const GLchar * name)
  ->
  glBindAttribLocation (ParameterWrapper<unsigned int> program, ParameterWrapper<unsigned int> index,
                        PointerWrapper<const char *> name)

<<Fixme null-terminated>>

For example this function features a generic pointer *pixels* which must be passed as an Numpy
array::

  void glTexImage1D (GLenum target, GLint level, GLint internalformat, GLsizei width, GLint border,
                     GLenum format, GLenum type, const void * [COMPSIZE(format,type,width)] pixels)
  ->
  glTexImage1D (ParameterWrapper<unsigned int> target, ParameterWrapper<int> level,
                ParameterWrapper<int> internalformat, ParameterWrapper<int> width,
                ParameterWrapper<int> border, ParameterWrapper<unsigned int> format,
                ParameterWrapper<unsigned int> type,
                PointerWrapper<const void * [COMPSIZE(format,type,width)]> pixels)
  -> None

This example is interesting, since the *width* parameter can be deduced from the shape of the Numpy
array.

This function features a typed pointer::

  void glGetIntegerv (GLenum pname, GLint * [COMPSIZE(pname)] data)
  ->
  glGetIntegerv (ParameterWrapper<unsigned int> pname, PointerWrapper<int * [COMPSIZE(pname)]> data)
  -> None

Return parameter passed as pointer
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The wrapper only supports null-terminated string, for example::

  const GLubyte * glGetString (GLenum name)
  ->
  glGetString (ParameterWrapper<unsigned int> name)

.. End
