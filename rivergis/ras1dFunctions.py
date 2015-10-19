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
    # TODO: Retrieve chunksize from user.
    """Probe a DTM to find cross-section vertical shape"""
    # Prepare DTMs
    surface_obj = heco.XSSurface()
    parent_obj = heco.XSCutLines()
    prepare_DTMs(rgis)
    update_DtmID(rgis, parent_obj)

    # insert xs points along each xsection
    rgis.rdb.process_hecobject(heco.XSSurface, 'pg_create_table')
    rgis.rdb.process_hecobject(heco.XSCutLines, 'pg_surface_points')

    # probe a DTM at each point
    QApplication.setOverrideCursor(Qt.WaitCursor)
    try:
        probe_DTMs(rgis, surface_obj, parent_obj, chunksize=10000)
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
    rgis.addInfo('<br><b>Running River Reach Names for Bridges/Culverts...</b>')
    # TODO

def ras1dBRStationing(rgis):
    rgis.addInfo('<br><b>Running Stationing for Bridges/Culverts...</b>')
    # TODO

def ras1dBRElevations(rgis):
    rgis.addInfo('<br><b>Running Elevations for Bridges/Culverts...</b>')
    # TODO

def ras1dRASBRAll(rgis):
    rgis.addInfo('<br><b>Running All Functions for Bridges/Culverts...</b>')
    # TODO

def ras1dInlRiverReachNames(rgis):
    rgis.addInfo('<br><b>Running River Reach Names for Inline Structures...</b>')
    # TODO

def ras1dInlStationing(rgis):
    rgis.addInfo('<br><b>Running Stationing for Inline Structures...</b>')
    # TODO

def ras1dInlElevations(rgis):
    rgis.addInfo('<br><b>Running Elevations for Inline Structures...</b>')
    # TODO

def ras1dInlAll(rgis):
    rgis.addInfo('<br><b>Running All Functions for Inline Structures...</b>')
    # TODO

def ras1dLatRiverReachNames(rgis):
    rgis.addInfo('<br><b>Running River Reach Names for Lateral Structures...</b>')
    # TODO

def ras1dLatStationing(rgis):
    rgis.addInfo('<br><b>Running Stationing for Lateral Structures...</b>')
    # TODO

def ras1dLatElevations(rgis):
    rgis.addInfo('<br><b>Running Elevations for Lateral Structures...</b>')
    # TODO


def ras1dLatAll(rgis):
    rgis.addInfo('<br><b>Running All Functions for Lateral Structures...</b>')
    # TODO

def ras1dSAElevations(rgis):
    """Probe a DTM to find storage area vertical shape"""
    # TODO: Retrieve chunksize from user.
    # Prepare DTMs
    surface_obj = heco.SASurface()
    parent_obj = heco.StorageAreas()
    prepare_DTMs(rgis)
    update_DtmID(rgis, parent_obj)

    # probe a DTM at each point
    QApplication.setOverrideCursor(Qt.WaitCursor)
    try:
        rgis.addInfo('<br><b>Creating point grid inside Storage Areas...</b>')
        rgis.rdb.process_hecobject(heco.SASurface, 'pg_create_table')
        rgis.rdb.process_hecobject(heco.StorageAreas, 'pg_surface_points')
        rgis.addInfo('Done')
        rgis.addInfo('<br><b>Extracting values from raster...</b>')
        probe_DTMs(rgis, surface_obj, parent_obj, chunksize=10000)
        rgis.addInfo('Done')
    finally:
        QApplication.restoreOverrideCursor()


def ras1dSAVolumeData(rgis):
    # TODO: Retrieve number of slices from user.
    rgis.addInfo('<br><b>Calculating elevation-volume data for Storage Areas...</b>')
    rgis.rdb.process_hecobject(heco.StorageAreas, 'pg_storage_calculator', slices=5)
    rgis.addInfo('Done')


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

