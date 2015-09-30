# -*- coding: utf-8 -*-

"""
/***************************************************************************
Name                 : RiverGIS
Description          : HEC-RAS tools for QGIS
Date                 : January, 2015
copyright            : (C) 2015 by RiverGIS Group
email                : rpasiok@gmail.com
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""
from ras_gis_import import *
import hecobjects as heco
from qgis.core import QgsVectorLayer, QgsMapLayerRegistry, QgsDataSourceURI, QgsPoint, QgsRaster
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from os.path import dirname

def ras1dStreamCenterlineTopology(rgis):
    """Create river network topology. Create nodes at reach ends and find the direction of flow (fromNode, toNode)"""
    # check if streamlines table is registered
    scExist = 'StreamCenterlines' in rgis.rdb.register.keys()
    if not scExist:
        rgis.addInfo('<br>StreamCenterlines are not registered in the river database. Import or create stream centerlines. <br>Cancelling...')
        return

    rgis.addInfo('<br><b>Building stream centerlines topology...</b>')
    rgis.rdb.process_hecobject(heco.NodesTable, 'pg_create_table')
    if rgis.rdb.process_hecobject(heco.StreamCenterlines, 'pg_topology'):
        rgis.addInfo('Done.')


def ras1dStreamCenterlineLengthsStations(rgis):
    """Calculate river reaches lenght and their endpoints stations"""
    ntExist = 'NodesTable' in [t[0] for t in rgis.rdb.list_tables()]
    if not ntExist:
        rgis.addInfo('<br>NodesTable is not registered in the river database.<br>Build stream centerlines topology first.<br>Cancelling...')
        qry = ''
    rgis.addInfo('<br><b>Calculating river reach(es) lenghts and their end stations...</b>')
    rgis.rdb.process_hecobject(heco.Endpoints, 'pg_create_table')
    if rgis.rdb.process_hecobject(heco.StreamCenterlines, 'pg_lengths_stations'):
        rgis.addInfo('Done.')


def ras1dStreamCenterlineAll(rgis):
    """Runs all analyses for rivers' centerlines, i.e. topology + Lengths/stations"""
    ras1dStreamCenterlineTopology(rgis)
    ras1dStreamCenterlineLengthsStations(rgis)


def ras1dXSRiverReachNames(rgis):
    """Finds river and reach name for each cross-section"""
    # check if streamlines  and xsec tables are registered
    scExist = 'StreamCenterlines' in rgis.rdb.register.keys()
    xsExist = 'XSCutLines' in rgis.rdb.register.keys()
    if not scExist or not xsExist:
        rgis.addInfo('<br>StreamCenterlines or XSCutLines table is not registered in the river database. Cancelling...')
        return
    rgis.addInfo('<br><b>Setting river and reach names for each cross-section...</b>')
    if rgis.rdb.process_hecobject(heco.XSCutLines, 'pg_river_reach_names'):
        rgis.addInfo('Done.')


def ras1dXSStationing(rgis):
    """Finds cross-sections' stationing (chainages) along its river reach"""
    rgis.addInfo('<br><b>Calculating cross-sections\' stationing...</b>')
    if rgis.rdb.process_hecobject(heco.XSCutLines, 'pg_stationing'):
        rgis.addInfo('Done.')


def ras1dXSBankStations(rgis):
    """Find banks stations for each cross-section. Based on intersection of banks and xs lines"""
    rgis.addInfo('<br><b>Calculating cross-sections\' banks stations...</b>')
    if rgis.rdb.process_hecobject(heco.XSCutLines, 'pg_bank_stations'):
        rgis.addInfo('Done.')


def ras1dXSDownstreamLengths(rgis):
    """Calculates downstream reach lengths from each cross-section along the 3 flow paths (channel, left and right overbank)"""
    rgis.addInfo('<br><b>Calculating cross-sections\' distances to the next cross-section downstream ...</b>')
    # check the flowpaths line type if not empty
    qry = 'SELECT "LineType" FROM "{0}"."Flowpaths";'.format(rgis.rdb.SCHEMA)
    lineTypes = rgis.rdb.run_query(qry, fetch=True)
    for row in lineTypes:
        if row[0].lower() not in ['channel', 'right', 'left', 'c', 'l', 'r']:
            rgis.addInfo('Check the Flowpaths LineType attribute values - it should be one of: Channel, Right, Left, C, L, or r')
            return
    if rgis.rdb.process_hecobject(heco.XSCutLines, 'pg_downstream_reach_lengths'):
        rgis.addInfo('Done.')


