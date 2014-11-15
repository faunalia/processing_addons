# -*- coding: utf-8 -*-

"""
***************************************************************************
    ogr2ogrdissolve.py
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

class ogr2ogrdissolve(OgrAlgorithm):

    OUTPUT_LAYER = 'OUTPUT_LAYER'
    INPUT_LAYER = 'INPUT_LAYER'
    GEOMETRY = 'GEOMETRY'
    FIELD = 'FIELD'    
    MULTI = 'MULTI' 
    COUNT = 'COUNT' 
    STATS = 'STATS' 
    STATSATT = 'STATSATT' 
    AREA = 'AREA'
    FIELDS = 'FIELDS'
    OPTIONS = 'OPTIONS'

    def getIcon(self):
        return  QIcon(os.path.dirname(__file__) + '/icons/sl.png')


    def defineCharacteristics(self):
        self.name = 'Dissolve polygons'
        self.group = '[OGR] Geoprocessing'

        self.addParameter(ParameterVector(self.INPUT_LAYER, 'Input layer',
                          [ParameterVector.VECTOR_TYPE_POLYGON], False))
        self.addParameter(ParameterString(self.GEOMETRY, 'Geometry column name ("geometry" for Shapefiles, may be different for other formats)',
                          'geometry', optional=False))
        self.addParameter(ParameterTableField(self.FIELD, 'Dissolve field',
                          self.INPUT_LAYER))
        self.addParameter(ParameterBoolean(self.MULTI,
                          'Output as multipart geometries?', True))
        self.addParameter(ParameterBoolean(self.FIELDS,
                          'Keep input attributes?', False)) 
        self.addParameter(ParameterBoolean(self.COUNT,
                          'Count dissolved features?', False))        
        self.addParameter(ParameterBoolean(self.AREA,
                          'Compute area and perimeter of dissolved features?', False))  
        self.addParameter(ParameterBoolean(self.STATS,
                          'Compute min/max/sum/mean for the following numeric attribute?', False)) 
        self.addParameter(ParameterTableField(self.STATSATT, 'Numeric attribute to compute dissolved features stats',
                          self.INPUT_LAYER))
        self.addParameter(ParameterString(self.OPTIONS, 'Additional creation options (see ogr2ogr manual)',
                          '', optional=True))
        self.addOutput(OutputVector(self.OUTPUT_LAYER, 'Output layer'))


    def processAlgorithm(self, progress):
        inLayer = self.getParameterValue(self.INPUT_LAYER)
        ogrLayer = self.ogrConnectionString(inLayer)
        layername = "'" + self.ogrLayerName(inLayer) + "'"
        geometry = unicode(self.getParameterValue(self.GEOMETRY))
        field = unicode(self.getParameterValue(self.FIELD))        
        statsatt = unicode(self.getParameterValue(self.STATSATT))
        stats = self.getParameterValue(self.STATS)
        area = self.getParameterValue(self.AREA)
        multi = self.getParameterValue(self.MULTI)
        count = self.getParameterValue(self.COUNT)
        fields = self.getParameterValue(self.FIELDS)
        #dsUri = QgsDataSourceURI(self.getParameterValue(self.INPUT_LAYER))
        #geomColumn = dsUri.geometryColumn()
        querystart = '-dialect sqlite -sql "SELECT ST_Union(' + geometry + ')'
        queryend = ' FROM ' + layername + ' GROUP BY ' + field + '"'
        if fields:
           queryfields = ",*"
        else:
           queryfields = "," + field
        if count:
           querycount = ", COUNT(" + geometry + ") AS count"
        else:
           querycount = ""
        if stats:
           querystats = ", SUM(" + statsatt + ") AS sum_diss, MIN(" + statsatt + ") AS min_diss, MAX(" + statsatt + ") AS max_diss, AVG(" + statsatt + ") AS avg_diss"
        else:
           querystats = ""
        if area:
           queryarea = ", SUM(ST_area(" + geometry + ")) AS area_diss, ST_perimeter(ST_union(" + geometry + ")) AS peri_diss"
        else:
           queryarea = ""  
        
        query = querystart + queryfields + querycount + querystats + queryarea + queryend
        output = self.getOutputFromName(self.OUTPUT_LAYER)
        outFile = output.value

        output = self.ogrConnectionString(outFile)
        options = unicode(self.getParameterValue(self.OPTIONS))

        arguments = []
        arguments.append(output)
        arguments.append(ogrLayer)
        arguments.append(query)               

        if not multi:
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