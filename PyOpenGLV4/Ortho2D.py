###################################################################################################
#
# PyOpenGLV4 - An OpenGL V4 layer on top of PyOpengl.
# Copyright (C) 2013 Salvaire Fabrice
#
####################################################################################################

####################################################################################################
#
#                                              Audit
#
# - 00/00/2013 Fabrice
#   - use Vector2D & Point2D ?
#   - middle -> center ?
#
####################################################################################################

####################################################################################################
#
# Signaling:
#
# - propagate states using return
# - use global states and users are responsible to check them
# - use a signal API
#
####################################################################################################

""" This module implements an Orthonormal 2D Viewport. """

####################################################################################################

from __future__ import division

import logging

import numpy as np

####################################################################################################

from .Tools.Interval import Interval, Interval2D

####################################################################################################

XAXIS, YAXIS = range(2)

####################################################################################################

def interval2d_from_center_and_size(center, size):

    """ Return an :class:`GVLab.Tools.Interval.Interval2D` instance.  The parameter *center* is a
    2-tuple that defines the center of the interval and the parameter *size* the 2-tuple (width,
    height).
    """

    point_inf = center - size * .5
    point_sup = point_inf + size

    return Interval2D((point_inf[0], point_sup[0]),
                      (point_inf[1], point_sup[1]))

####################################################################################################

class ViewportArea(object):

    """ This class defines a viewport area.
 
    It implements an interval arithmetic using the class :class:`GVLab.Tools.Interval.Interval2D`.
    """

    _logger = logging.getLogger(__name__)

    ##############################################
    
    def __init__(self, max_area):

        """ The parameter *max_area* must be an :class:`GVLab.Tools.Interval.Interval2D` instance
        that defines the maximum area allowed for the viewport.
        """

        self._max_area = max_area.copy()
        self._area = max_area.copy()

        self._set_reference_point()

    ##############################################
    
    def __str__(self):

        return str(self._area)

    ##############################################

    # Fixme: mutable argument, return ?

    def _check_axis_interval(self, axis_interval, axis):

        """ Check the axis interval and return a new one that is included in the max area. """

        # Fixme: don't report all error checks

        max_axis_interval = self._max_area[axis]

        inferior = axis_interval.inf < max_axis_interval.inf
        superior = max_axis_interval.sup < axis_interval.sup

        if inferior and superior:
            # Report error via exception
            raise ValueError('out of axis area')
        elif inferior:
            # Fix interval but don't report
            return Interval(max_axis_interval.inf,
                            max_axis_interval.inf + axis_interval.length())
        elif superior:
            # Fix interval but don't report
            return Interval(max_axis_interval.sup - axis_interval.length(),
                            max_axis_interval.sup)
        else:
            return Interval(axis_interval) # Fixme: copy ?

    ##############################################

    def _check_area(self, area):

        """ Check the interval *area* is included in the the max area. """

        return area.is_included_in(self._max_area)

    ##############################################
    
    def _set_reference_point(self):

        """ Set the reference point of the viewport defined as the left-bottom corner. """

        self.ref_point = np.array([self._area.x.inf,
                                   self._area.y.sup],
                                  dtype=np.float)

    ##############################################

    def center(self):

        """ Return the viewport center as an Numpy array. """

        return np.array(self._area.middle(), dtype=np.float)

    ##############################################

    def size(self, dtype=np.uint):

        """ Return the viewport size as an Numpy array. """

        return np.array(self._area.size(), dtype=dtype)

    ##############################################

    @property
    def area(self):
        return self._area

    ##############################################

    @area.setter
    def area(self, area):

        """ Set the area. """

        # Fixme: compution intersection and return True/False if changed

        string_format = """set_area:
   %s
  ->
   %s
 / %s"""
        self._logger.debug(string_format % (self._area, area, self._max_area))

        if self._check_area(area):
            self._area = area.copy() # Fixme: better coding ?
            self._set_reference_point()
        else:
            intersection = area & self._max_area
            if not intersection.is_empty():
                for axis in XAXIS, YAXIS:
                    self._area[axis] = self._check_axis_interval(area[axis], axis)
                self._set_reference_point()
            else:
                # Report error via exception
                raise ValueError('Out of area')

    ##############################################

    @property
    def max_area(self):
        return self._max_area

    ##############################################
    
    def translate(self, dx, axis):

        """ Translate the viewport of *dx* in the *axis* direction. """

        # Fixme: don't report all error checks

        old_axis_interval = self._area[axis]

        axis_interval = self._area[axis]
        axis_interval += dx
        self._area[axis] = self._check_axis_interval(axis_interval, axis)
        
        string_format = """translate
   %s
  ->
   (%s)
  ->
   %s
 / %s""" 
        self._logger.debug(string_format % (old_axis_interval, axis_interval, self._area[axis], self._max_area[axis]))
        self._set_reference_point()