def ras1dXSElevations(rgis):
    """Probe a DTM to find cross-section vertical shape"""
    QApplication.setOverrideCursor(Qt.WaitCursor)

    rgis.addInfo('<br><b>Creating cross-sections\' points:</b>')
    # # Create xsection points table
    rgis.rdb.process_hecobject(heco.XSPoints, 'pg_create_table')

    # Create DTMs table
    rgis.rdb.process_hecobject(heco.DTMs, 'pg_create_table')

    # insert DTMs parameters into the DTMs table
    if not rgis.dtms:
        rgis.addInfo('<br>Choose a DTM for cross-section points elevation (Settings > DTM Setup) and try again.')
        return
    dtmsParams = []
    for layerId in rgis.dtms:
        rlayer = rgis.mapRegistry.mapLayer(layerId)
        name = '\'{0}\''.format(rlayer.name())
        uri = '\'{0}\''.format(rlayer.dataProvider().dataSourceUri())
        dp = '\'{0}\''.format(rlayer.dataProvider().name())
        lid = '\'{0}\''.format(rlayer.id())
        pixelSize = min(rlayer.rasterUnitsPerPixelX(), rlayer.rasterUnitsPerPixelY())
        bboxWkt = rlayer.extent().asWktPolygon()
        geom = 'ST_GeomFromText(\'{0}\', {1})'.format(bboxWkt, rgis.rdb.SRID)
        params = '({0})'.format(',\n'.join([geom, name, uri, dp, lid, str(pixelSize)]))
        dtmsParams.append(params)
    qry = '''
        INSERT INTO "{0}"."DTMs" (geom, "Name","DtmUri", "Provider", "LayerID", "CellSize") VALUES \n  {1};
    '''.format(rgis.rdb.SCHEMA, '{0}'.format(',\n'.join(dtmsParams)))
    rgis.rdb.run_query(qry)

    # get the smallest cell size DTM covering each xsection
    qry = '''
    WITH data AS (
    SELECT DISTINCT ON (xs."XsecID")
      xs."XsecID" as "XsecID",
      dtm."DtmID" as "DtmID",
      dtm."CellSize" as "CellSize"
    FROM
      "{0}"."XSCutLines" as xs,
      "{0}"."DTMs" as dtm
    WHERE
      xs.geom && dtm.geom AND
      ST_Contains(dtm.geom, xs.geom)
    ORDER BY xs."XsecID", dtm."CellSize" ASC)
    UPDATE "{0}"."XSCutLines" as xs
    SET
      "DtmID" = data."DtmID"
    FROM data
    WHERE
      data."XsecID" = xs."XsecID";
    SELECT "XsecID", "DtmID"
    FROM "{0}"."XSCutLines";
    '''.format(rgis.rdb.SCHEMA)
    rgis.rdb.run_query(qry)

    # insert xs points along each xsection
    qry = '''
    WITH line AS
      (SELECT
        xs."XsecID" as "XsecID",
        dtm."CellSize" as "CellSize",
        (ST_Dump(xs.geom)).geom AS geom
      FROM
        "{0}"."XSCutLines" as xs,
        "{0}"."DTMs" as dtm
      WHERE
        xs."DtmID" = dtm."DtmID"),
    linemeasure AS
      (SELECT
        "XsecID",
        ST_AddMeasure(line.geom, 0, ST_Length(line.geom)) AS linem,
        generate_series(0, (ST_Length(line.geom)*100)::int, (line."CellSize"*100)::int) AS "Station"
      FROM line),
    geometries AS (
      SELECT
        "XsecID",
        "Station",
        (ST_Dump(ST_GeometryN(ST_LocateAlong(linem, "Station"/100), 1))).geom AS geom
      FROM linemeasure)

    INSERT INTO "{0}"."XSPoints" (geom, "XsecID", "Station")
    SELECT
      ST_SetSRID(ST_MakePoint(ST_X(geom), ST_Y(geom)), {1}) AS geom,
      "XsecID",
      "Station"/100
    FROM geometries;

    INSERT INTO "{0}"."XSPoints" (geom, "XsecID", "Station")
    SELECT
      ST_Endpoint(geom),
      "XsecID",
      ST_Length(geom)
    FROM "{0}"."XSCutLines";
    '''
    qry = qry.format(rgis.rdb.SCHEMA, rgis.rdb.SRID)
    rgis.rdb.run_query(qry)

    # probe a DTM at each xsection point
    qry = 'SELECT * FROM "{0}"."DTMs";'.format(rgis.rdb.SCHEMA)
    dtms = rgis.rdb.run_query(qry, fetch=True)
    for dtm in dtms:
        dtmId = dtm['DtmID']
        lid = dtm['LayerID']
        rlayer = rgis.mapRegistry.mapLayer(lid)
        qry = '''
        WITH xsids AS (
        SELECT "XsecID" FROM "{0}"."XSCutLines" WHERE "DtmID" = {1} ORDER BY "XsecID"
        )
        SELECT
          pts."PtID" as "PtID",
          ST_X(pts.geom) as x,
          ST_Y(pts.geom) as y
        FROM
          "{0}"."XSPoints" as pts,
          xsids
        WHERE
          pts."XsecID" = xsids."XsecID";
        '''.format(rgis.rdb.SCHEMA, dtmId)
        pts = rgis.rdb.run_query(qry, fetch=True)

        if pts:
            qry = ''
            for pt in pts:
                ident = rlayer.dataProvider().identify(QgsPoint(pt[1], pt[2]), QgsRaster.IdentifyFormatValue)
                if rgis.DEBUG > 1:
                    rgis.addInfo('Wartosc rastra w ({1}, {2}): {0}'.format(ident.results()[1], pt[1], pt[2]))
                if ident.isValid():
                    pt.append(round(ident.results()[1], 2))
                    if rgis.DEBUG > 1:
                        rgis.addInfo('{0}'.format(', '.join([str(a) for a in pt])))
                    qry += 'UPDATE "{0}"."XSPoints" SET "Elevation" = {1} WHERE "PtID" = {2};\n'\
                        .format(rgis.rdb.SCHEMA, pt[3], pt[0])
            if rgis.DEBUG:
                rgis.addInfo(qry)
            rgis.rdb.run_query(qry)
        else:
            pass

    QApplication.restoreOverrideCursor()
    rgis.addInfo('Done')


