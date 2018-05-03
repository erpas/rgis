# -*- coding: utf-8 -*-

"""
/***************************************************************************
Name                 : RiverGIS
Description          : HEC-RAS tools for QGIS
Date                 : December, 2015
copyright            : (C) 2015 by RiverGIS Group
email                : rpasiok@gmail.com, damnback333@gmail.com
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
from __future__ import absolute_import
import os

from . import hecobjects as heco
from qgis.PyQt.QtCore import Qt, QSettings
from qgis.PyQt.QtWidgets import QApplication, QInputDialog, QFileDialog

from .ras_gis_import import RasGisImport
from .rasElevations import prepare_DTMs, update_DtmID, probe_DTMs
from .dlg_rasXSUpdate import DlgXSUpdateInsertMeasuredPts


def ras1dStreamCenterlineTopology(rgis):
    """Create river network topology. Create nodes at reach ends and find the direction of flow (fromNode, toNode)"""
    # check if streamlines table is registered
    sc_exist = 'StreamCenterlines' in list(rgis.rdb.register.keys())
    if not sc_exist:
        rgis.addInfo('<br>StreamCenterlines are not registered in the river database. Import or create stream centerlines. <br>Cancelling...')
        return

    rgis.addInfo('<br><b>Building stream centerlines topology...</b>')
    rgis.rdb.process_hecobject(heco.NodesTable, 'pg_create_table')
    if rgis.rdb.process_hecobject(heco.StreamCenterlines, 'pg_topology'):
        rgis.rdb.add_to_view(heco.NodesTable())
        rgis.addInfo('Done.')


def ras1dStreamCenterlineLengthsStations(rgis):
    """Calculate river reaches length and their endpoints stations"""
    nt_exists = 'NodesTable' in rgis.rdb.list_tables()
    if not nt_exists:
        rgis.addInfo('<br>NodesTable is not registered in the river database.<br>Build stream centerlines topology first.<br>Cancelling...')
        return

    rgis.addInfo('<br><b>Calculating river reach(es) lengths and their end stations...</b>')
    rgis.rdb.process_hecobject(heco.Endpoints, 'pg_create_table')
    if rgis.rdb.process_hecobject(heco.StreamCenterlines, 'pg_lengths_stations'):
        rgis.rdb.add_to_view(heco.Endpoints())
        rgis.addInfo('Done.')


def ras1dStreamCenterlineAll(rgis):
    """Runs all analyses for rivers' centerlines, i.e. topology + Lengths/stations"""
    ras1dStreamCenterlineTopology(rgis)
    ras1dStreamCenterlineLengthsStations(rgis)


def ras1dXSRiverReachNames(rgis):
    """Finds river and reach name for each cross-section"""
    # check if streamlines  and xsec tables are registered
    sc_exist = 'StreamCenterlines' in list(rgis.rdb.register.keys())
    xs_exist = 'XSCutLines' in list(rgis.rdb.register.keys())
    if not sc_exist or not xs_exist:
        rgis.addInfo('<br>StreamCenterlines or XSCutLines table is not registered in the river database. Cancelling...')
        return

    # TODO: check stream centerlines names are distinct

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
    line_types = rgis.rdb.run_query(qry, fetch=True)
    for row in line_types:
        if row[0].lower() not in ['channel', 'right', 'left', 'c', 'l', 'r']:
            rgis.addInfo(row[0])
            rgis.addInfo('Check the Flowpaths LineType attribute values - it should be one of: Channel, Right, Left, C, L, or r')
            return

    if rgis.rdb.process_hecobject(heco.XSCutLines, 'pg_downstream_reach_lengths', line_type='Channel'):
        rgis.addInfo('Channel flowpaths done.')
    if rgis.rdb.process_hecobject(heco.XSCutLines, 'pg_downstream_reach_lengths', line_type='Left'):
        rgis.addInfo('Left flowpaths done.')
    if rgis.rdb.process_hecobject(heco.XSCutLines, 'pg_downstream_reach_lengths', line_type='Right'):
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
    prepare_DTMs(rgis)
    if not rgis.dtms:
        rgis.addInfo('<br>No DTM for elevation sampling. Probing aborted!')
        return
    surface_obj = heco.XSSurface()
    parent_obj = heco.XSCutLines()
    update_DtmID(rgis, parent_obj)
    try:
        chunk = rgis.dtm_chunksize
    except:
        chunk = 0

    # insert points along each xsection
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


