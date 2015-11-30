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
from qgis.core import *
from qgis.utils import *
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from math import floor
from os.path import join, dirname, isfile
import processing
from time import sleep


def ras2dCreate2dPoints(rgis):
    """
    Create 2D computational points for each 2D flow area. 
    Points are regularly spaced (based on CellSize attribute of the FlowArea2D table) except for breaklines, where they are aligned to form a cell face exactly at a breakline.
    Points spacing along and across a breakline is read from CellSizeAlong and CellSizeAcross attributes of BreakLines2D table, respectively. A number of cells rows to align with a beakline can be given.
    Create breakpoints at locations where a cell face is needed (on a breakline).
    """
    rgis.addInfo("<br><b>Creating computational points for 2D flow areas<b>")

    # and create breaklines with a linear measure
    qry = '''
    SELECT * FROM "{0}"."FlowAreas2d"
    '''.format(rgis.rdb.SCHEMA)
    chk2dAreas = rgis.rdb.run_query(qry, fetch=True)
    if not chk2dAreas:
        rgis.addInfo("  No 2d flow area in the database.<br>  Import or create it before generating 2d computational points.<br>  Cancelling...")
        return

    QApplication.setOverrideCursor(Qt.WaitCursor)
    qry = '''CREATE OR REPLACE FUNCTION "{0}".makegrid(geometry, float, integer)
    RETURNS geometry AS
    'SELECT ST_Collect(st_setsrid(ST_POINT(x/1000000::float,y/1000000::float),$3)) FROM
      generate_series(floor(st_xmin($1)*1000000)::bigint, ceiling(st_xmax($1)*1000000)::bigint,($2*1000000)::bigint) as x,
      generate_series(floor(st_ymin($1)*1000000)::bigint, ceiling(st_ymax($1)*1000000)::bigint,($2*1000000)::bigint) as y
    where st_intersects($1,st_setsrid(ST_POINT(x/1000000::float,y/1000000::float),$3))'
    LANGUAGE sql;'''.format(rgis.rdb.SCHEMA)
    rgis.rdb.run_query(qry)

    rgis.addInfo("  Creating regular mesh points..." )

    # create regular mesh points
    # and delete points located too close to the 2D area boundary
    qry = '''
    DELETE FROM "{0}"."MeshPoints2d";
    INSERT INTO
        "{0}"."MeshPoints2d" ("AreaID", "BLID", geom)
    SELECT
        "AreaID",
        -1,
        (ST_Dump("{0}".makegrid(geom, "CellSize", {1}))).geom as geom
    FROM
        "{0}"."FlowAreas2d";

    WITH areas2dshrinked AS (
        SELECT
            "AreaID",
            ST_Buffer(a2d.geom, -0.3 * a2d."CellSize") as geom
        FROM
            "{0}"."FlowAreas2d" as a2d
    )
    DELETE FROM
       "{0}"."MeshPoints2d" as pts_a
    WHERE
        pts_a."MPID" NOT IN (
            SELECT
                pts."MPID"
            FROM
                "{0}"."MeshPoints2d" as pts,
                areas2dshrinked
            WHERE
                ST_Intersects(pts.geom, areas2dshrinked.geom)
            );
    '''.format(rgis.rdb.SCHEMA, rgis.rdb.SRID)
    rgis.rdb.run_query(qry)

    # find which breakline line belongs to which 2d flow area
    # and create breaklines with a linear measure
    qry = '''
    WITH ids as (
        SELECT
            a."AreaID",
            l."BLID"
        FROM
            "{0}"."BreakLines2d" l,
             "{0}"."FlowAreas2d" a
        WHERE
            a.geom && l.geom and
            ST_Contains(a.geom, l.geom)
    )
    UPDATE "{0}"."BreakLines2d" l
    SET
        "AreaID" = ids."AreaID"
    FROM
        ids
    WHERE ids."BLID" = l."BLID";

    DROP TABLE IF EXISTS "{0}"."BreakLines2d_m";
    CREATE TABLE "{0}"."BreakLines2d_m" (
        "BLmID" serial primary key,
        "AreaID" integer,
        "CellSizeAlong" double precision,
        "CellSizeAcross" double precision,
        "RowsAligned" integer,
        geom geometry(LINESTRINGM, {1})
    );

    INSERT INTO "{0}"."BreakLines2d_m" (
        "AreaID",
        "CellSizeAlong",
        "CellSizeAcross",
        "RowsAligned",
        geom
        )
    SELECT
        "AreaID",
        "CellSizeAlong",
        "CellSizeAcross",
        "RowsAligned",
        (ST_Dump(ST_AddMeasure(geom, 0, ST_Length(geom)))).geom
    FROM
        "{0}"."BreakLines2d";
    '''.format(rgis.rdb.SCHEMA, rgis.rdb.SRID)
    rgis.rdb.run_query(qry)

    qry = '''
    WITH brbuf AS (
    SELECT
        ST_Buffer(geom, "RowsAligned" * "CellSizeAcross" +
                    "CellSizeAlong" * 0.2, \'endcap=flat join=round\') as geom
    FROM
        "{0}"."BreakLines2d_m"
    )
    DELETE FROM
        "{0}"."MeshPoints2d" as p
    USING
        brbuf
    WHERE
        brbuf.geom && p.geom AND
        ST_Intersects(brbuf.geom, p.geom);
    '''.format(rgis.rdb.SCHEMA)
    rgis.rdb.run_query(qry)

    rgis.addInfo("  Creating mesh points along structures..." )

    # check if breaklines and breakpoints exist in the database
    bls_exist = False
    bps_exist = False
    # rgis.addInfo("  List of tables: {}".format(rgis.rdb.list_tables()) )
    for t in rgis.rdb.list_tables():
        if t[0] == 'BreakLines2d':
            bls_exist = True
        if t[0] == 'BreakPoints2d':
            bps_exist = True

    if bls_exist:

        # find measures of breakpoints along breaklines
        # there was a change in the alg name between PostGIS 2.0 and 2.1
        # ST_Line_Locate_Point -> ST_LineLocatePoint
        qry = "select PostGIS_Full_Version() as ver;"
        postgisVersion = rgis.rdb.run_query(qry, True)[0]['ver'].split('\"')[1][:5]
        pgMajV = int(postgisVersion[:1])
        pgMinV = int(postgisVersion[2:3])
        if pgMajV < 2:
            locate = "ST_Line_Locate_Point"
        elif pgMajV >= 2 and pgMinV == 0:
            locate = "ST_Line_Locate_Point"
        else:
            locate = "ST_LineLocatePoint"

        if bps_exist:
            # find breakline that a breakpoint is located on ( tolerance = 10 [map units] )
            breakPtsLocTol = 10
            qry = '''
            WITH ids AS (
                SELECT
                    b."BLmID",
                    p."BPID",
                    b."AreaID"
                FROM
                    "{0}"."BreakLines2d_m" b,
                    "{0}"."BreakPoints2d" p
                WHERE
                    ST_Buffer(p.geom, {1}) && b.geom and
                    ST_Contains(ST_Buffer(b.geom, {1}), p.geom)
            )
            UPDATE
                "{0}"."BreakPoints2d" p
            SET
                "BLmID" = ids."BLmID",
                "AreaID" = ids."AreaID"
            FROM
                ids
            WHERE
                ids."BPID" = p."BPID";
            '''.format(rgis.rdb.SCHEMA, breakPtsLocTol)
            rgis.rdb.run_query(qry)

            # find breakpoints measures along a breakline
            qry = '''
            UPDATE
                "{0}"."BreakPoints2d" p
            SET
                "Fraction" = {1}(b.geom, p.geom)
            FROM
                "{0}"."BreakLines2d_m" b
            WHERE
                p."BLmID" = b."BLmID";
            '''.format(rgis.rdb.SCHEMA, locate)
            rgis.rdb.run_query(qry)

        # find breaklines with measures
        qry = '''
        SELECT
            "BLmID",
            "AreaID",
            "CellSizeAlong" as csx,
            "CellSizeAcross" as csy,
            ST_Length(geom) as len,
            "RowsAligned" as rows
        from
            "{0}"."BreakLines2d_m";
        '''.format(rgis.rdb.SCHEMA)
        bls = rgis.rdb.run_query(qry, True)

        for line in bls:
            if not line['csx'] or not line['csy'] or not line['rows']:
                rgis.addInfo('<br><b>  Empty BreakLines2d attribute! Cancelling...<b><br>')
                QApplication.setOverrideCursor(Qt.ArrowCursor)
                return
            odl = float(line['csx'])
            szer = float(line['csy'])
            id = line['BLmID']
            leng = float(line['len'])
            rows = int(line['rows'])
            imax = int(leng/(odl))

            # check if breakpoints exist on the breakline
            qry = '''
            SELECT
                bp."BPID"
            FROM
                "{0}"."BreakLines2d_m" bl,
                "{0}"."BreakPoints2d" bp
            WHERE
                bl."BLmID" = {1} AND
                bp."BLmID" = bl."BLmID";
            '''.format(rgis.rdb.SCHEMA, id)
            bp_on_bl = rgis.rdb.run_query(qry, True)
            if rgis.DEBUG:
                rgis.addInfo("  Breakline BLmID={0}, {1}".format(id, bp_on_bl))

            if not bp_on_bl:
                # no BreakPoints2d: create aligned mesh at regular interval = CellSizeAlong
                if rgis.DEBUG:
                    rgis.addInfo("  Creating regular points for breakline BLmID=%i (no breakpoints)" % id )
                for i in range(0, imax+1):
                    dist = i * odl
                    for j in range(0,rows):
                        qry = '''
                        INSERT INTO
                            "{0}"."MeshPoints2d" ("BLID", "AreaID", "CellSize", geom)
                        SELECT
                            "BLmID",
                            "AreaID",
                            {1},
                            ST_Centroid(ST_LocateAlong(geom, {2}, {3}))
                        FROM
                            "{0}"."BreakLines2d_m"
                        WHERE
                            "BLmID" = {4};

                        INSERT INTO
                            "{0}"."MeshPoints2d" ("BLID", "AreaID", "CellSize", geom)
                        SELECT
                            "BLmID",
                            "AreaID",
                            {1},
                            ST_Centroid(ST_LocateAlong(geom, {2}, -{3}))
                        FROM
                            "{0}"."BreakLines2d_m"
                        WHERE
                            "BLmID" = {4};
                        '''.format(rgis.rdb.SCHEMA, odl, dist, j*szer+szer/2, id)
                        rgis.rdb.run_query(qry)

            else: # create cell faces at breakline's breakpoints
                qry = '''
                SELECT DISTINCT
                    p."Fraction"
                FROM
                    "{0}"."BreakPoints2d" p
                WHERE
                    p."BLmID" = {1};
                '''.format(rgis.rdb.SCHEMA, id)
                ms = rgis.rdb.run_query(qry, True)

                if rgis.DEBUG:
                    rgis.addInfo("  Creating breakpoints for structure id=%i (with breakpoints)" % id )
                sm_param = 4
                db_min = 10.**9
                bm = [] # breakpoints m list (linear locations on current structure)
                mpts = [] # linear measures of mesh points to be created

                for m in ms:
                    bm.append(float(m['Fraction']))
                    if rgis.DEBUG:
                        rgis.addInfo('  BreakPoint2d fraction: {}'.format(float(m['Fraction'])))

                # sort the list
                bm.sort()

                for i, m in enumerate(bm):
                    # calculate minimal distance between breakpoints
                    if i > 0:
                        db_min = min( bm[i] - bm[i-1], db_min)
                if rgis.DEBUG:
                    rgis.addInfo('  Min dist between breakpoints db_min={}'.format(db_min))
                # create 2 mesh points on both sides of a breakpoint at a distance db_min / sm_param
                dist_min = min( db_min / sm_param, 0.5 * odl / leng )
                cs_min = dist_min * leng
                if rgis.DEBUG:
                    rgis.addInfo('  dist_min={}, cs_min={}'.format(dist_min, cs_min))
                for m in bm:
                    mpts.append(max(0.0001, m - dist_min))
                    mpts.append(min(m + dist_min, 0.9999))

                # find gaps between points along a breakline longer than 3 * dist_min
                gaps = []
                for i, m in enumerate(mpts):
                    if rgis.DEBUG:
                        rgis.addInfo('  m={}'.format(m))
                    if i > 0:
                        dist = m - mpts[i-1]
                        if dist > 3 * dist_min:
                            gaps.append([m,dist])

                # create mesh points filling the gaps
                for g in gaps:
                    m, dist = g
                    # how many points to insert?
                    k = int(floor(dist / (2*dist_min)))
                    # distance between new points
                    cs = dist / k
                    for j in range(1,k):
                        mpts.append(m - j * cs)
                        if rgis.DEBUG:
                            rgis.addInfo('gap: dist={}, m={}'.format(cs, m - j * cs))

                # insert aligned mesh points into table
                for m in sorted(mpts):
                    for j in range(0, rows):
                        qry = '''
                        INSERT INTO
                            "{0}"."MeshPoints2d" ("BLID", "AreaID", "CellSize", geom)
                        SELECT
                            "BLmID",
                            "AreaID",
                            {1},
                            ST_Centroid(ST_LocateAlong(geom, {2}, {3}))
                        FROM
                            "{0}"."BreakLines2d_m"
                        WHERE
                            "BLmID" = {4};

                        INSERT INTO
                            "{0}"."MeshPoints2d" ("BLID", "AreaID", "CellSize", geom)
                        SELECT
                            "BLmID",
                            "AreaID",
                            {1},
                            ST_Centroid(ST_LocateAlong(geom, {2}, -{3}))
                        FROM
                            "{0}"."BreakLines2d_m"
                        WHERE
                            "BLmID" = {4};
                        '''.format(rgis.rdb.SCHEMA, cs_min, m*leng, j*szer+szer/2, id)
                        rgis.rdb.run_query(qry)

    rgis.addInfo("  Deleting mesh points located too close to each other or outside the 2D area..." )

    qry = '''
    DELETE FROM
        "{0}"."MeshPoints2d" p1
    USING
        "{0}"."MeshPoints2d" p2
    WHERE
        p1."BLID" <> -1 AND
        p2."BLID" <> -1 AND
        p1."BLID" <> p2."BLID" AND
        p1."MPID" > p2."MPID" AND
        ST_DWithin(p1.geom, p2.geom, 0.75 * LEAST(p1."CellSize", p2."CellSize"));

    DELETE FROM
        "{0}"."MeshPoints2d" p
    USING
        "{0}"."FlowAreas2d" as a
    WHERE
        a."AreaID" = p."AreaID" AND
        NOT ST_Contains(ST_Buffer(a.geom,-0.3*a."CellSize"), p.geom );
    '''.format(rgis.rdb.SCHEMA)
    rgis.rdb.run_query(qry)
    rgis.addInfo('Done')

    QApplication.setOverrideCursor(Qt.ArrowCursor)


