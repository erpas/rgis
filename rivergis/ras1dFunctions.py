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
import hecobjects as heco
from qgis.core import QgsVectorLayer, QgsMapLayerRegistry, QgsDataSourceURI, QgsPoint, QgsRaster
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from os.path import dirname
from ras_gis_import import RasGisImport
from rasElevations import prepare_DTMs, update_DtmID, probe_DTMs
from dlg_rasXSUpdate import DlgXSUpdateInsertMeasuredPts


def ras1dStreamCenterlineTopology(rgis):
    """Create river network topology. Create nodes at reach ends and find the direction of flow (fromNode, toNode)"""
    # check if streamlines table is registered
    sc_exist = 'StreamCenterlines' in rgis.rdb.register.keys()
    if not sc_exist:
        rgis.addInfo('<br>StreamCenterlines are not registered in the river database. Import or create stream centerlines. <br>Cancelling...')
        return

    rgis.addInfo('<br><b>Building stream centerlines topology...</b>')
    rgis.rdb.process_hecobject(heco.NodesTable, 'pg_create_table')
    if rgis.rdb.process_hecobject(heco.StreamCenterlines, 'pg_topology'):
        rgis.addInfo('Done.')


def ras1dStreamCenterlineLengthsStations(rgis):
    """Calculate river reaches length and their endpoints stations"""
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
    sc_exist = 'StreamCenterlines' in rgis.rdb.register.keys()
    xs_exist = 'XSCutLines' in rgis.rdb.register.keys()
    if not sc_exist or not xs_exist:
        rgis.addInfo('<br>StreamCenterlines or XSCutLines table is not registered in the river database. Cancelling...')
        return
    rgis.addInfo('<br><b>Setting river and reach names for each cross-section...</b>')
    if rgis.rdb.process_hecobject(heco.XSCutLines, 'pg_river_reach_names'):
        rgis.addInfo('Done.')


def ras1dXSStationing(rgis):
    """Finds cross-sections' stationing (chainages) along its river reach"""
    rgis.addInfo('<br><b>Calculating cross-sections stationing...</b>')
    if rgis.rdb.process_hecobject(heco.XSCutLines, 'pg_stationing'):
        rgis.addInfo('Done.')


def ras1dXSBankStations(rgis):
    """Find banks stations for each cross-section. Based on intersection of banks and xs lines"""
    rgis.addInfo('<br><b>Calculating cross-sections banks stations...</b>')
    if rgis.rdb.process_hecobject(heco.XSCutLines, 'pg_bank_stations'):
        rgis.addInfo('Done.')


def ras1dXSDownstreamLengths(rgis):
    """Calculates downstream reach lengths from each cross-section along the 3 flow paths (channel, left and right overbank)"""
    rgis.addInfo('<br><b>Calculating cross-sections distances to the next cross-section downstream ...</b>')
    # check the flowpaths line type if not empty
    qry = 'SELECT "LineType" FROM "{0}"."Flowpaths";'.format(rgis.rdb.SCHEMA)
    lineTypes = rgis.rdb.run_query(qry, fetch=True)
    for row in lineTypes:
        if row[0].lower() not in ['channel', 'right', 'left', 'c', 'l', 'r']:
            rgis.addInfo(row[0])
            rgis.addInfo('Check the Flowpaths LineType attribute values - it should be one of: Channel, Right, Left, C, L, or r')
            return
    if rgis.rdb.process_hecobject(heco.XSCutLines, 'pg_downstream_reach_lengths', line_type='Channel', sort=True):
        rgis.addInfo('Channel flowpaths done.')
    if rgis.rdb.process_hecobject(heco.XSCutLines, 'pg_downstream_reach_lengths', line_type='Left', sort=False):
        rgis.addInfo('Left flowpaths done.')
    if rgis.rdb.process_hecobject(heco.XSCutLines, 'pg_downstream_reach_lengths', line_type='Right', sort=False):
        rgis.addInfo('Right flowpaths done.')


def ras1dStreamCenterlines2Flowpaths(rgis):
    """Copy stream centerlines into flowpaths PostGIS table.
    Reaches are merged based on their river name to form a continuous lines."""
    rgis.addInfo('<br><b>Copying stream centerlines into flowpaths...</b>')
    if rgis.rdb.process_hecobject(heco.Flowpaths, 'pg_channel_from_stream'):
        rgis.addInfo('Done.')


