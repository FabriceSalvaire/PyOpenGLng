#! /usr/bin/env python
# -*- python -*-

####################################################################################################
#
# PyOpenGLV4 - An OpenGL V4 layer on top of PyOpengl..
# Copyright (C) 2013 Salvaire Fabrice
#
####################################################################################################

####################################################################################################
#
# Options
#

import argparse
argument_parser = argparse.ArgumentParser()

argument_parser.add_argument('--debug',
                             action="store_true",
                             help='Enable OpenGL logging')

args = argument_parser.parse_args()

####################################################################################################
#
# Logging
#

import logging

# Place here in order to enable logging
if args.debug:
    import OpenGL
    OpenGL.FULL_LOGGING = True

logging.basicConfig(
    format='\033[1;32m%(asctime)s\033[0m - \033[1;34m%(name)s - %(module)s.%(funcName)s\033[0m - \033[1;31m%(levelname)s\033[0m - %(message)s',
    #level=logging.DEBUG,
    level=logging.INFO,
    )

####################################################################################################

import sys

from PyQt4 import QtCore, QtGui

####################################################################################################

from GlWidget import GlWidget

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
