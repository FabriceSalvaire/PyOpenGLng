=================
PyOpenGLng V0.1.0
=================

:Info: The home page of PyOpenGLng is located at http://fabricesalvaire.github.com/PyOpenGLng

PyOpenGLng, proudly blessed as is, is an experimental OpenGL wrapper for Python which generate the
requested OpenGL API from the `OpenGL XML Registry
<https://cvs.khronos.org/svn/repos/ogl/trunk/doc/registry/public/api>`_ and use an automatic
translator to map the C API to Python. Actually the wrapper use ctypes.

By design this wrapper supports all the OpenGL version, but it focus towards the programmable
pipeline and the most recent API. On Linux desktop Mesa release 10 supports OpenGL 3.3.

The Python package provides three components:

* an Oriented Object API to the OpenGL XML registry,
* a ctypes wrapper,
* and an experimental high level API.

Source Repository
-----------------

The PyOpenGLng project is hosted at github
http://github.com/FabriceSalvaire/PyOpenGLng
 
Requirements
------------

* Python 2.7
* Numpy
* PyQt 4.9 for the high level API and the examples

Testing
-------

To test PyOpenGLng, run the following commands in a terminal::

  git clone git@github.com:FabriceSalvaire/PyOpenGLng.git pyopenglng
  cd pyopenglng
  export PYTHONPATH=$PWD:$PYTHONPATH
  cd examples
  python test-high-level-api.py --opengl=v3 # designed to run on Mesa
  python test-high-level-api.py --opengl=v4 # require a proprietary driver

The command :command:`query-opengl-api` in :file:`bin` directory is a tool to query the OpenGL API.

..
   Building & Installing
   ---------------------

   Download and unpack the source, then run the following commands in a terminal::

     python setup.py build
     python setup.py install

.. End