def ras2dPreviewMesh(rgis):
    """Loads the mesh points to the canvas and builds Voronoi polygons"""
    areas = None
    u1 = QgsDataSourceURI()
    u1.setConnection(rgis.host, rgis.port, rgis.database, rgis.user, rgis.passwd)
    u1.setDataSource(rgis.schema, "MeshPoints2d", "geom")
    mesh_pts = QgsVectorLayer(u1.uri(), "MeshPoints2d", "postgres")
    voronoi = processing.runalg("qgis:voronoipolygons",mesh_pts,3,None)
    # QgsMapLayerRegistry.instance().addMapLayers([mesh_pts])

    # try to load the 2D Area polygon and clip the Voronoi diagram
    try:
        u2 = QgsDataSourceURI()
        u2.setConnection(rgis.host, rgis.port, rgis.database, rgis.user, rgis.passwd)
        u2.setDataSource(rgis.schema, "FlowAreas2d", "geom")
        areas = QgsVectorLayer(u2.uri(), "FlowAreas2d", "postgres")
        if rgis.DEBUG:
            rgis.addInfo('Voronoi layer: \n{0}\nFlow Areas 2d layer ok? {1}'.format( \
                voronoi['OUTPUT'], areas.isValid()))
        # TODO: construct voronoi polygons separately for each 2d mesh area
        voronoiClip = processing.runalg("qgis:clip",voronoi['OUTPUT'],areas,None)
        if rgis.DEBUG:
            rgis.addInfo('Cutted Voronoi polygons:\n{0}'.format(voronoiClip['OUTPUT']))
        sleep(1)
        voronoiClipLayer = QgsVectorLayer(voronoiClip['OUTPUT'], "Mesh preview", "ogr")
        QgsMapLayerRegistry.instance().addMapLayers([voronoiClipLayer])

    except:
        voronoiLayer = QgsVectorLayer(voronoi['OUTPUT'], "Mesh preview", "ogr")
        QgsMapLayerRegistry.instance().addMapLayers([voronoiLayer])

    # change layers' style
    root = QgsProject.instance().layerTreeRoot()
    legItems = root.findLayers()
    for item in legItems:
        if item.layerName() == 'Mesh preview':
            stylePath = join(rgis.rivergisPath,'styles/Mesh2d.qml')
            item.layer().loadNamedStyle(stylePath)
            rgis.iface.legendInterface().refreshLayerSymbology(item.layer())
            rgis.iface.mapCanvas().refresh()


