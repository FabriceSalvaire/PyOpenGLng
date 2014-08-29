.. -*- Mode: rst -*-

.. _examples-page:

.. include:: abbreviation.txt

==========
 Examples
==========

Some examples are provided with the PyOpenGLng source in the :file:`examples` directory, we will
presents them in the followings.

.. note:: PyOpenGLng was only tested on the Linux platform.

First of all, either you have to install PyOpenGLng (using virtualenv for example) or you must setup
your ``PYTHONPATH`` environment variable. For example enter these commands in a Linux terminal:

.. code-block:: sh

  cd pyopenglng
  export PYTHONPATH=$PWD:$PYTHONPATH

The script :file:`test-high-level-api.py` shows an usage of the high level API for both OpenGL
version 3 and 4. The first one is intended for platform running the |Mesa|_ which support the OpenGL
3.3 API on Intel HD GPU (since release 10.0 / november 2013). The second one is intended for
platform running a proprietary driver like the one provided by Nvidia which implements OpenGL up to
the version 4.4.

To run this example, enter the following commands in a Linux terminal::

  cd examples
  python test-high-level-api.py --opengl=v3 # designed to run on Mesa
  python test-high-level-api.py --opengl=v4 # require a proprietary driver

.. End
