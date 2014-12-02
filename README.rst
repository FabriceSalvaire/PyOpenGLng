.. -*- Mode: rst -*-

.. -*- Mode: rst -*-

.. |ohloh| image:: https://www.openhub.net/accounts/230426/widgets/account_tiny.gif
   :target: https://www.openhub.net/accounts/fabricesalvaire
   :alt: Fabrice Salvaire's Ohloh profile
   :height: 15px
   :width:  80px

.. |PyOpenGLngUrl| replace:: http://fabricesalvaire.github.io/PyOpenGLng

.. |PyOpenGLngHomePage| replace:: PyOpenGLng Home Page
.. _PyOpenGLngHomePage: http://fabricesalvaire.github.io/PyOpenGLng

.. |PyOpenGLngDoc| replace:: PyOpenGLng Documentation
.. _PyOpenGLngDoc: http://pyopenglng.readthedocs.org/en/latest

.. |PyOpenGLng@readthedocs-badge| image:: https://readthedocs.org/projects/pyopenglng/badge/?version=latest
   :target: http://pyopenglng.readthedocs.org/en/latest

.. |PyOpenGLng@github| replace:: https://github.com/FabriceSalvaire/PyOpenGLng
.. .. _PyOpenGLng@github: https://github.com/FabriceSalvaire/PyOpenGLng

.. |PyOpenGLng@readthedocs| replace:: http://pyopenglng.readthedocs.org
.. .. _PyOpenGLng@readthedocs: http://pyopenglng.readthedocs.org

.. |PyOpenGLng@pypi| replace:: https://pypi.python.org/pypi/PyOpenGLng
.. .. _PyOpenGLng@pypi: https://pypi.python.org/pypi/PyOpenGLng

.. |Build Status| image:: https://travis-ci.org/FabriceSalvaire/PyOpenGLng.svg?branch=master
   :target: https://travis-ci.org/FabriceSalvaire/PyOpenGLng
   :alt: PyOpenGLng build status @travis-ci.org

.. End
.. -*- Mode: rst -*-

.. |Python| replace:: Python
.. _Python: http://python.org

.. |PyPI| replace:: PyPI
.. _PyPI: https://pypi.python.org/pypi

.. |Numpy| replace:: Numpy
.. _Numpy: http://www.numpy.org

.. |Sphinx| replace:: Sphinx
.. _Sphinx: http://sphinx-doc.org

.. |Mesa| replace:: Mesa 3D Graphics Library
.. _Mesa: http://www.mesa3d.org

.. |ctypes| replace:: ctypes
.. _ctypes: http://docs.python.org/2/library/ctypes.html

.. |cffi| replace:: CFFI
.. _cffi: http://cffi.readthedocs.org

.. |OpenGL| replace:: OpenGL
.. _OpenGL: http://www.opengl.org

.. |OpenGL_registry| replace:: OpenGL XML API Registry
.. _OpenGL_registry: http://www.opengl.org/registry

.. |OpenGL_registry_cvs| replace:: Khronos OpenGL API CVS
.. _OpenGL_registry_cvs: https://cvs.khronos.org/svn/repos/ogl/trunk/doc/registry/public/api

.. |pypy| replace:: pypy
.. _pypy: http://pypy.org

.. End

============
 PyOpenGLng
============

The official PyOpenGLng Home Page is located at |PyOpenGLngUrl|

The latest documentation build from the git repository is available at readthedocs.org |PyOpenGLng@readthedocs-badge|

Written by `Fabrice Salvaire <http://www.fabrice-salvaire.fr>`_.

..
  |Build Status|

-----

.. -*- Mode: rst -*-


==============
 Introduction
==============

PyOpenGLng, proudly blessed as is, is an experimental |OpenGL|_ wrapper for |Python|_ which generates
the requested OpenGL API from the |OpenGL_Registry|_ and use an automatic translator to map the
C API to Python. The interface between C and Python is supported by |ctypes|_  and also by |CFFI|_
which paves the way to use the |pypy|_ interpreter.

By design this wrapper supports all the OpenGL version, but it focus towards the programmable
pipeline and the most recent OpenGL API. On Linux desktop, |Mesa|_ release 10 (November 2013)
supports the OpenGL 3.3 API for Intel HD GPU.

The Python package provides three components:

* an Oriented Object API to the OpenGL XML registry,
* a ctypes and CFFI wrapper,
* an experimental high level API.

.. warning:: We should test all the API to claim a compliance with the OpenGL API. Since the OpenGL
  API becomes more and more large and complex over the release, such attempt would require a huge
  amount of work. Up to now only a part of the API was tested successfully.

Bibliography
-------------

The followings list of links provides an overview on the topic:

* `PyOpenGL - the de facto standard OpenGL Python binding <http://pyopengl.sourceforge.net>`_
* `Vispy - a high-performance interactive 2D/3D data visualization library <http://vispy.org>`_

.. End

.. -*- Mode: rst -*-

.. _installation-page:


==============
 Installation
==============

Dependencies
------------

PyOpenGLng requires the following dependencies:

 * |Python|_ 2.7
 * |Numpy|_
 * freetype-py 
 * PyQt 4.9 for the high level API and the examples

Installation from PyPi Repository
---------------------------------

PyOpenGLng is made available on the |Pypi|_ repository at |PyOpenGLng@pypi|

Run this command to install the last release:

.. code-block:: sh

  pip install PyOpenGLng

Installation from Source
------------------------

The PyOpenGLng source code is hosted at |PyOpenGLng@github|

To clone the Git repository, run this command in a terminal:

.. code-block:: sh

  git clone git@github.com:FabriceSalvaire/PyOpenGLng.git

Then to build and install PyOpenGLng run these commands:

.. code-block:: sh

  python setup.py build
  python setup.py install

..
  How To Install PyOpenGLng
  The PyOpenGLng project is hosted on `github <http://github.com/FabriceSalvaire/PyOpenGLng>`_.
  Requirements
  Building & Installing
  Download and unpack the source, then run the following commands in a terminal::

.. End

.. End
