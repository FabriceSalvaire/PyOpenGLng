#! /usr/bin/env python
# -*- python -*-

####################################################################################################
#
# PyOpenGLng - An OpenGL Python Wrapper with a High Level API.
# Copyright (C) 2013 Salvaire Fabrice
#
####################################################################################################

####################################################################################################

import argparse
import logging
import sys

from PyQt4 import QtCore, QtGui

####################################################################################################
#
# Options
#

argument_parser = argparse.ArgumentParser(
    description='PyOpenGLng example',
    formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

argument_parser.add_argument('--debug-level',
                             default='none',
                             choices=('none', 'warning', 'info', 'debug', 'opengl'),
                             help='logging level')

argument_parser.add_argument('--opengl',
                             default='v3',
                             choices=('v3', 'v4'),
                             help='OpenGL version')

args = argument_parser.parse_args()

####################################################################################################
#
# Logging
#

# Place here in order to enable logging

if args.debug_level == 'opengl':
    import OpenGL
    OpenGL.FULL_LOGGING = True
    level = logging.DEBUG
elif args.debug_level == 'debug':
    level = logging.DEBUG
elif args.debug_level == 'info':
    level=logging.INFO
elif args.debug_level == 'warning':
    level = logging.WARNING

if args.debug_level != 'none':
    logging.basicConfig(
        format='\033[1;32m%(asctime)s\033[0m - \033[1;34m%(name)s - %(module)s.%(funcName)s\033[0m - \033[1;31m%(levelname)s\033[0m - %(message)s',
        level=level,
        )

####################################################################################################

if args.opengl == 'v3':
    from GlWidgetV3 import GlWidget
elif args.opengl == 'v4':
    from GlWidgetV4 import GlWidget
else:
    raise ValueError('Unsupported OpenGL version')

####################################################################################################

class MainWindow(QtGui.QMainWindow):
    
    def __init__ (self):
        
        super(MainWindow, self).__init__()

        self.resize(1000, 800)

        self.central_widget = QtGui.QWidget(self)
        self.horizontal_layout = QtGui.QHBoxLayout(self.central_widget)

        self.graphics_view = GlWidget(self.central_widget)
        self.graphics_view.setFocusPolicy(QtCore.Qt.ClickFocus)

        self.horizontal_layout.addWidget(self.graphics_view)
        self.setCentralWidget(self.central_widget)

####################################################################################################

class Application(QtGui.QApplication):
    
    def __init__(self):
        
        super(Application, self).__init__(sys.argv)
        
        self.main_window = MainWindow()
        self.main_window.show()

####################################################################################################

if __name__ == "__main__":

    application = Application()
    application.exec_()

####################################################################################################
#
# End
#
####################################################################################################