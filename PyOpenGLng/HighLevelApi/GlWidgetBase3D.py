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

import numpy as np

from PyQt4 import QtCore, QtOpenGL
from PyQt4.QtCore import Qt

####################################################################################################

from . import GL
from .GlFeatures import GlVersion, GlFeatures

####################################################################################################

class GlWidgetBase3D(QtOpenGL.QGLWidget):

    _logger = logging.getLogger(__name__)

    ##############################################

    def __init__(self, parent):

        self._logger.debug('Initialise GlWidgetBase')

        super(GlWidgetBase3D, self).__init__(parent)

        if not self.format().directRendering():
            QtGui.QMessageBox.critical(None,
                                       'Error',
                                       "The Image Viewer requires an OpenGL direct rendering")
            raise NameError('Indirect Rendering')

        self._old_position = None
        self.rotation_x = 0
        self.rotation_y = 0

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

        self.update()

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

        GL.glEnable(GL.GL_DEPTH_TEST)
        GL.glDepthFunc(GL.GL_LESS)
        GL.glClearColor(0,0,0,0)
        GL.glClear(GL.GL_COLOR_BUFFER_BIT | GL.GL_DEPTH_BUFFER_BIT)

        self.paint()
        
    ##############################################

    def update(self):

        self._logger.debug('')

        self.update_model_view_projection_matrix()
        self.updateGL()

    ##############################################

    # def mousePressEvent(self, event):

    #     self._logger.info("Mouse press event")
    #     if event.buttons() & Qt.LeftButton:
    #         self._logger.info("left button")
    #     else:
    #         self.parent().mousePressEvent(event)

    ##############################################

    def mouseMoveEvent(self, event):

        self._logger.info('')
        if event.buttons() & Qt.LeftButton:
            position = event.posF()
            if self._old_position is not None:
                delta = position - self._old_position
                px_to_degree = 1./1
                self.rotation_x += delta.y() * px_to_degree
                self.rotation_y += delta.x() * px_to_degree
                self.rotation_x = self.rotation_x % 360
                self.rotation_y = self.rotation_y % 360
                self.update()
            self._logger.info('Rotate scene {} {}'.format(self.rotation_x, self.rotation_y))
            self._old_position = position
        else:
            self.parent().mouseMoveEvent(event)

####################################################################################################
#
# End
#
####################################################################################################