def ras1dXSElevations(rgis):
    """Probe a DTM to find cross-section vertical shape"""
    # Prepare DTMs
    surface_obj = heco.XSSurface()
    parent_obj = heco.XSCutLines()
    prepare_DTMs(rgis)
    update_DtmID(rgis, parent_obj)
    try:
        chunk = rgis.dtm_chunksize
    except:
        chunk = 10000

    # insert xs points along each xsection
    rgis.rdb.process_hecobject(heco.XSSurface, 'pg_create_table')
    rgis.rdb.process_hecobject(heco.XSCutLines, 'pg_surface_points')

    # probe a DTM at each point
    QApplication.setOverrideCursor(Qt.WaitCursor)
    try:
        probe_DTMs(rgis, surface_obj, parent_obj, chunksize=chunk)
        rgis.addInfo('Done')
    finally:
        QApplication.restoreOverrideCursor()


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
    rgis.rdb.process_hecobject(heco.LeveePoints, 'pg_create_table')
    if rgis.rdb.process_hecobject(heco.LeveeAlignment, 'pg_levee_positions'):
        rgis.addInfo('Done.')


def ras1dIneffective(rgis):
    rgis.addInfo('<br><b>Finding ineffective flow areas for cross-sections</b>')
    rgis.rdb.process_hecobject(heco.IneffLines, 'pg_create_table')
    if rgis.rdb.process_hecobject(heco.IneffAreas, 'pg_ineffective_positions'):
        rgis.addInfo('Done.')


def ras1dObstructions(rgis):
    rgis.addInfo('<br><b>Finding blocked obstructions for cross-sections</b>')
    rgis.rdb.process_hecobject(heco.BlockLines, 'pg_create_table')
    if rgis.rdb.process_hecobject(heco.BlockedObs, 'pg_blocked_positions'):
        rgis.addInfo('Done.')


def ras1dBRRiverReachNames(rgis):
    """Finds river and reach name for each bridge"""
    sc_exist = 'StreamCenterlines' in rgis.rdb.register.keys()
    br_exist = 'Bridges' in rgis.rdb.register.keys()
    if not sc_exist or not br_exist:
        rgis.addInfo('<br>StreamCenterlines or Bridges table is not registered in the river database. Cancelling...')
        return
    rgis.addInfo('<br><b>Setting river and reach names for each bridge...</b>')
    if rgis.rdb.process_hecobject(heco.Bridges, 'pg_river_reach_names'):
        rgis.addInfo('Done.')


def ras1dBRStationing(rgis):
    """Finds bridges stationing (chainages) along its river reach"""
    rgis.addInfo('<br><b>Calculating bridges stationing...</b>')
    if rgis.rdb.process_hecobject(heco.Bridges, 'pg_stationing'):
        rgis.addInfo('Done.')


def ras1dBRElevations(rgis):
    rgis.addInfo('<br><b>Running Elevations for Bridges/Culverts...</b>')
    # TODO


def ras1dRASBRAll(rgis):
    # TODO: Add Elevation calculations.
    ras1dBRRiverReachNames(rgis)
    ras1dBRStationing(rgis)


def ras1dISRiverReachNames(rgis):
    """Finds river and reach name for each inline structure"""
    sc_exist = 'StreamCenterlines' in rgis.rdb.register.keys()
    is_exist = 'InlineStructures' in rgis.rdb.register.keys()
    if not sc_exist or not is_exist:
        rgis.addInfo('<br>StreamCenterlines or InlineStructures table is not registered in the river database. Cancelling...')
        return
    rgis.addInfo('<br><b>Setting river and reach names for each inline structure...</b>')
    if rgis.rdb.process_hecobject(heco.InlineStructures, 'pg_river_reach_names'):
        rgis.addInfo('Done.')


def ras1dISStationing(rgis):
    """Finds inline structures stationing (chainages) along its river reach"""
    rgis.addInfo('<br><b>Calculating inline structures stationing...</b>')
    if rgis.rdb.process_hecobject(heco.InlineStructures, 'pg_stationing'):
        rgis.addInfo('Done.')


def ras1dISElevations(rgis):
    rgis.addInfo('<br><b>Running Elevations for Inline Structures...</b>')
    # TODO


def ras1dISAll(rgis):
    # TODO: Add Elevation calculations.
    ras1dISRiverReachNames(rgis)
    ras1dISStationing(rgis)

