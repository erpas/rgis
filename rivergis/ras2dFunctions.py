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
from builtins import range
import os

from . import hecobjects as heco
from qgis.core import QgsDataSourceUri, QgsVectorLayer, QgsProject, QgsFeature, QgsGeometry
from qgis.PyQt.QtCore import QSettings, Qt
from qgis.PyQt.QtWidgets import QApplication, QFileDialog
from math import floor
from psycopg2 import ProgrammingError


def ras2dCreate2dPoints(rgis):
    """
    Create 2D computational points for each 2D flow area.
    Points are regularly spaced (based on CellSize attribute of the FlowArea2D table) except for breaklines, where they are aligned to form a cell face exactly at a breakline.
    Points spacing along and across a breakline is read from CellSizeAlong and CellSizeAcross attributes of BreakLines2D table, respectively. A number of cells rows to align with a beakline can be given.
    Create breakpoints at locations where a cell face is needed (on a breakline).
    """
    rgis.addInfo('<br><b>Creating computational points for 2D flow areas<b>')

    # and create breaklines with a linear measure
    qry = 'SELECT * FROM "{0}"."FlowAreas2d"'.format(rgis.rdb.SCHEMA)
    chk2dAreas = rgis.rdb.run_query(qry, fetch=True)
    if not chk2dAreas:
        rgis.addInfo('No 2d flow area in the database.<br>  Import or create it before generating 2d computational points.<br>  Cancelling...')
        return

    QApplication.setOverrideCursor(Qt.WaitCursor)
    rgis.addInfo('Creating regular mesh points...')

    # create regular mesh points
    # and delete points located too close to the 2D area boundary
    rgis.rdb.process_hecobject(heco.MeshPoints2d, 'pg_create_table')
    rgis.rdb.process_hecobject(heco.MeshPoints2d, 'pg_create_mesh')

    # find which breakline line belongs to which 2d flow area
    # and create breaklines with a linear measure
    rgis.rdb.process_hecobject(heco.BreakLines2d, 'pg_flow_to_breakline')
    rgis.rdb.process_hecobject(heco.BreakLines2d, 'pg_breaklines_m')
    rgis.rdb.process_hecobject(heco.BreakLines2d, 'pg_drop_by_buffer')

    rgis.addInfo('Creating mesh points along structures...')

    # check if breaklines and breakpoints exist in the database
    bls_exist = False
    bps_exist = False
    for t in rgis.rdb.list_tables():
        if t == 'BreakLines2d':
            bls_exist = True
        if t == 'BreakPoints2d':
            bps_exist = True

    if bls_exist:
        # find measures of breakpoints along breaklines
        # there was a change in the alg name between PostGIS 2.0 and 2.1
        # ST_Line_Locate_Point -> ST_LineLocatePoint
        qry = 'SELECT PostGIS_Full_Version() AS ver;'
        postgisVersion = rgis.rdb.run_query(qry, True)[0]['ver'].split('\"')[1][:5]
        pgMajV = int(postgisVersion[:1])
        pgMinV = int(postgisVersion[2:3])
        if pgMajV < 2:
            locate = 'ST_Line_Locate_Point'
        elif pgMajV >= 2 and pgMinV == 0:
            locate = 'ST_Line_Locate_Point'
        else:
            locate = 'ST_LineLocatePoint'

        # find breakline that a breakpoint is located on ( tolerance = 10 [map units] )
        if bps_exist:
            breakPtsLocTol = 10
            rgis.rdb.process_hecobject(heco.BreakPoints2d, 'pg_bpoints_along_blines', tolerance=breakPtsLocTol, func_name=locate)
        # find breaklines with measures
        qry = '''
        SELECT
            "BLmID",
            "AreaID",
            "CellSizeAlong" AS csx,
            "CellSizeAcross" AS csy,
            ST_Length(geom) AS len,
            "RowsAligned" AS rows
        FROM
            "{0}"."BreakLines2d_m";
        '''
        qry = qry.format(rgis.rdb.SCHEMA)
        bls = rgis.rdb.run_query(qry, True)

        for line in bls:
            if not line['csx'] or not line['csy'] or not line['rows']:
                rgis.addInfo('<br><b>  Empty BreakLines2d attribute! Cancelling...<b><br>')
                QApplication.restoreOverrideCursor()
                return
            dist_x = float(line['csx'])
            width = float(line['csy'])
            id = line['BLmID']
            leng = float(line['len'])
            rows = int(line['rows'])
            imax = int(leng/(dist_x))

            # check if breakpoints exist on the breakline
            qry = '''
            SELECT
                bp."BPID"
            FROM
                "{0}"."BreakLines2d_m" AS bl,
                "{0}"."BreakPoints2d" AS bp
            WHERE
                bl."BLmID" = {1} AND
                bp."BLmID" = bl."BLmID";
            '''
            try:
                qry = qry.format(rgis.rdb.SCHEMA, id)
                bp_on_bl = rgis.rdb.run_query(qry, True)
                if rgis.DEBUG:
                    rgis.addInfo('Breakline BLmID={0}, {1}'.format(id, bp_on_bl))
            except ProgrammingError:
                bp_on_bl = None

            if not bp_on_bl:
                # no BreakPoints2d: create aligned mesh at regular interval = CellSizeAlong
                if rgis.DEBUG:
                    rgis.addInfo('Creating regular points for breakline BLmID={0} (no breakpoints)'.format(id))
                for i in range(0, imax+1):
                    dist = i * dist_x
                    for j in range(0, rows):
                        rgis.rdb.process_hecobject(heco.MeshPoints2d, 'pg_aligned_mesh', cellsize=dist_x, measure=dist, offset=j*width+width/2, blid=id)

            # create cell faces at breakline's breakpoints
            else:
                qry = '''
                SELECT DISTINCT
                    p."Fraction"
                FROM
                    "{0}"."BreakPoints2d" AS p
                WHERE
                    p."BLmID" = {1};
                '''
                qry = qry.format(rgis.rdb.SCHEMA, id)
                ms = rgis.rdb.run_query(qry, True)

                if rgis.DEBUG:
                    rgis.addInfo('Creating breakpoints for structure id={0} (with breakpoints)'.format(id))
                sm_param = 4
                db_min = 10.**9
                # breakpoints m list (linear locations on current structure)
                bm = []
                # linear measures of mesh points to be created
                mpts = []

                for m in ms:
                    bm.append(float(m['Fraction']))
                    if rgis.DEBUG:
                        rgis.addInfo('BreakPoint2d fraction: {0}'.format(float(m['Fraction'])))

                # sort the list
                bm.sort()

                for i, m in enumerate(bm):
                    # calculate minimal distance between breakpoints
                    if i > 0:
                        db_min = min(bm[i] - bm[i-1], db_min)
                if rgis.DEBUG:
                    rgis.addInfo('Min dist between breakpoints db_min={0}'.format(db_min))
                # create 2 mesh points on both sides of a breakpoint at a distance db_min / sm_param
                dist_min = min(db_min / sm_param, 0.5 * dist_x / leng)
                cs_min = dist_min * leng
                if rgis.DEBUG:
                    rgis.addInfo('dist_min={0}, cs_min={1}'.format(dist_min, cs_min))
                for m in bm:
                    mpts.append(max(0.0001, m - dist_min))
                    mpts.append(min(m + dist_min, 0.9999))

                # find gaps between points along a breakline longer than 3 * dist_min
                gaps = []
                for i, m in enumerate(mpts):
                    if rgis.DEBUG:
                        rgis.addInfo('m={0}'.format(m))
                    if i > 0:
                        dist = m - mpts[i-1]
                        if dist > 3 * dist_min:
                            gaps.append([m, dist])

                # create mesh points filling the gaps
                for g in gaps:
                    m, dist = g
                    # how many points to insert?
                    k = int(floor(dist / (2*dist_min)))
                    # distance between new points
                    cs = dist / k
                    for j in range(1, k):
                        mpts.append(m - j * cs)
                        if rgis.DEBUG:
                            rgis.addInfo('gap: dist={0}, m={1}'.format(cs, m - j * cs))

                # insert aligned mesh points into table
                for m in sorted(mpts):
                    for j in range(0, rows):
                        rgis.rdb.process_hecobject(heco.MeshPoints2d, 'pg_aligned_mesh', cellsize=cs_min, measure=m*leng, offset=j*width+width/2, blid=id)

    rgis.addInfo('Deleting mesh points located too close to each other or outside the 2D area...')
    rgis.rdb.process_hecobject(heco.MeshPoints2d, 'pg_clean_points')
    rgis.addInfo('Done')

    QApplication.restoreOverrideCursor()


