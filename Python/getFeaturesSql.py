# -*- coding: utf-8 -*-

import unicodedata
from qgis.core import *


def toAscii(text):
    """Removes diacritics from the string, replaceses spaces with underscore"""
    a = text.decode('utf-8').replace(u'\u0141', "L").replace(u'\u0142', "l")
    # b = a.replace(" ", "_")
    textAscii = unicodedata.normalize("NFKD", a).encode('ascii', 'ignore')
    return textAscii

SCHEMA = 'start'
SRID = 2180

# layer to import
layer = QgsVectorLayer("C:/Users/T410/Documents/qgis_plugins/rgroup_example/start/streamcenterlines.shp", "SC", "ogr")
if not layer.isValid():
    print "Layer failed to load!"
else:
    print "Layer loaded succesfully"
# layer = iface.activeLayer()

# kod dla warstwy StreamCenterlines
layerName = 'StreamCenterlines'
layerGeomType = 'LINESTRING'

tryImportFields = ['ReachCode', 'RiverCode'] # fields to import to PG

def getLayerInsertIntoPGSql(layer, ):

    # get all features from the layer
    features = layer.getFeatures()

    # get the layer's field name list
    layerFields = []
    for attr in layer.pendingFields():
        layerFields.append(attr.name())


    importFields = [] # list of fields that will be imported

    # check if the layer has attributes to import and get their values
    for fieldName in tryImportFields:
        if fieldName in layerFields:
            importFields.append(fieldName)

    # create SQL for inserting the layer into PG database
    schTable = '"{0}"."{1}"'.format(SCHEMA, layerName)
    attrs = ['"{0}"'.format(toAscii(attr)) for attr in importFields]

    qry = 'INSERT INTO {0} \n\t({1}, geom) \nVALUES\n\t('.format(schTable, ', '.join(attrs))
    rows = []
    for feat in features:
        geomWkt = feat.geometry().exportToWkt()
        vals =['\'{0}\''.format( '\', \''.join([feat.attribute(attr)]) ) for attr in importFields]
        vals.append('ST_GeomFromText(\'{0}\', {1})'.format(geomWkt, SRID))
        rows.append('{0}'.format(', '.join(vals)))

    qry += '{0});'.format('),\n\t('.join(rows))
    print qry