def ras2dSaveMeshPtsToGeometry(rgis,geoFileName=None):
    """Saves mesh points from current schema and table 'mesh_pts' to HEC-RAS geometry file"""
    if not geoFileName:
        s = QSettings()
        lastGeoFileDir = s.value("rivergis/lastGeoDir", "")
        geoFileName = QFileDialog.getSaveFileName(None, 'Target HEC-RAS geometry file', directory=lastGeoFileDir, filter='HEC-RAS geometry (*.g**)')
        if not geoFileName:
            return
        s.setValue("rivergis/lastGeoDir", dirname(geoFileName))

    rgis.addInfo("<br><b>Saving 2D Flow Area to HEC-RAS geometry file...</b>")

    # get mesh points extent
    qry = '''
    SELECT
        ST_XMin(ST_Collect(geom)) as xmin,
        ST_XMax(ST_collect(geom)) as xmax,
        ST_YMin(ST_collect(geom)) as ymin,
        ST_YMax(ST_collect(geom)) as ymax
    FROM
        "{0}"."MeshPoints2d";
    '''.format(rgis.rdb.SCHEMA)
    pExt = rgis.rdb.run_query(qry, True)[0]
    xmin, xmax, ymin, ymax = [pExt['xmin'], pExt['xmax'], pExt['ymin'], pExt['ymax']]
    buf = max(0.2*(xmax-xmin), 0.2*(ymax-ymin))
    pExtStr = '{:.2f}, {:.2f}, {:.2f}, {:.2f}'.format(xmin-buf, xmax+buf, ymax+buf, ymin-buf)

    # get list of mesh areas
    qry = '''
    SELECT
        "AreaID",
        "Name",
        ST_X(ST_Centroid(geom)) as x,
        ST_Y(ST_Centroid(geom)) as y,
        ST_NPoints(geom) as ptsnr
    FROM "{0}"."FlowAreas2d";
    '''.format(rgis.rdb.SCHEMA)
    t = ''

    for area in rgis.rdb.run_query(qry, True):
        qry = '''
        SELECT ST_AsText(geom) as geom
        FROM
            "{0}"."FlowAreas2d"
        WHERE
            "AreaID"={1};
        '''.format(rgis.rdb.SCHEMA, area['AreaID'])
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
            ST_X(geom) as x,
            ST_Y(geom) as y
        FROM
            "{0}"."MeshPoints2d"
        WHERE
            "AreaID" = {1};
        '''.format(rgis.schema, area['AreaID'])
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

    if not isfile(geoFileName):
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
