# -*- coding: utf-8 -*-

"""
***************************************************************************
    ogr2ogrbuffer.py
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
from processing.core.parameters import ParameterTableField
from processing.core.outputs import OutputVector

from processing.tools.system import *
from processing.tools import dataobjects

from processing.algs.gdal.OgrAlgorithm import OgrAlgorithm
from processing.algs.gdal.GdalUtils import GdalUtils

class ogr2ogrbuffer(OgrAlgorithm):

    OUTPUT_LAYER = 'OUTPUT_LAYER'
    INPUT_LAYER = 'INPUT_LAYER'
    GEOMETRY = 'GEOMETRY'
    DISTANCE = 'DISTANCE'   
    DISSOLVEALL = 'DISSOLVEALL'
    FIELD = 'FIELD'
    MULTI = 'MULTI' 
    OPTIONS = 'OPTIONS'

    def getIcon(self):
        return  QIcon(os.path.dirname(__file__) + '/icons/sl.png')

    def defineCharacteristics(self):
        self.name = 'Buffer vectors'
        self.group = '[OGR] Geoprocessing'

        self.addParameter(ParameterVector(self.INPUT_LAYER, 'Input layer',
                          [ParameterVector.VECTOR_TYPE_ANY], False))
        self.addParameter(ParameterString(self.GEOMETRY, 'Geometry column name ("geometry" for Shapefiles, may be different for other formats)',
                          'geometry', optional=False))
        self.addParameter(ParameterString(self.DISTANCE,'Buffer distance', '1000', optional=False))
        self.addParameter(ParameterBoolean(self.DISSOLVEALL,
                          'Dissolve all results?', False))
        self.addParameter(ParameterTableField(self.FIELD, 'Dissolve by attribute',
                          self.INPUT_LAYER, optional=True))
        self.addParameter(ParameterBoolean(self.MULTI,
                          'Output as singlepart geometries (only used when dissolving by attribute)?', False))
        self.addParameter(ParameterString(self.OPTIONS, 'Additional creation options (see ogr2ogr manual)',
                          '', optional=True))
        self.addOutput(OutputVector(self.OUTPUT_LAYER, 'Output layer'))



    def processAlgorithm(self, progress):
        inLayer = self.getParameterValue(self.INPUT_LAYER)
        ogrLayer = self.ogrConnectionString(inLayer)
        layername = "'" + self.ogrLayerName(inLayer) + "'"
        geometry = unicode(self.getParameterValue(self.GEOMETRY))
        distance = unicode(self.getParameterValue(self.DISTANCE))
        dissolveall = self.getParameterValue(self.DISSOLVEALL)
        field = unicode(self.getParameterValue(self.FIELD)) 
        multi = self.getParameterValue(self.MULTI)
        
        output = self.getOutputFromName(self.OUTPUT_LAYER)
        outFile = output.value

        output = self.ogrConnectionString(outFile)
        options = unicode(self.getParameterValue(self.OPTIONS))

        arguments = []
        arguments.append(output)
        arguments.append(ogrLayer)
        if dissolveall or field != 'None':
           arguments.append('-dialect sqlite -sql "SELECT ST_Union(ST_Buffer(')
        else:
           arguments.append('-dialect sqlite -sql "SELECT ST_Buffer(')           
        arguments.append(geometry)
        arguments.append(',')
        arguments.append(distance)
        if dissolveall or field != 'None':
           arguments.append(')),*')  
        else:
           arguments.append('),*')  
        arguments.append('FROM')
        arguments.append(layername)
        if field != 'None':
           arguments.append('GROUP')
           arguments.append('BY')         
           arguments.append(field) 
        arguments.append('"')   
        if field != 'None' and multi:
           arguments.append('-explodecollections')

        if len(options) > 0:
            arguments.append(options)
            
        commands = []
        if isWindows():
            commands = ['cmd.exe', '/C ', 'ogr2ogr.exe',
                        GdalUtils.escapeAndJoin(arguments)]
        else:
            commands = ['ogr2ogr', GdalUtils.escapeAndJoin(arguments)]

        GdalUtils.runGdal(commands, progress)