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

def ras1dTopology(rgis):
    """Creates river network topology. Creates nodes at reach ends and finds the direction of flow (fromNode, toNode)"""
    # check if streamlines table is registered
    scExist = 'StreamCenterlines' in rgis.rdb.register.keys()
    if not scExist:
        rgis.addInfo('<br>StreamCenterlines are not registered in the river database. Cancelling...')
        return

    rgis.addInfo('<br><b>Building topology on StreamCenterlines...</b>')
    if rgis.rdb.process_hecobject(heco.StreamCenterlines, 'pg_topology'):
        rgis.addInfo('Done.')


def ras1dLengthsStations(rgis):
    """Calculate river reaches lenght and their endpoints stations"""

    # check if streamlines table is registered
    # TODO: czy bedziemy rejestrowac tabele Endpoints, NodesTable jako obiekty bazy?
    # zeby mozna je bylo traktowac jak inne tabele, np.?
    # ntExist = 'NodesTable' in rgis.rdb.register.keys()
    schema_tables = rgis.rdb.list_tables()
    ntExist = 'NodesTable' in [t[0] for t in rgis.rdb.list_tables()]
    if not ntExist:
        rgis.addInfo('<br>NodesTable is not registered in the river database.<br>Build StreamCenterlines Topology first.<br>Cancelling...')
        return

    rgis.addInfo('<br><b>Calculating river reach(es) lenghts and their end stations...</b>')
    if rgis.rdb.process_hecobject(heco.StreamCenterlines, 'pg_lengths_stations'):
        rgis.addInfo('Done.')


def ras1dCenterlineElevations(rgis):
    """Finds rivers' centerline elevations"""
    # Ta czynnosc wydaje sie zbedna - HEC-RAS nie potrzebuje profilu wysokosciowego rzeki
    pass


def ras1dStreamCenterlineAll(rgis):
    """Runs all analyses for rivers' centerlines"""
    pass


def ras1dXSRiverReachNames(rgis):
    """Finds river and reach name for each cross-section"""
    pass


def ras1dXSStationing(rgis):
    """Finds cross-sections' stationing (chainages) along its river reach"""
    pass


def ras1dXSBankStations(rgis):
    """Finds banks stations for each cross-section. Based on intersection of bank and xs lines"""
    pass


def ras1dXSDownstreamLengths(rgis):
    """Calculates downstream reach lengths from each cross-section along the 3 flow paths (channel, left and right overbank)"""
    pass


def ras1dXSElevations(rgis):
    """RProbes a DEM to find cross-section vertical shape"""
    pass


def ras1dXSAll(rgis):
    """Runs all the XS analyses"""
    pass