def ras1dXSAll(rgis):
    """Runs all the XS analyses"""
    ras1dXSRiverReachNames(rgis)
    ras1dXSStationing(rgis)
    ras1dXSBankStations(rgis)
    ras1dXSDownstreamLengths(rgis)
    ras1dXSElevations(rgis)


def ras1dXSExtractMannings(rgis):
    rgis.addInfo('<br><b>Extracting Manning\'s n values for cross-sections</b>')
    if rgis.rdb.process_hecobject(heco.LanduseAreas, 'pg_extract_manning'):
        rgis.addInfo('Done.')


def ras1dLevees(rgis):
    rgis.addInfo('<br><b>Calculating levees stations for cross-sections...</b>')
    # TODO
    if rgis.rdb.process_hecobject(heco.LeveeAlignment, 'pg_????'):
        rgis.addInfo('Done.')


def ras1dIneffective(rgis):
    rgis.addInfo('<br><b>Finding ineffective flow areas for cross-sections</b>')
    # TODO
    if rgis.rdb.process_hecobject(heco.IneffAreas, 'pg_????'):
        rgis.addInfo('Done.')


def ras1dObstructions(rgis):
    rgis.addInfo('<br><b>Finding blocked obstructions for cross-sections</b>')
    # TODO
    if rgis.rdb.process_hecobject(heco.BlockedObs, 'pg_????'):
        rgis.addInfo('Done.')


def ras1dXSInsertMeasPts(rgis):
    rgis.addInfo('<br><b>Updating cross-sections - inserting measured points...</b>')
    # TODO
    if rgis.rdb.process_hecobject(heco.XSCutlines, 'pg_????'):
        rgis.addInfo('Done.')


def ras1dCreateRasGisImportFile(rgis):
    """
    Save HEC-RAS model geometry in RAS GIS Import format.
    """
    s = QSettings()
    lastRasGisImportFileDir = s.value("rivergis/lastRasGisImportDir", "")
    importFileName = QFileDialog.getSaveFileName(None, \
                     'Target HEC-RAS GIS Import file', \
                     directory=lastRasGisImportFileDir, \
                     filter='HEC-RAS GIS Import (*.sdf)')
    if not importFileName:
        return
    s.setValue("rivergis/lastRasGisImportDir", dirname(importFileName))
    rgi = RasGisImport(rgis)
    sdf = rgi.gis_import_file()
    if rgis.DEBUG:
        rgis.addInfo(sdf)
    importFile = open(importFileName, 'w')
    importFile.write(sdf)
    importFile.close()
