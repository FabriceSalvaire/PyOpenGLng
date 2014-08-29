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

.. End

============
 PyOpenGLng
============

The official PyOpenGLng Home Page is located at |PyOpenGLngUrl|

The latest documentation build from the git repository is available at readthedocs.org |PyOpenGLng@readthedocs-badge|

Written by `Fabrice Salvaire <http://fabrice-salvaire.pagesperso-orange.fr>`_.

|Build Status|

-----

.. -*- Mode: rst -*-


==============
 Introduction
==============

PyOpenGLng, proudly blessed as is, is an experimental OpenGL wrapper for |Python| which generate the
requested OpenGL API from the `OpenGL XML Registry
<https://cvs.khronos.org/svn/repos/ogl/trunk/doc/registry/public/api>`_ and use an automatic
translator to map the C API to Python. Actually the wrapper use ctypes.

By design this wrapper supports all the OpenGL version, but it focus towards the programmable
pipeline and the most recent API. On Linux desktop Mesa release 10 supports OpenGL 3.3.

The Python package provides three components:

* an Oriented Object API to the OpenGL XML registry,
* a ctypes wrapper,
* and an experimental high level API.

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

Testing
-------

To test PyOpenGLng, run the following commands in a terminal::

  cd pyopenglng
  export PYTHONPATH=$PWD:$PYTHONPATH
  cd examples
  python test-high-level-api.py --opengl=v3 # designed to run on Mesa
  python test-high-level-api.py --opengl=v4 # require a proprietary driver

..
  How To Install PyOpenGLng
  The PyOpenGLng project is hosted on `github <http://github.com/FabriceSalvaire/PyOpenGLng>`_.
  Requirements
  Building & Installing
  Download and unpack the source, then run the following commands in a terminal::

.. End

.. End
