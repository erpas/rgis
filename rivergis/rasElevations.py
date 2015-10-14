# -*- coding: utf-8 -*-
__author__ = 'Łukasz Dębek'

from hecobjects import DTMs
from qgis.core import QgsVectorLayer, QgsMapLayerRegistry, QgsDataSourceURI, QgsPoint, QgsRaster
from PyQt4.QtCore import *
from PyQt4.QtGui import *


def prepare_DTMs(rgis):
    # Create DTMs table
    rgis.rdb.process_hecobject(DTMs, 'pg_create_table')
    # insert DTMs parameters into the DTMs table
    if not rgis.dtms:
        rgis.rasDTMSetup()
    if not rgis.dtms:
        rgis.addInfo('<br> Choose a DTM for elevation sampling.')
        return
    dtms_params = []
    for layer_id in rgis.dtms:
        rlayer = rgis.mapRegistry.mapLayer(layer_id)
        name = '\'{0}\''.format(rlayer.name())
        uri = '\'{0}\''.format(rlayer.dataProvider().dataSourceUri())
        dp = '\'{0}\''.format(rlayer.dataProvider().name())
        lid = '\'{0}\''.format(rlayer.id())
        pixel_size = min(rlayer.rasterUnitsPerPixelX(), rlayer.rasterUnitsPerPixelY())
        bbox_wkt = rlayer.extent().asWktPolygon()
        geom = 'ST_GeomFromText(\'{0}\', {1})'.format(bbox_wkt, rgis.rdb.SRID)
        params = '({0})'.format(',\n'.join([geom, name, uri, dp, lid, str(pixel_size)]))
        dtms_params.append(params)
    qry = 'INSERT INTO "{0}"."DTMs" (geom, "Name","DtmUri", "Provider", "LayerID", "CellSize") VALUES \n  {1};'
    qry = qry.format(rgis.rdb.SCHEMA, '{0}'.format(',\n'.join(dtms_params)))
    rgis.rdb.run_query(qry)


def probe_DTMs(rgis, surface):
    # probe a DTM at each point
    qry = 'SELECT * FROM "{0}"."DTMs";'.format(rgis.rdb.SCHEMA)
    dtms = rgis.rdb.run_query(qry, fetch=True)
    for dtm in dtms:
        dtm_id = dtm['DtmID']
        lid = dtm['LayerID']
        rlayer = rgis.mapRegistry.mapLayer(lid)
        qry = 'SELECT "PtID", ST_X(geom) as x, ST_Y(geom) as y FROM "{0}"."{1}" WHERE "DtmID" = {2};'
        qry = qry.format(rgis.rdb.SCHEMA, surface, dtm_id)
        pts = rgis.rdb.run_query(qry, fetch=True)
        if pts:
            qry = ''
            for pt in pts:
                ident = rlayer.dataProvider().identify(QgsPoint(pt[1], pt[2]), QgsRaster.IdentifyFormatValue)
                if rgis.DEBUG > 1:
                    rgis.addInfo('Raster value in ({1}, {2}): {0}'.format(ident.results()[1], pt[1], pt[2]))
                if ident.isValid():
                    pt.append(round(ident.results()[1], 2))
                    if rgis.DEBUG > 1:
                        rgis.addInfo('{0}'.format(', '.join([str(a) for a in pt])))
                    qry += 'UPDATE "{0}"."{1}" SET "Elevation" = {2} WHERE "PtID" = {3};\n'.format(rgis.rdb.SCHEMA, surface, pt[3], pt[0])
            if rgis.DEBUG:
                rgis.addInfo(qry)
            rgis.rdb.run_query(qry)
        else:
            pass
