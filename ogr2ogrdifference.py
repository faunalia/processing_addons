# -*- coding: utf-8 -*-

"""
***************************************************************************
    clipbypolygon.py
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

class ogr2ogrdifference(OgrAlgorithm):

    INPUT_LAYER_A = 'INPUT_LAYER_A'
    INPUT_LAYER_B = 'INPUT_LAYER_B'
    FIELD_A = 'FIELD_A'
    FIELD_B = 'FIELD_B'
    FIELDS_A = 'FIELDS_A'
    TABLE = 'TABLE'
    SCHEMA = 'SCHEMA'
    MULTI = 'MULTI'    
    OPTIONS = 'OPTIONS'
    OUTPUT = 'OUTPUT'
    
    def getIcon(self):
        return  QIcon(os.path.dirname(__file__) + '/icons/postgis.png')

    def defineCharacteristics(self):
        self.name = 'Polygon Difference (non symmetrical)'
        self.group = '[OGR] PostGIS Geoprocessing'

        self.addParameter(ParameterVector(self.INPUT_LAYER_A, 'Input layer',
                          [ParameterVector.VECTOR_TYPE_POLYGON], False))
        self.addParameter(ParameterTableField(self.FIELD_A, 'First input layer ID',
                          self.INPUT_LAYER_A, optional=False))
        self.addParameter(ParameterString(self.FIELDS_A, 'Fields/attributes of input layer to be kept in results (comma separated list)',
                          '', optional=False))
        self.addParameter(ParameterVector(self.INPUT_LAYER_B, 'Layer to be subtracted',
                          [ParameterVector.VECTOR_TYPE_POLYGON], False))
        self.addParameter(ParameterTableField(self.FIELD_B, 'Second input layer ID',
                          self.INPUT_LAYER_B, optional=False))
        self.addParameter(ParameterString(self.SCHEMA, 'Output schema',
                          'public', optional=False))
        self.addParameter(ParameterString(self.TABLE, 'Output table name',
                          'difference', optional=False))
        self.addParameter(ParameterBoolean(self.MULTI,
                          'Output as multipart geometries?', True))
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
        fieldsA = unicode(self.getParameterValue(self.FIELDS_A))
        dsUriA = QgsDataSourceURI(self.getParameterValue(self.INPUT_LAYER_A))
        geomColumnA = dsUriA.geometryColumn()
        dsUriB = QgsDataSourceURI(self.getParameterValue(self.INPUT_LAYER_B))
        geomColumnB = dsUriB.geometryColumn()
        schema = unicode(self.getParameterValue(self.SCHEMA))
        table = unicode(self.getParameterValue(self.TABLE))
        multi = self.getParameterValue(self.MULTI)
        if len(fieldsA) > 0:
           fieldstring = "," + fieldsA
        else:
           fieldstring = ""        

        if multi:
           sqlstring = "-sql \"SELECT (ST_Multi(ST_Difference(g1." + geomColumnA + ",ST_Union(g2." + geomColumnB + "))))::geometry(MultiPolygon) AS geom, g1. " + fieldA + " AS id_input" + fieldstring + " FROM " + layernameA + " AS g1, " + layernameB + " AS g2 GROUP BY g1." + geomColumnA + ",g1." + fieldA + "\""" -nln " + table + " -lco SCHEMA=" + schema + " -lco FID=gid -nlt MULTIPOLYGON -lco GEOMETRY_NAME=geom --config PG_USE_COPY YES"
        else:
           sqlstring = "-sql \"SELECT (ST_Dump(ST_Difference(g1." + geomColumnA + ",ST_Union(g2." + geomColumnB + ")))).geom::geometry(Polygon) AS geom, g1. " + fieldA + " AS id_input" + fieldstring + " FROM " + layernameA + " AS g1, " + layernameB + " AS g2 GROUP BY g1." + geomColumnA + ",g1." + fieldA + "\""" -nln " + table + " -lco SCHEMA=" + schema + " -lco FID=gid -nlt POLYGON -lco GEOMETRY_NAME=geom --config PG_USE_COPY YES"

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