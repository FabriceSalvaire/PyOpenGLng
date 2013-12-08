####################################################################################################
#
# PyOpenGLng - An OpenGL Python Wrapper with a High Level API.
# Copyright (C) 2013 Salvaire Fabrice
#
####################################################################################################

####################################################################################################

import cPickle as pickle
import glob
import os

from lxml import etree

####################################################################################################

class Manual(dict):

    ##############################################

    @classmethod
    def load (cls):

        manuals = {}
        for pickle_file in glob.glob(os.path.join(os.path.dirname(__file__), 'man*.pickle')):
            with open(pickle_file, 'r') as f:
                manual = pickle.load(f)
                manuals[manual.name] = manual

        return manuals
    
    ##############################################

    def __init__(self, name):

        self.name = name

####################################################################################################

class Page(object):

    ##############################################

    def __init__(self, function, page_name, purpose):

        self.function = function
        self.page_name = page_name
        self.purpose = purpose

####################################################################################################

class ManualParser(object):

    ##############################################

    def __init__(self, manual_path):

        self.manual = Manual(os.path.basename(manual_path))
        self._parse_pages(manual_path)

    ##############################################

    def _parse_pages(self, manual_path):

        for page in glob.glob(os.path.join(manual_path, 'gl*.xml')):
            self._parse_page(page)

    ##############################################

    def _parse_page(self, page_path):

        page_name = os.path.basename(page_path)
        page_name = page_name.replace('.xml', '')

        with open(page_path, 'r') as f:
            xml_source = f.read()
            # MathML namespace is missing
            xml_source = xml_source.replace('<refentry ',
                                            '<refentry xmlns:mml="http://www.w3.org/1998/Math/MathML" ')
            # Undefinded entities
            for entity in ('it', 'lfloor', 'rfloor', 'plus', 'af', 'times', 'nbsp', 'ne', 'le',
                           'lceil', 'rceil', 'minus', 'infin', 'CenterDot', 'Delta', 'Hat', 'Sigma',
                           'PartialD', 'DoubleVerticalBar', 'Prime', 'LeftFloor', 'RightFloor',
                           'LeftCeiling', 'RightCeiling', 'VerticalBar'):
                xml_source = xml_source.replace('&' + entity + ';', '')

        root = etree.fromstring(xml_source)
        functions = [node.text for node in root.findall('refnamediv/refname')]
        purpose = root.find('refnamediv/refpurpose').text
        for function in functions:
            self.manual[function] = Page(function, page_name, purpose)

####################################################################################################
# 
# End
# 
####################################################################################################
