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


def update_DtmID(rgis, parent_obj):
    parent_id = parent_obj.attrs[0][0]
    qry = '''
-- get the smallest cell size DTM covering each feature --
WITH data AS
    (SELECT DISTINCT ON (par.{2})
        par.{2} as {2},
        dtm."DtmID" as "DtmID",
        dtm."CellSize" as "CellSize"
    FROM
        "{0}"."{1}" as par,
        "{0}"."DTMs" as dtm
    WHERE
        ST_Contains(dtm.geom, par.geom)
    ORDER BY
        par.{2},
        dtm."CellSize")
UPDATE "{0}"."{1}" as par
SET
    "DtmID" = data."DtmID"
FROM
    data
WHERE
    data.{2} = par.{2};
'''
    qry = qry.format(rgis.rdb.SCHEMA, parent_obj.name, parent_id)
    rgis.rdb.run_query(qry)


def probe_DTMs(rgis, surface_obj, parent_obj, chunksize=0):
    # probe a DTM at each point
    rgis.addInfo('<br><b>Probing DTM along {0}...</b>'.format(parent_obj.name))
    qry = 'SELECT * FROM "{0}"."DTMs";'.format(rgis.rdb.SCHEMA)
    dtms = rgis.rdb.run_query(qry, fetch=True)
    parent_id = parent_obj.attrs[0][0]
    for dtm in dtms:
        dtm_id = dtm['DtmID']
        lid = dtm['LayerID']
        rlayer = rgis.mapRegistry.mapLayer(lid)
        qry = '''
SELECT
    surf."PtID" AS "PtID",
    ST_X(surf.geom) AS x,
    ST_Y(surf.geom) AS y
FROM
    "{0}"."{1}" AS surf,
    "{0}"."{2}" AS par
WHERE
    surf.{3} = par.{3} AND
    par."DtmID" = {4};
'''
        qry = qry.format(rgis.rdb.SCHEMA, surface_obj.name, parent_obj.name, parent_id, dtm_id)
        if chunksize <= 0:
            chunk = [rgis.rdb.run_query(qry, fetch=True)]
        else:
            chunk = rgis.rdb.run_query(qry, fetch=True, arraysize=chunksize)
        if not chunk:
            continue
        else:
            pass
        for pts in chunk:
            if not pts:
                continue
            else:
                pass
            qry = ''
            for pt in pts:
                ident = rlayer.dataProvider().identify(QgsPoint(pt[1], pt[2]), QgsRaster.IdentifyFormatValue)
                try:
                    if ident.isValid():
                        pt.append(round(ident.results()[1], 2))
                        qry += 'UPDATE "{0}"."{1}" SET "Elevation" = {2} WHERE "PtID" = {3};\n'.format(rgis.rdb.SCHEMA, surface_obj.name, pt[3], pt[0])
                except:
                    rgis.addInfo('Problem with getting raster value for point with PtID {0}'.format(pt[0]))
            rgis.rdb.run_query(qry)