def ras2dPreviewMesh(rgis):
    """Build and load Voronoi polygons for the mesh points"""
    u1 = QgsDataSourceUri()
    u1.setConnection(rgis.host, rgis.port, rgis.database, rgis.user, rgis.passwd)
    u1.setDataSource(rgis.schema, 'MeshPoints2d', 'geom')
    mesh_pts = QgsVectorLayer(u1.uri(), 'MeshPoints2d', 'postgres')
    u2 = QgsDataSourceUri()
    u2.setConnection(rgis.host, rgis.port, rgis.database, rgis.user, rgis.passwd)
    u2.setDataSource(rgis.schema, 'FlowAreas2d', 'geom')
    areas = QgsVectorLayer(u2.uri(), 'FlowAreas2d', 'postgres')

    pts_list = []
    for pt in mesh_pts.getFeatures():
        pts_list.append(pt.geometry())
    multipts = QgsGeometry().unaryUnion(pts_list)

    voronoi = multipts.voronoiDiagram()
    voronoi_lyr = QgsVectorLayer('Polygon?crs=proj4:{}'.format(rgis.crs.toProj4()), 'Mesh preview', 'memory')
    voronoi_dp = voronoi_lyr.dataProvider()

    new_feats = []
    for area in areas.getFeatures():
        for item in voronoi.asGeometryCollection():
            poly = QgsGeometry.fromPolygonXY(item.asPolygon())
            poly_cut = poly.intersection(area.geometry())
            fet = QgsFeature()
            fet.setGeometry(poly_cut)
            new_feats.append(fet)

    _ = voronoi_dp.addFeatures(new_feats)

    QgsProject.instance().addMapLayer(voronoi_lyr)

    # change layers' style
    root = QgsProject.instance().layerTreeRoot()
    leg_items = root.findLayers()
    for item in leg_items:
        if item.name() == 'Mesh preview':
            style_path = os.path.join(rgis.rivergisPath, 'styles/Mesh2d.qml')
            item.layer().loadNamedStyle(style_path)


