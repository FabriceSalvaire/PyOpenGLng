=========================
How To Install PyOpenGLng
=========================

The PyOpenGLng project is hosted on `github <http://github.com/FabriceSalvaire/PyOpenGLng>`_.
 
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

Building & Installing
---------------------

Download and unpack the source, then run the following commands in a terminal::

  git clone git@github.com:FabriceSalvaire/PyOpenGLng.git pyopenglng
  cd pyopenglng
  python setup.py build
  python setup.py install

.. end