####################################################################################################

class ZoomManagerAbc(object):

    """ This class implements a basic zoom manager. """

    _logger = logging.getLogger(__name__)

    ##############################################
    
    def __init__(self):

        """ The initial zoom factor is set to one. """

        self.zoom_factor = 1

    ##############################################
    
    def check_zoom(self, zoom_factor):

        """ Basic implementation to check a zoom factor, return the 2-tuple (True, zoom_factor). """

        self.zoom_factor = zoom_factor

        return True, zoom_factor

####################################################################################################

class Ortho2D(object):

    """ This class implements an Orthonormal 2D Viewport.
    """

    _logger = logging.getLogger(__name__)

    gl_to_window_parity = np.array([ 1, -1], dtype=np.float)

    ##############################################
    
    def __init__(self, max_area, zoom_manager, window):

        """ The parameter *max_area* must be an :class:`GVLab.Tools.Interval.Interval2D` instance
        that defines the maximum area allowed for the viewport.

        The parameter *zoom_manager* must be an :class:`ZoomManager` instance.

        The parameter *window* must implement a Window Trait, that defines a method :meth:`size`
        returning the 2-tuple (width, height).
        """

        self.viewport_area = ViewportArea(max_area)
        self.zoom_manager = zoom_manager
        self.window = window

        self.zoom_at_with_scale(max_area.middle(), zoom_factor=1)

    ##############################################

    def __str__(self):

        string_format = """Ortho2D:
 - max area: %s
 - area: %s
 - window: %s
 - zoom factor: %g
 - matrix:
%s
"""

        text = string_format % (self.viewport_area._max_area,
                                self.viewport_area,
                                self.window.size(),
                                self.zoom_manager.zoom_factor,
                                self.view_matrix(),
                                )
        return text

    ##############################################

    def _compute_display_scale(self):

        """ Compute the display scale. """

        self.display_scale = self.viewport_area.size(dtype=np.float) / self.window.size()
        self.parity_display_scale = self.display_scale * self.gl_to_window_parity
        self.inverse_parity_display_scale = 1 / self.parity_display_scale

    ##############################################

    def window_to_gl_coordinate(self, window_point):

        """ Return the scene coordinate from the window coordinate.  The parameter *window_point*
        must be an Numpy array.
        """

        return self.viewport_area.ref_point + self.parity_display_scale * window_point

   ###############################################

    def gl_to_window_coordinate(self, gl_point):

        """ Return the window coordinate from the scene coordinate.  The parameter *gl_point*
        must be an Numpy array.
        """

        window_point = (gl_point - self.viewport_area.ref_point) * self.inverse_parity_display_scale

        return np.rint(window_point)

   ###############################################

    def window_to_gl_distance(self, x_window):

        return self.parity_display_scale[0] * x_window

    ##############################################
    
    def translate(self, dx, axis):

        """ Translate the viewport of *dx* in the *axis* direction. """        

        self.viewport_area.translate(dx, axis)

    ##############################################

    def _compute_zoom_to_fit_axis(self, length, axis):

        """ Compute the zoom to fit an axis size. """

        self._logger.debug("compute_zoom_to_fit_axis %u %u" % (length, axis))

        # Fixme: window.size[axis] ?

        return self.window.size()[axis] / length

    ##############################################

    def _compute_zoom_to_fit_interval(self, interval):
       
        """ Compute the zoom to fit an interval.  The parameter *interval* must be an
        :class:`GVLab.Tools.Interval.Interval2D` instance.
        """

        axis_scale = self.window.size() / np.array(interval.size(), dtype=np.float)
        axis = axis_scale.argmin()
        zoom_factor = axis_scale[axis]

        return axis, zoom_factor

    ##############################################

    def zoom_at_with_scale(self, point, zoom_factor):

        """ Zoom the viewport centered on a point.  The parameter *point* must be an Numpy array.
        """

        self._logger.debug('zoom_at_with_scale %s %g' % (str(point), zoom_factor))

        # zoom_changed unused
        zoom_changed, zoom_factor = self.zoom_manager.check_zoom(zoom_factor)
        self._logger.debug("Check Zoom: changed %s, zoom %6.1f" % (zoom_changed, zoom_factor))

        new_area_size = self.window.size() / zoom_factor
        new_area = interval2d_from_center_and_size(point, new_area_size)
        self.viewport_area.area = new_area
        self._compute_display_scale()

    ##############################################
    
    def zoom_at(self, center):

        """ Zoom the viewport centered on the point *center*.  The parameter *center* must be an
        Numpy array.
        """

        self.zoom_at_with_scale(center, self.zoom_manager.zoom_factor)

    ##############################################
    
    def zoom_at_center(self, zoom_factor):
        
        """ Zoom on the viewport center. """

        self.zoom_at_with_scale(self.viewport_area.center(), zoom_factor)

    ##############################################

    def zoom_interval(self, interval):

        """ Zoom to an interval.  The parameter *interval* must be an
        :class:`GVLab.Tools.Interval.Interval2D` instance.
        """

        # Fixme: name ?

        # axis unused
        axis, zoom_factor = self._compute_zoom_to_fit_interval(interval)
        self.zoom_at_with_scale(interval.middle(), zoom_factor)

    ##############################################

    def fit_axis(self, length, axis):

        """ Set the zoom so as to fit an axis size. """

        zoom_factor = self._compute_zoom_to_fit_axis(length, axis)
        self.zoom_at_center(zoom_factor)

    ##############################################

    def resize(self):

        """ Resize the viewport for the new window size. """

        self.zoom_at_center(self.zoom_manager.zoom_factor)

    ##############################################

    def viewport_scale(self, window_size):

        """ Return the viewport scale. """

        return self.viewport_area.size() / np.array(window_size, dtype='f')

    ##############################################

    def view_matrix(self):

        """ Return the view matrix. """

        offset = self.viewport_area.center() * -1.
        scale = 2. / self.viewport_area.size()
        offset *= scale

        matrix = np.array([[ scale[0], 0.,       0., offset[0] ],
                           [ 0.,       scale[1], 0., offset[1] ],
                           [ 0.,       0.,       1.,        0. ],
                           [ 0.,       0.,       0.,        1. ]],
                          dtype=np.float32)

        return matrix

    ##############################################

    def viewport_uniform_buffer_data(self, window_size):

        """ Return the viewport uniform buffer data. """

        matrix = self.view_matrix()
        viewport_scale = self.viewport_scale(window_size)

        viewport_array = np.array(list(matrix.transpose().flatten()) +
                                  list(viewport_scale) +
                                  list(1./viewport_scale),
                                  dtype=np.float32)

        return viewport_array

    ##############################################

    def ortho2d_bounding_box(self):

        area = self.viewport_area.area

        return (area.x.inf, area.x.sup, area.y.inf, area.y.sup)

    ##############################################

    def row_bounding_box(self):

        left, bottom, right, top = self.viewport_area.area.bounding_box()
        right = self.viewport_area.max_area.x.sup

        return (left, bottom, right, top)

    ##############################################

    def get_state(self):

        """ Get the viewport state. """

        return self.viewport_area.area

    ##############################################

    def set_state(self, state):

        """ Set the viewport state. """

        self.zoom_interval(state)

####################################################################################################
#
# End
#
####################################################################################################
