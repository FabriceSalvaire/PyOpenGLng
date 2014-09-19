.. _tools-page:

=====
Tools
=====

The command :command:`query-opengl-api` in the :file:`bin` directory provides a tool to query the
OpenGL API using the :obj:`PyOpenGLng.GlApi` module.

The online help could be printed on the terminal using the command::

    > query-opengl-api --help

    usage: query-opengl-api [-h] --api {gl,gles} --api-number API_NUMBER
                            [--profile {core,compatibility}] [--validate]
                            [--translate-type] [--build-wrapper] [--summary]
                            [--list-enums] [--list-commands]
                            [--list-multi-referenced-pointer-commands]
                            [--list-computed-size-commands]
                            [--list-multi-pointer-commands] [--enum ENUM]
                            [--command COMMAND] [--man MAN]
    
    A tool to query the OpenGL API
    
    optional arguments:
      -h, --help            show this help message and exit
      --api {gl,gles}       API (default: None)
      --api-number API_NUMBER
                            API number (default: None)
      --profile {core,compatibility}
                            API profile (default: core)
      --validate            validate xml file (default: False)
      --translate-type      translate gl to c type (default: False)
      --build-wrapper       Build wrapper (default: False)
      --summary             summary (default: False)
      --list-enums          list enums (default: False)
      --list-commands       list commands (default: False)
      --list-multi-referenced-pointer-commands
                            list commands having size parameter used by more than
                            one pointer parameter (default: False)
      --list-computed-size-commands
                            list commands having a computed size parameter
                            (default: False)
      --list-multi-pointer-commands
                            list commands having a multi-pointer parameter
                            (default: False)
      --enum ENUM           Show enum property (default: None)
      --command COMMAND     Show command prototype (default: None)
      --man MAN             Show man page (default: None)

We will presents the main functions in the followings.

In any case, you have to select an API, its number and profile. As example we will use the OpenGL V3.3
core profile API.

You can print a summary on the API using::

    > query-opengl-api --api=gl --api-number=3.3 --profile=core --summary
    
    OpenGL API gl 3.3 profile: core
      - Number of Enums:      797
      - Number of Commands:   344

You can list all the enumerants using::
    
    > query-opengl-api --api=gl --api-number=3.3 --profile=core --list-enums

    Enum GL_ACTIVE_ATTRIBUTES = 0x8b89
    Enum GL_ACTIVE_ATTRIBUTE_MAX_LENGTH = 0x8b8a
    Enum GL_ACTIVE_TEXTURE = 0x84e0
    ...

You can list all the commands using::
    
    > query-opengl-api --api=gl --api-number=3.3 --profile=core --list-commands

    glActiveTexture
    glAttachShader
    glBeginConditionalRender
    ...

You can print the definition of an enumerant using::
    
    > query-opengl-api --api=gl --api-number=3.3 --profile=core --enum GL_ACTIVE_ATTRIBUTES

    Enum GL_ACTIVE_ATTRIBUTES = 0x8b89 (type: None, alias: None, api: None, comment: None)

You can print the definition of a command using::
    
    > query-opengl-api --api=gl --api-number=3.3 --profile=core --command glActiveTexture

    void glActiveTexture (GLenum texture)

And you can translate the GL type to C using::
    
    > query-opengl-api --api=gl --api-number=3.3 --profile=core --command glActiveTexture --translate-type

    void glActiveTexture (unsigned int texture)

To get the translation use::

    > query-opengl-api --api=gl --api-number=3.3 --profile=core --build-wrapper --command glDeleteBuffers

    glDeleteBuffers - delete named buffer objects
    
    glDeleteBuffers (InputArrayWrapper<const unsigned int * [n]> buffers)
    
    void glDeleteBuffers (GLsizei n, const GLuint * [n] buffers)

.. End
