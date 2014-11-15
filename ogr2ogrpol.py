# -*- coding: utf-8 -*-

"""
***************************************************************************
    ogr2ogrpol.py
    ---------------------
    Date                 : November 2012
    Copyright            : (C) 2012 by Victor Olaya
    Email                : volayaf at gmail dot com
***************************************************************************
*                                                                         *
*   This program is free software; you can redistribute it and/or modify  *
*   it under the terms of the GNU General Public License as published by  *
*   the Free Software Foundation; either version 2 of the License, or     *
*   (at your option) any later version.                                   *
*                                                                         *
***************************************************************************
"""

__author__ = 'Victor Olaya'
__date__ = 'November 2012'
__copyright__ = '(C) 2012, Victor Olaya'

# This will get replaced with a git SHA1 when you do a git archive

__revision__ = '$Format:%H$'

import os

from PyQt4.QtCore import *
from PyQt4.QtGui import *

from qgis.core import *

from processing.core.parameters import ParameterVector
from processing.core.parameters import ParameterString
from processing.core.parameters import ParameterNumber
from processing.core.parameters import ParameterBoolean
from processing.core.outputs import OutputVector

from processing.tools.system import *
from processing.tools import dataobjects

from processing.algs.gdal.OgrAlgorithm import OgrAlgorithm
from processing.algs.gdal.GdalUtils import GdalUtils

class ogr2ogrpol(OgrAlgorithm):

    OUTPUT_LAYER = 'OUTPUT_LAYER'
    INPUT_LAYER = 'INPUT_LAYER'
    DISTANCE = 'DISTANCE'
    GEOMETRY = 'GEOMETRY'
    OPTIONS = 'OPTIONS'

    def getIcon(self):
        return  QIcon(os.path.dirname(__file__) + '/icons/sl.png')


    def defineCharacteristics(self):
        self.name = 'Create points on lines'
        self.group = '[OGR] Geoprocessing'

        self.addParameter(ParameterVector(self.INPUT_LAYER, 'Input layer',
                          [ParameterVector.VECTOR_TYPE_LINE], False))
        self.addParameter(ParameterString(self.GEOMETRY, 'Geometry column name ("geometry" for Shapefiles, may be different for other formats)',
                          'geometry', optional=False))
        self.addParameter(ParameterNumber(self.DISTANCE, 'Distance from line start represented as fraction of line length', 0, 1, 0.5))
        self.addParameter(ParameterString(self.OPTIONS, 'Additional creation options (see ogr2ogr manual)',
                          '', optional=True))
        self.addOutput(OutputVector(self.OUTPUT_LAYER, 'Output layer'))

    def processAlgorithm(self, progress):
        inLayer = self.getParameterValue(self.INPUT_LAYER)
        ogrLayer = self.ogrConnectionString(inLayer)
        layername = "'" + self.ogrLayerName(inLayer) + "'"
        distance = unicode(self.getParameterValue(self.DISTANCE))
        geometry = unicode(self.getParameterValue(self.GEOMETRY))
        
        output = self.getOutputFromName(self.OUTPUT_LAYER)
        outFile = output.value

        output = self.ogrConnectionString(outFile)
        options = unicode(self.getParameterValue(self.OPTIONS))

        arguments = []
        arguments.append(output)
        arguments.append(ogrLayer)

        arguments.append('-dialect sqlite -sql "SELECT ST_Line_Interpolate_Point(')
        arguments.append(geometry)
        arguments.append(',')
        arguments.append(distance)
        arguments.append('),*')
        arguments.append('FROM')
        arguments.append(layername)
        arguments.append('"')
        
        if len(options) > 0:
            arguments.append(options)
            
        commands = []
        if isWindows():
            commands = ['cmd.exe', '/C ', 'ogr2ogr.exe',
                        GdalUtils.escapeAndJoin(arguments)]
        else:
            commands = ['ogr2ogr', GdalUtils.escapeAndJoin(arguments)]

        GdalUtils.runGdal(commands, progress)