def ras2dSaveMeshPtsToGeometry(rgis, geoFileName=None):
    """Saves mesh points from current schema and table 'mesh_pts' to HEC-RAS geometry file"""
    if not geoFileName:
        s = QSettings()
        lastGeoFileDir = s.value('rivergis/lastGeoDir', '')
        geoFileName, __ = QFileDialog.getSaveFileName(None, 'Target HEC-RAS geometry file', directory=lastGeoFileDir, filter='HEC-RAS geometry (*.g**)')
        if not geoFileName:
            return
        s.setValue('rivergis/lastGeoDir', os.path.dirname(geoFileName))

    rgis.addInfo('<br><b>Saving 2D Flow Area to HEC-RAS geometry file...</b>')

    # get mesh points extent
    qry = '''
    SELECT
        ST_XMin(ST_Collect(geom)) AS xmin,
        ST_XMax(ST_collect(geom)) AS xmax,
        ST_YMin(ST_collect(geom)) AS ymin,
        ST_YMax(ST_collect(geom)) AS ymax
    FROM
        "{0}"."MeshPoints2d";
    '''
    qry = qry.format(rgis.rdb.SCHEMA)
    pExt = rgis.rdb.run_query(qry, True)[0]
    xmin, xmax, ymin, ymax = [pExt['xmin'], pExt['xmax'], pExt['ymin'], pExt['ymax']]
    buf = max(0.2*(xmax-xmin), 0.2*(ymax-ymin))
    pExtStr = '{:.2f}, {:.2f}, {:.2f}, {:.2f}'.format(xmin-buf, xmax+buf, ymax+buf, ymin-buf)

    # get list of mesh areas
    qry = '''
    SELECT
        "AreaID",
        "Name",
        ST_X(ST_Centroid(geom)) AS x,
        ST_Y(ST_Centroid(geom)) AS y,
        ST_NPoints(geom) AS ptsnr
    FROM
        "{0}"."FlowAreas2d";
    '''
    qry = qry.format(rgis.rdb.SCHEMA)
    t = ''

    for area in rgis.rdb.run_query(qry, True):
        qry = '''
        SELECT
            ST_AsText(geom) AS geom
        FROM
            "{0}"."FlowAreas2d"
        WHERE
            "AreaID" = {1};
        '''
        qry = qry.format(rgis.rdb.SCHEMA, area['AreaID'])
        res = rgis.rdb.run_query(qry, True)[0]['geom']
        ptsList = res[9:-2].split(',')
        ptsTxt = ''
        for pt in ptsList:
            x, y = [float(c) for c in pt.split(' ')]
            ptsTxt += '{:>16.4f}{:>16.4f}\n'.format(x, y)
        t += '''

Storage Area={0:<14},{1:14},{2:14}
Storage Area Surface Line= {3:d}
{4}
Storage Area Type= 0
Storage Area Area=
Storage Area Min Elev=
Storage Area Is2D=-1
Storage Area Point Generation Data=,,,
'''.format(area['Name'], area['x'], area['y'], area['ptsnr'], ptsTxt)

        qry = '''
        SELECT
            ST_X(geom) AS x,
            ST_Y(geom) AS y
        FROM
            "{0}"."MeshPoints2d"
        WHERE
            "AreaID" = {1};
        '''
        qry = qry.format(rgis.schema, area['AreaID'])
        pkty = rgis.rdb.run_query(qry, True)

        coords = ''
        for i, pt in enumerate(pkty):
            if i % 2 == 0:
                coords += '{:16.2f}{:16.2f}'.format(float(pt['x']), float(pt['y']))
            else:
                coords += '{:16.2f}{:16.2f}\n'.format(float(pt['x']), float(pt['y']))

        t += '''Storage Area 2D Points= {0}
{1}
Storage Area 2D PointsPerimeterTime=25Jan2015 01:00:00
Storage Area Mannings=0.06
2D Cell Volume Filter Tolerance=0.003
2D Face Profile Filter Tolerance=0.003
2D Face Area Elevation Profile Filter Tolerance=0.003
2D Face Area Elevation Conveyance Ratio=0.02

'''.format(len(pkty), coords)

    if not os.path.isfile(geoFileName):
        createNewGeometry(geoFileName, pExtStr)

    geoFile = open(geoFileName, 'r')
    geoLines = geoFile.readlines()
    geoFile.close()

    geoFile = open(geoFileName, 'w')
    geo = ""
    for line in geoLines:
        if not line.startswith('Chan Stop Cuts'):
            geo += line
        else:
            geo += t
            geo += line
    geoFile.write(geo)
    geoFile.close()

    rgis.addInfo('Saved to:\n{}'.format(geoFileName))


def createNewGeometry(filename, extent):
    t = '''Geom Title=Import from RiverGIS
Program Version=5.00
Viewing Rectangle= {0}


Chan Stop Cuts=-1



Use User Specified Reach Order=0
GIS Ratio Cuts To Invert=-1
GIS Limit At Bridges=0
Composite Channel Slope=5
'''.format(extent)
    geoFile = open(filename, 'w')
    geoFile.write(t)
    geoFile.close()
