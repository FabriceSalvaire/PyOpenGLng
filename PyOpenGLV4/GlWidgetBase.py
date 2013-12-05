####################################################################################################
#
# PyOpenGLV4 - An OpenGL V4 layer on top of PyOpengl.
# Copyright (C) 2013 Salvaire Fabrice
#
####################################################################################################

####################################################################################################

import logging

import numpy as np

from PyQt4 import QtCore, QtOpenGL

####################################################################################################

import OpenGL

# If True, then wrap functions with logging operations which reports each call along with its
# arguments to the OpenGL.calltrace logger at the INFO level. This is *extremely* slow. You should
# *not* enable this in production code!
# OpenGL.FULL_LOGGING = True

# If set to a False value before importing any OpenGL.* libraries will completely disable
# error-checking. This can dramatically improve performance, but makes debugging far harder.
# OpenGL.ERROR_CHECKING = False

# If set to a True value before importing the numpy/lists support modules, will cause array
# operations to raise OpenGL.error.CopyError if the operation would cause a data-copy in order to
# make the passed data-type match the target data-type.
# OpenGL.ERROR_ON_COPY = True

# Only include OpenGL 3.1 compatible entry points. Note that this will generally break most PyOpenGL
# code that hasn't been explicitly made "legacy free" via a significant rewrite.
# OpenGL.FORWARD_COMPATIBLE_ONLY # True

# if True, attempt to use the OpenGL_accelerate package to provide Cython-coded accelerators for
# core wrapping operations.
# default = True
# OpenGL.USE_ACCELERATE = False

import OpenGL.GL as GL

####################################################################################################

from .Ortho2D import Ortho2D, XAXIS, YAXIS, ZoomManagerAbc
from .GlFeatures import GlVersion, GlFeatures
from .Tools.Interval import IntervalInt2D

####################################################################################################