def ras1dLatRiverReachNames(rgis):
    """Finds river and reach name for each lateral structure"""
    sc_exist = 'StreamCenterlines' in rgis.rdb.register.keys()
    ls_exist = 'LateralStructures' in rgis.rdb.register.keys()
    if not sc_exist or not ls_exist:
        rgis.addInfo('<br>StreamCenterlines or LateralStructures table is not registered in the river database. Cancelling...')
        return
    rgis.addInfo('<br><b>Setting river and reach names for each lateral structure...</b>')
    if rgis.rdb.process_hecobject(heco.LateralStructures, 'pg_river_reach_names'):
        rgis.addInfo('Done.')


def ras1dLatStationing(rgis):
    """Finds lateral structures stationing (chainages) along its river reach"""
    rgis.addInfo('<br><b>Calculating lateral structures stationing...</b>')
    if rgis.rdb.process_hecobject(heco.LateralStructures, 'pg_stationing'):
        rgis.addInfo('Done.')


def ras1dLatElevations(rgis):
    rgis.addInfo('<br><b>Running Elevations for Lateral Structures...</b>')
    # TODO


def ras1dLatAll(rgis):
    # TODO: Add Elevation calculations.
    ras1dLatRiverReachNames(rgis)
    ras1dLatStationing(rgis)


def ras1dSAElevations(rgis):
    """Probe a DTM to later find storage area volume"""
    # Prepare DTMs
    surface_obj = heco.SASurface()
    parent_obj = heco.StorageAreas()
    prepare_DTMs(rgis)
    update_DtmID(rgis, parent_obj)
    try:
        chunk = rgis.dtm_chunksize
    except:
        chunk = 10000

    # probe a DTM at each point
    QApplication.setOverrideCursor(Qt.WaitCursor)
    try:
        rgis.addInfo('<br><b>Calculating Storage Areas elevation values...</b>')
        rgis.rdb.process_hecobject(heco.SASurface, 'pg_create_table')
        rgis.addInfo('Creating point grid inside Storage Areas...')
        rgis.rdb.process_hecobject(heco.StorageAreas, 'pg_surface_points')
        rgis.addInfo('Extracting values from raster...')
        probe_DTMs(rgis, surface_obj, parent_obj, chunksize=chunk)
        rgis.addInfo('Updating maximum and minimum elevation values in Storage Areas...')
        rgis.rdb.process_hecobject(heco.StorageAreas, 'pg_maxmin')
        rgis.addInfo('Done')
    finally:
        QApplication.restoreOverrideCursor()


def ras1dSAVolumeData(rgis):
    # TODO: Retrieve number of slices from user.
    rgis.addInfo('<br><b>Calculating elevation-volume data for Storage Areas...</b>')
    rgis.rdb.process_hecobject(heco.StorageAreas, 'pg_storage_calculator', slices=5)
    rgis.addInfo('Done')


def ras1dSAAll(rgis):
    ras1dSAElevations(rgis)
    ras1dSAVolumeData(rgis)


def ras1dSACAssignNearestSA(rgis):
    rgis.addInfo('<br><b>Finding nearest Storage Areas for the connection...</b>')


def ras1dSACElevations(rgis):
    rgis.addInfo('<br><b>Running Elevations for Storage Areas Connections...</b>')


def ras1dSACAll(rgis):
    ras1dSAElevations(rgis)
    ras1dSAVolumeData(rgis)


def ras1dXSUpdateInsertMeasuredPts(rgis):
    rgis.addInfo('<br><b>Updating cross-sections - inserting measured points...</b>')
    dlg = DlgXSUpdateInsertMeasuredPts(rgis)
    dlg.exec_()


def ras1dCreateRasGisImportFile(rgis):
    """
    Save HEC-RAS model geometry in RAS GIS Import format (SDF).
    """
    rgis.addInfo('<br><b>Creating RAS GIS Import file from HEC-RAS model geometry...</b>')
    s = QSettings()
    lastRasGisImportFileDir = s.value("rivergis/lastRasGisImportDir", "")
    importFileName = QFileDialog.getSaveFileName(None,
                     'Target HEC-RAS GIS Import file',
                     directory=lastRasGisImportFileDir,
                     filter='HEC-RAS GIS Import (*.sdf)')
    if not importFileName:
        rgis.addInfo('Creating RAS GIS Import file cancelled.')
        return
    s.setValue("rivergis/lastRasGisImportDir", dirname(importFileName))
    rgi = RasGisImport(rgis)
    sdf = rgi.gis_import_file()
    if rgis.DEBUG:
        rgis.addInfo(sdf)
    with open(importFileName, 'w') as importFile:
        importFile.write(sdf)
    rgis.addInfo('Done.')
