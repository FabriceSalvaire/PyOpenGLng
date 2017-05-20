####################################################################################################
#
# PyOpenGLng - An OpenGL Python Wrapper with a High Level API.
# Copyright (C) 2014 Fabrice Salvaire
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
####################################################################################################

####################################################################################################

import logging

import numpy as np # for Vector dtype

try:
    from PyQt5 import QtCore
    from PyQt5.QtWidgets import QMessageBox
    IS_PyQt5 = True
    IS_QOpenGLWidget = True
    if IS_QOpenGLWidget:
        from PyQt5.QtWidgets import QOpenGLWidget
    else:
        from PyQt5.QtOpenGL import QGLWidget as QOpenGLWidget
        from PyQt5.QtOpenGL import QGLContext, QGLFormat
except ImportError:
    from PyQt4 import QtCore
    from PyQt4.QtGui import QMessageBox
    from PyQt4.QtOpenGL import QGLWidget as QOpenGLWidget
    IS_PyQt5 = False
    IS_QOpenGLWidget = False

####################################################################################################

from . import GL
from ..Math.Geometry import Vector
from ..Math.Interval import IntervalInt2D
from .GlFeatures import GlVersion, GlFeatures
from .Ortho2D import Ortho2D, XAXIS, YAXIS, XYAXIS, ZoomManagerAbc

####################################################################################################

def opengl_context(function):

    """ Decorator that makes an OpenGL widget the current widget for OpenGL operations """

    def wrapper(widget, *args, **kwargs):

        """ Argument widget must be a :class:`QOpenGLWidget` instance. """

        widget.makeCurrent()
        function(widget, *args, **kwargs)
        widget.doneCurrent()

    return wrapper

####################################################################################################

class GlWidgetBase(QOpenGLWidget):

    _logger = logging.getLogger(__name__)

    ##############################################

    def __init__(self, parent):

        self._logger.debug('Initialise GlWidgetBase')

        super(GlWidgetBase, self).__init__(parent)

        if not IS_QOpenGLWidget:
            if not self.format().directRendering():
                QMessageBox.critical(None,
                                     'Error',
                                     "The Image Viewer requires an OpenGL direct rendering")
                raise NameError('Indirect Rendering')

        self.glortho2d = None

        self._clear_colour = (1, 1, 1, 1)
        self._clear_bit = GL.GL_COLOR_BUFFER_BIT

        self.x_step = 10
        self.y_step = 10
        self.zoom_step = 2. # must be float

        # self.setAutoFillBackground(False)
        # self.setAutoBufferSwap(False)

    ##############################################

    @property
    def clear_colour(self):
        return self._clear_colour

    @clear_colour.setter
    def clear_colour(self, value):
        self._clear_colour = tuple(value[:4])

    @property
    def clear_bit(self):
        return self._clear_bit

    @clear_bit.setter
    def clear_bit(self, value):
        self._clear_bit = value

    ##############################################

    def initializeGL(self):

        """ Initialise any required resources

        It is called just once before paintGL.
        """

        self._logger.debug('Initialise GL - Super')

        # if IS_PyQt5:
            # self.initializeOpenGLFunctions()
            # surface_format = Qt.QSurfaceFormat()
            # surface_format.setVersion(4, 0)
            # surface_format.setProfile(Qt.QSurfaceFormat.CoreProfile)
            # surface_format.setSwapBehavior(Qt.QSurfaceFormat.DoubleBuffer)
            # surface_format.setDepthBufferSize(32)
            # self.setFormat(surface_format)
            # surface_format = self.format()
            # print(surface_format.version())
            # print(surface_format.profile())
        
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
        print(('Resize viewport to (%u, %u)' % (width, height)))

        if not width or not height:
            raise NameError("Bad widget size")

        # viewport corresponds to the window lower left corner x, y and viewport width, height
        GL.glViewport(0, 0, width, height)

        if self.glortho2d is not None:
            self._logger.debug('  resize glortho2d')
            self.glortho2d.resize()
        else:
            self.init_glortho2d()

        self.update()

    ##############################################

    def init_glortho2d(self, max_area=None, zoom_manager=None, reverse_y_axis=False):

        self._logger.debug('Initialise Ortho2D - Super')

        if max_area is None:
            area_size = 10**3
            max_area = IntervalInt2D([-area_size, area_size], [-area_size, area_size])
            self._logger.debug('  use default max area ' + str(max_area))

        if zoom_manager is None:
            self._logger.debug('  use default ZoomManagerAbc')
            zoom_manager = ZoomManagerAbc()

        self.glortho2d = Ortho2D(max_area, zoom_manager, self, reverse_y_axis)

    ##############################################

    def size(self):

        # reimplement method to return np.array instead of PyQt4.QtCore.QSize(width, height)

        return Vector(self.width(), self.height(), dtype=np.uint)

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

        GL.glClearColor(*self._clear_colour)
        GL.glClear(self._clear_bit)

        # GL.glClearStencil(0)
        # GL.glStencilMask(~0)
        # GL.glClear(.... | GL.GL_STENCIL_BUFFER_BIT)
        
        self.paint()

    ##############################################

    def update(self):

        self._logger.debug('')

        # if IS_QOpenGLWidget:
        self.makeCurrent()
        self.update_model_view_projection_matrix()
        if IS_QOpenGLWidget:
            QOpenGLWidget.update(self)
        else:
            self.updateGL()

    ##############################################

    def window_to_gl_coordinate(self, event, round_to_integer=False):

        """ Convert mouse coordinate
        """

        position = Vector(event.x(), event.y())

        return self.glortho2d.window_to_gl_coordinate(position, round_to_integer)

    ##############################################

    def display_all(self):

        # Fixme: commented ?
        # self.glortho2d.zoom_bounding_box()
        self.update()

    ##############################################

    def zoom_one(self):

        self.glortho2d.zoom_at_center(1.)
        self.update()

    ##############################################

    def zoom_at_with_scale(self, x, y, zoom_factor):

        location = Vector(x, y)
        self.glortho2d.zoom_at_with_scale(location, zoom_factor)
        self.update()

    ##############################################

    def zoom_at(self, x, y):

        location = Vector(x, y)
        self.glortho2d.zoom_at(location)
        self.update()

    ##############################################

    def zoom_interval(self, interval):

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

    def translate_xy(self, dxy):

        self.glortho2d.translate(dxy, XYAXIS)
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

        if IS_PyQt5:
            delta = event.angleDelta().y()
        else:
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
