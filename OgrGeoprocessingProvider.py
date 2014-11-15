# -*- coding: latin-1 -*-

"""
***************************************************************************
    OgrGeoProcessingProvider.py
    ---------------------
    Date                 : July 2014
    Copyright            : (C) 2014 by Alexander Bruy
    Email                : alexander dot bruy at gmail dot com
***************************************************************************
*                                                                         *
*   This program is free software; you can redistribute it and/or modify  *
*   it under the terms of the GNU General Public License as published by  *
*   the Free Software Foundation; either version 2 of the License, or     *
*   (at your option) any later version.                                   *
*                                                                         *
***************************************************************************
"""

__author__ = 'Alexander Bruy'
__date__ = 'July 2014'
__copyright__ = '(C) 2014, Alexander Bruy'

# This will get replaced with a git SHA1 when you do a git archive

__revision__ = '$Format:%H$'

import os

from PyQt4.QtGui import *

from processing.core.AlgorithmProvider import AlgorithmProvider
from processing.core.ProcessingConfig import Setting, ProcessingConfig
from processing.tools import system

from processing_ogrgeoprocessing.ogr2ogrdissolve import ogr2ogrdissolve
from processing_ogrgeoprocessing.ogr2ogrbuffer import ogr2ogrbuffer
from processing_ogrgeoprocessing.ogr2ogrclip import ogr2ogrclip
from processing_ogrgeoprocessing.ogr2ogrclipextent import ogr2ogrclipextent
from processing_ogrgeoprocessing.ogr2ogrdistance import ogr2ogrdistance
from processing_ogrgeoprocessing.ogr2ogronesidebuffer import ogr2ogronesidebuffer
from processing_ogrgeoprocessing.ogr2ogrpol import ogr2ogrpol
from processing_ogrgeoprocessing.ogr2ogrtopostgis import ogr2ogrtopostgis
from processing_ogrgeoprocessing.ogr2ogrtopostgislist import ogr2ogrtopostgislist
from processing_ogrgeoprocessing.ogr2ogrclipbypolygon import ogr2ogrclipbypolygon
from processing_ogrgeoprocessing.ogr2ogrmakevalid import ogr2ogrmakevalid
from processing_ogrgeoprocessing.ogr2ogrdifference import ogr2ogrdifference

class OgrGeoprocessingProvider(AlgorithmProvider):

    def __init__(self):
        AlgorithmProvider.__init__(self)

        self.activate = False

        self.alglist = [ogr2ogrdissolve(),ogr2ogrbuffer(),ogr2ogrclip(),ogr2ogrdistance(),ogr2ogronesidebuffer(),ogr2ogrpol(),
			ogr2ogrtopostgis(),ogr2ogrtopostgislist(),ogr2ogrclipbypolygon(),ogr2ogrmakevalid(),ogr2ogrdifference()]
        for alg in self.alglist:
            alg.provider = self

    def initializeSettings(self):
        AlgorithmProvider.initializeSettings(self)

    def unload(self):
        AlgorithmProvider.unload(self)

    def getName(self):
        return 'OGR Geoprocessing tools'

    def getDescription(self):
        return 'OGR Geoprocessing tools'

    def getIcon(self):
        return QIcon(os.path.dirname(__file__) + '/icons/faunalia.png')

    def _loadAlgorithms(self):
        self.algs = self.alglist