class GlWidgetBase(QtOpenGL.QGLWidget):

    _logger = logging.getLogger(__name__)

    ##############################################

    def __init__(self, parent):

        self._logger.debug('Initialise GlWidgetBase')

        super(GlWidgetBase, self).__init__(parent)

        if not self.format().directRendering():
            QtGui.QMessageBox.critical(None,
                                       'Error',
                                       "The Image Viewer requires an OpenGL direct rendering")
            raise NameError('Indirect Rendering')

        self.glortho2d = None

        self.x_step = 10
        self.y_step = 10
        self.zoom_step = 2. # must be float

        self.setAutoFillBackground(False)
        # self.setAutoBufferSwap(False)
 
    ##############################################

    def initializeGL(self):

        """ Initialise any required resources
        
        It is called just once before paintGL.
        """    

        self._logger.debug('Initialise GL - Super')
        
        self.gl_version = GlVersion()
        self.gl_features = GlFeatures()
        # print self.gl_version
        for extension in ('GL_EXT_texture_integer',
                          #'GL_NV_texture_shader',
                          ):
            if extension not in self.gl_features:
                raise NameError("Doesn't have GL extension %s" % (extension))

    ##############################################

    def resizeGL(self, width, height):

        """ Set up the projection and viewport
        
        Resize Event
        """

        self._logger.debug('Resize viewport to (%u, %u)' % (width, height))

        # viewport corresponds to the window lower left corner x, y and viewport width, height
        GL.glViewport(0, 0, width, height)

        if self.glortho2d is not None:
            self._logger.debug('  resize glortho2d')
            self.glortho2d.resize()
        else:
            self.init_glortho2d()

        self.update()

    ##############################################

    def init_glortho2d(self, max_area=None, zoom_manager=None):

        self._logger.debug('Initialise Ortho2D - Super')

        if max_area is None:
            area_size = 10**3
            max_area = IntervalInt2D([-area_size, area_size], [-area_size, area_size])
            self._logger.debug('  use default max area ' + str(max_area))

        if zoom_manager is None:
            self._logger.debug('  use default ZoomManagerAbc')
            zoom_manager = ZoomManagerAbc()

        self.glortho2d = Ortho2D(max_area, zoom_manager, self)

    ##############################################

    def size(self):

        # reimplement method to return np.array instead of PyQt4.QtCore.QSize(width, height)

        return np.array((self.width(), self.height()), dtype=np.uint)

    ##############################################
    #
    # updateGL [virtual slot] : Updates the widget by calling glDraw()
    #

    ##############################################
    #
    # glDraw [virtual protected]
    #
    # Executes the virtual function paintGL().
    #
    # The widget's rendering context will become the current context and initializeGL() will be called if
    # it hasn't already been called.
    #
        
    ##############################################

    def paintGL(self):

        """ Perform the OpenGL calls needed to render the scene.
        """

        self._logger.debug('Paint OpenGL Scene')

        GL.glClearStencil(0)
        GL.glClearColor(0,0,0,0)
        # GL.glClear(GL.GL_COLOR_BUFFER_BIT)
        GL.glStencilMask(~0)
        GL.glClear(GL.GL_COLOR_BUFFER_BIT | GL.GL_STENCIL_BUFFER_BIT)
        
        self.paint()
        
    ##############################################

    def update(self):

        self._logger.debug('')

        self.update_model_view_projection_matrix()
        self.updateGL()

    ##############################################

    def window_to_gl_coordinate(self, event):

        """ Convert mouse coordinate
        """

        position = np.array((event.x(), event.y()), dtype=np.uint)

        return self.glortho2d.window_to_gl_coordinate(position)

    ##############################################

    def display_all(self):

        # self.glortho2d.zoom_bounding_box()
        self.update()

    ##############################################

    def zoom_one(self):

        self.glortho2d.zoom_at_center(1.)
        self.update()

    ##############################################
    
    def zoom_at_with_scale(self, x, y, zoom_factor):

        location = np.array((x, y), dtype=np.float)
        self.glortho2d.zoom_at_with_scale(location, zoom_factor)
        self.update()
        
    ##############################################
    
    def zoom_at(self, x, y):

        location = np.array((x, y), dtype=np.float)
        self.glortho2d.zoom_at(location)
        self.update()

    ##############################################
    
    def zoom_interval(self, interval):

        self.viewport_history.push_viewport_state('zoom bounding box')
        self.glortho2d.zoom_interval(interval)
        self.update()

    ##############################################

    def translate_x(self, dx):

        self.glortho2d.translate(dx, XAXIS)
        self.update()

    ##############################################

    def translate_y(self, dy):

        self.glortho2d.translate(dy, YAXIS)
        self.update()

    ##############################################

    def keyPressEvent(self, event):

        self._logger.debug('Key press event ' + str(event.key()))

        key = event.key()
        if   key == QtCore.Qt.Key_Left:
            self.translate_x(-self.x_step)

        elif key == QtCore.Qt.Key_Right:
            self.translate_x( self.x_step)

        elif key == QtCore.Qt.Key_Down:
            self.translate_y(-self.y_step)

        elif key == QtCore.Qt.Key_Up:
            self.translate_y( self.y_step)

        elif key == QtCore.Qt.Key_R:
            self.display_all()

        elif key == QtCore.Qt.Key_1:
            self.zoom_one()

        elif key == QtCore.Qt.Key_Plus:
            zoom_factor = self.glortho2d.zoom_manager.zoom_factor * self.zoom_step
            # print "Key + zoom %.3f -> %.3f" % (self.glortho2d.zoom_manager.zoom_factor, zoom_factor)
            self.glortho2d.zoom_at_center(zoom_factor)
            self.update()

        elif key == QtCore.Qt.Key_Minus:
            zoom_factor = self.glortho2d.zoom_manager.zoom_factor / self.zoom_step
            # print "Key - zoom %.3f -> %.3f" % (self.glortho2d.zoom_manager.zoom_factor, zoom_factor)
            self.glortho2d.zoom_at_center(zoom_factor)
            self.update()

        elif key == QtCore.Qt.Key_K:
            self.delete_objects()

        elif key == QtCore.Qt.Key_S:
            self.set_objects()

        else:
            self.parent().keyPressEvent(event)

    ##############################################

    def mousePressEvent(self, event):

        if event.buttons() & QtCore.Qt.LeftButton:
            args = (event.x(), event.y()) + tuple(self.window_to_gl_coordinate(event))
            self._logger.debug('Mouse press event %u, %u px %.1f, %.1f gl' % args)
        else:
            self.parent().mousePressEvent(event)

    ##############################################

    def wheel_zoom(self, event):

        self._logger.debug('Wheel Zoom')

        position = self.window_to_gl_coordinate(event)
        zoom_factor = self.glortho2d.zoom_manager.zoom_factor

        delta = int(event.delta())
        if delta == 120:
            zoom_factor *= self.zoom_step
        else:
            zoom_factor /= self.zoom_step

        self.glortho2d.zoom_at_with_scale(position, zoom_factor)
        self.update()

####################################################################################################
#
# End
#
####################################################################################################
