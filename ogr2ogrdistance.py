# -*- coding: utf-8 -*-

"""
***************************************************************************
    ogr2ogrdistance.py
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
from processing.core.outputs import OutputHTML

from processing.tools.system import *
from processing.tools import dataobjects

from processing.algs.gdal.OgrAlgorithm import OgrAlgorithm
from processing.algs.gdal.GdalUtils import GdalUtils

class ogr2ogrdistance(OgrAlgorithm):

    OUTPUT_LAYER = 'OUTPUT_LAYER'
    INPUT_LAYER_A = 'INPUT_LAYER_A'
    INPUT_LAYER_B = 'INPUT_LAYER_B'
    FIELD_A = 'FIELD_A'
    FIELD_B = 'FIELD_B'
    TABLE = 'TABLE'
    SCHEMA = 'SCHEMA'
    OPTIONS = 'OPTIONS'
    OUTPUT = 'OUTPUT'
    
    def getIcon(self):
        return  QIcon(os.path.dirname(__file__) + '/icons/postgis.png')

    def defineCharacteristics(self):
        self.name = 'Distance between features'
        self.group = '[OGR] PostGIS Geoprocessing'

        self.addParameter(ParameterVector(self.INPUT_LAYER_A, 'First input layer',
                          [ParameterVector.VECTOR_TYPE_ANY], False))
        self.addParameter(ParameterTableField(self.FIELD_A, 'First input layer ID',
                          self.INPUT_LAYER_A, optional=False))
        self.addParameter(ParameterVector(self.INPUT_LAYER_B, 'Second input layer',
                          [ParameterVector.VECTOR_TYPE_ANY], False))
        self.addParameter(ParameterTableField(self.FIELD_B, 'Second input layer ID',
                          self.INPUT_LAYER_B, optional=False))
        self.addParameter(ParameterString(self.SCHEMA, 'Output schema',
                          'public', optional=False))
        self.addParameter(ParameterString(self.TABLE, 'Output table name',
                          'distance_analysis', optional=False))
        self.addParameter(ParameterString(self.OPTIONS, 'Additional creation options (see ogr2ogr manual)',
                          '', optional=True))
        self.addOutput(OutputHTML(self.OUTPUT, 'Output log'))
        
    def processAlgorithm(self, progress):
        inLayerA = self.getParameterValue(self.INPUT_LAYER_A)
        ogrLayerA = self.ogrConnectionString(inLayerA)
        layernameA = self.ogrLayerName(inLayerA)
        inLayerB = self.getParameterValue(self.INPUT_LAYER_B)
        ogrLayerB = self.ogrConnectionString(inLayerB)
        layernameB = self.ogrLayerName(inLayerB)
        fieldA = unicode(self.getParameterValue(self.FIELD_A))
        fieldB = unicode(self.getParameterValue(self.FIELD_B))
        dsUriA = QgsDataSourceURI(self.getParameterValue(self.INPUT_LAYER_A))
        geomColumnA = dsUriA.geometryColumn()
        dsUriB = QgsDataSourceURI(self.getParameterValue(self.INPUT_LAYER_B))
        geomColumnB = dsUriB.geometryColumn()
        schema = unicode(self.getParameterValue(self.SCHEMA))
        table = unicode(self.getParameterValue(self.TABLE))
        sqlstring = "-sql \"SELECT ST_ShortestLine(g1." + geomColumnA + ",g2." + geomColumnB + ") AS geom, ST_Distance(g1." + geomColumnA + ",g2." + geomColumnB + ") AS distance, g1. " + fieldA + " AS id_from, g2. " + fieldB + " AS id_to FROM " + layernameA + " AS g1, " + layernameB + " AS g2\" -nln " + table + " -lco SCHEMA=" + schema + " -lco FID=gid -lco GEOMETRY_NAME=geom -nlt LINESTRING --config PG_USE_COPY YES"
        options = unicode(self.getParameterValue(self.OPTIONS))

        arguments = []
        arguments.append('-f')
        arguments.append('PostgreSQL')
        arguments.append(ogrLayerA)
        arguments.append(ogrLayerA)
        arguments.append(sqlstring)
        arguments.append('-overwrite')
                
        if len(options) > 0:
            arguments.append(options)
        #print table   
        commands = []
        if isWindows():
            commands = ['cmd.exe', '/C ', 'ogr2ogr.exe',
                        GdalUtils.escapeAndJoin(arguments)]
        else:
            commands = ['ogr2ogr', GdalUtils.escapeAndJoin(arguments)]

        GdalUtils.runGdal(commands, progress)

        output = self.getOutputValue(self.OUTPUT)
        f = open(output, 'w')
        f.write('<pre>')
        for s in GdalUtils.getConsoleOutput()[1:]:
            f.write(unicode(s))
        f.write('</pre>')
        f.close()        