def ras1dHealLanduseGeoms(rgis):
    rgis.addInfo('<br><b>Healing Landuse Areas geometries</b>')
    if rgis.rdb.process_hecobject(heco.LanduseAreas, 'pg_heal_manning_geometries'):
        rgis.addInfo('Done.')


def ras1dXSExtractMannings(rgis):
    rgis.addInfo('<br><b>Extracting Manning\'s n values for cross-sections</b>')
    rgis.rdb.process_hecobject(heco.Manning, 'pg_create_table')
    if rgis.rdb.process_hecobject(heco.LanduseAreas, 'pg_extract_manning'):
        rgis.rdb.add_to_view(heco.Manning())
        rgis.addInfo('Done.')


def ras1dLevees(rgis):
    rgis.addInfo('<br><b>Calculating levees stations for cross-sections...</b>')
    rgis.rdb.process_hecobject(heco.LeveePoints, 'pg_create_table')
    if rgis.rdb.process_hecobject(heco.LeveeAlignment, 'pg_levee_positions'):
        rgis.rdb.add_to_view(heco.LeveePoints())
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
    sc_exist = 'StreamCenterlines' in list(rgis.rdb.register.keys())
    br_exist = 'Bridges' in list(rgis.rdb.register.keys())
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
    """Probe a DTM to find bridges vertical shape"""
    # Prepare DTMs
    prepare_DTMs(rgis)
    if not rgis.dtms:
        rgis.addInfo('<br>No DTM for elevation sampling. Probing aborted!')
        return
    surface_obj = heco.BRSurface()
    parent_obj = heco.Bridges()
    update_DtmID(rgis, parent_obj)
    try:
        chunk = rgis.dtm_chunksize
    except:
        chunk = 0

    # insert points along each bridge
    rgis.rdb.process_hecobject(heco.BRSurface, 'pg_create_table')
    rgis.rdb.process_hecobject(heco.Bridges, 'pg_surface_points')

    # probe a DTM at each point
    QApplication.setOverrideCursor(Qt.WaitCursor)
    try:
        probe_DTMs(rgis, surface_obj, parent_obj, chunksize=chunk)
        rgis.addInfo('Done')
    finally:
        QApplication.restoreOverrideCursor()


def ras1dRASBRAll(rgis):
    ras1dBRRiverReachNames(rgis)
    ras1dBRStationing(rgis)
    ras1dBRElevations(rgis)


def ras1dISRiverReachNames(rgis):
    """Finds river and reach name for each inline structure"""
    sc_exist = 'StreamCenterlines' in list(rgis.rdb.register.keys())
    is_exist = 'InlineStructures' in list(rgis.rdb.register.keys())
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
    """Probe a DTM to find inline structure vertical shape"""
    # Prepare DTMs
    prepare_DTMs(rgis)
    if not rgis.dtms:
        rgis.addInfo('<br>No DTM for elevation sampling. Probing aborted!')
        return
    surface_obj = heco.ISSurface()
    parent_obj = heco.InlineStructures()
    update_DtmID(rgis, parent_obj)
    try:
        chunk = rgis.dtm_chunksize
    except:
        chunk = 0

    # insert points along each inline structure
    rgis.rdb.process_hecobject(heco.ISSurface, 'pg_create_table')
    rgis.rdb.process_hecobject(heco.InlineStructures, 'pg_surface_points')

    # probe a DTM at each point
    QApplication.setOverrideCursor(Qt.WaitCursor)
    try:
        probe_DTMs(rgis, surface_obj, parent_obj, chunksize=chunk)
        rgis.addInfo('Done')
    finally:
        QApplication.restoreOverrideCursor()


def ras1dISAll(rgis):
    ras1dISRiverReachNames(rgis)
    ras1dISStationing(rgis)
    ras1dISElevations(rgis)


def ras1dLatRiverReachNames(rgis):
    """Finds river and reach name for each lateral structure"""
    sc_exist = 'StreamCenterlines' in list(rgis.rdb.register.keys())
    ls_exist = 'LateralStructures' in list(rgis.rdb.register.keys())
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
    """Probe a DTM to find lateral structure vertical shape"""
    # Prepare DTMs
    prepare_DTMs(rgis)
    if not rgis.dtms:
        rgis.addInfo('<br>No DTM for elevation sampling. Probing aborted!')
        return
    surface_obj = heco.LSSurface()
    parent_obj = heco.LateralStructures()
    update_DtmID(rgis, parent_obj)
    try:
        chunk = rgis.dtm_chunksize
    except:
        chunk = 0

    # insert points along each lateral structure
    rgis.rdb.process_hecobject(heco.LSSurface, 'pg_create_table')
    rgis.rdb.process_hecobject(heco.LateralStructures, 'pg_surface_points')

    # probe a DTM at each point
    QApplication.setOverrideCursor(Qt.WaitCursor)
    try:
        probe_DTMs(rgis, surface_obj, parent_obj, chunksize=chunk)
        rgis.addInfo('Done')
    finally:
        QApplication.restoreOverrideCursor()


def ras1dLatAll(rgis):
    ras1dLatRiverReachNames(rgis)
    ras1dLatStationing(rgis)
    ras1dLatElevations(rgis)


def ras1dSAElevations(rgis):
    """Probe a DTM to later find storage area volume"""
    # Prepare DTMs
    prepare_DTMs(rgis)
    if not rgis.dtms:
        rgis.addInfo('<br>No DTM for elevation sampling. Probing aborted!')
        return False
    surface_obj = heco.SASurface()
    parent_obj = heco.StorageAreas()
    update_DtmID(rgis, parent_obj)
    try:
        chunk = rgis.dtm_chunksize
    except:
        chunk = 0

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
    return True


def ras1dSAVolumeData(rgis):
    nr_slices, ok = QInputDialog.getInt(rgis, 'Number of slices', 'Number of slices for volume calculation:', 10, 3, 30, 1)
    if not ok:
        rgis.addInfo('  Incorrect number of slices. Cancelling...')
        return

    rgis.addInfo('<br><b>Calculating elevation-volume data for Storage Areas...</b>')
    rgis.rdb.process_hecobject(heco.SAVolume, 'pg_create_table')
    rgis.rdb.process_hecobject(heco.StorageAreas, 'pg_storage_calculator', slices=nr_slices)
    rgis.rdb.add_to_view(heco.SAVolume())
    rgis.addInfo('Done')


def ras1dSAAll(rgis):
    if ras1dSAElevations(rgis) is True:
        ras1dSAVolumeData(rgis)


def ras1dSACAssignNearestSA(rgis):
    rgis.addInfo('<br><b>Finding nearest Storage Areas for the connection...</b>')
    if rgis.rdb.process_hecobject(heco.SAConnections, 'pg_assign_nearest_sa'):
        rgis.addInfo('Done.')


def ras1dSACElevations(rgis):
    """Probe a DTM to find storage areas connections vertical shape"""
    # Prepare DTMs
    prepare_DTMs(rgis)
    if not rgis.dtms:
        rgis.addInfo('<br>No DTM for elevation sampling. Probing aborted!')
        return
    surface_obj = heco.SACSurface()
    parent_obj = heco.SAConnections()
    update_DtmID(rgis, parent_obj)
    try:
        chunk = rgis.dtm_chunksize
    except:
        chunk = 0

    # insert points along each sa connection
    rgis.rdb.process_hecobject(heco.SACSurface, 'pg_create_table')
    rgis.rdb.process_hecobject(heco.SAConnections, 'pg_surface_points')

    # probe a DTM at each point
    QApplication.setOverrideCursor(Qt.WaitCursor)
    try:
        probe_DTMs(rgis, surface_obj, parent_obj, chunksize=chunk)
        rgis.addInfo('Done')
    finally:
        QApplication.restoreOverrideCursor()


def ras1dSACAll(rgis):
    ras1dSACAssignNearestSA(rgis)
    ras1dSACElevations(rgis)


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
    last_dir = s.value('rivergis/lastRasGisImportDir', '')
    import_fname, __ = QFileDialog.getSaveFileName(None,
                     'Target HEC-RAS GIS Import file',
                     directory=last_dir,
                     filter='HEC-RAS GIS Import (*.sdf)')
    if not import_fname:
        rgis.addInfo('Creating RAS GIS Import file cancelled.')
        return

    s.setValue('rivergis/lastRasGisImportDir', os.path.dirname(import_fname))
    rgis.rdb.register.clear()
    rgis.rdb.register_existing(heco)
    rgi = RasGisImport(rgis)
    rgi.check_components()
    sdf = rgi.gis_import_file()
    if rgis.DEBUG:
        rgis.addInfo(sdf)
    with open(import_fname, 'w') as import_file:
        import_file.write(sdf)
    rgis.addInfo('Done.')
