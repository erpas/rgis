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
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from math import floor



def ras2dCreate2dPoints(rgis):
    """
    Create 2D computational points for each 2D flow area. 
    Points are regularly spaced (based on CellSize attribute of the FlowArea2D table) except for breaklines, where they are aligned to form a cell face exactly at a breakline.
    Points spacing along and across a breakline is read from CellSizeAlong and CellSizeAcross attributes of BreakLines2D table, respectively. A number of cells rows to align with a beakline can be given.
    Create breakpoints at locations where a cell face is needed (on a breakline).
    """
    rgis.addInfo("<br><b>Creating computational points for 2D flow areas<b>" )
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
    INSERT INTO
        "{0}"."MeshPoints2d" ("AreaID", "BLID", geom)
    SELECT
        "AreaID",
        -1,
        (ST_Dump(makegrid(geom, "CellSize", {1}))).geom as geom
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
                pts.geom && areas2dshrinked.geom AND
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
                    "CellSizeAlong" * 0.6, \'endcap=flat join=round\') as geom
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

    # find breakline that a breakpoint is located on ( tolerance = 10 [map units] )
    breakPtsLocTol = 10
    qry = '''
    WITH ids AS (
        SELECT
            b."BLID",
            p."BPID",
            b."AreaID"
        FROM
            "{0}"."BreakLines2d" b,
            "{0}"."BreakPoints2d" p
        WHERE
            ST_Buffer(p.geom, {1}) && b.geom and
            ST_Contains(ST_Buffer(b.geom, {1}), p.geom)
    )
    UPDATE
        "{0}"."BreakPoints2d" p
    SET
        "BLID" = ids."BLID",
        "AreaID" = ids."AreaID"
    FROM
        ids
    WHERE
        ids."BPID" = p."BPID";
    '''.format(rgis.rdb.SCHEMA, breakPtsLocTol)
    rgis.rdb.run_query(qry)

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
    qry = '''
    UPDATE
        "{0}"."BreakPoints2d" p
    SET
        "Fraction" = {1}(b.geom, p.geom)
    FROM
        "{0}"."BreakLines2d" b
    WHERE
        p."BLID" = b."BLID";
    '''.format(rgis.rdb.SCHEMA, locate)
    rgis.rdb.run_query(qry)

    rgis.addInfo("  Creating aligned mesh points along structures..." )

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

    if bls:
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

            qry = '''
            SELECT DISTINCT
                p."Fraction"
            FROM
                "{0}"."BreakPoints2d" p,
                "{0}"."BreakLines2d" l
            WHERE
                p."BLID" = {1};
            '''.format(rgis.rdb.SCHEMA, id)
            ms = rgis.rdb.run_query(qry, True)

            if not ms:
                # no BreakPoints2d: create aligned mesh at regular interval = CellSizeAlong
                if rgis.DEBUG:
                    rgis.addInfo("  Creating regular points for structure id=%i (no breakpoints)" % id )
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
                    for j in range(0,k):
                        mpts.append(m - j * cs)

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

                        # qry = 'insert into %s.mesh_pts (lid, aid, cellsize, geom) select gid, aid, %.2f, ST_Centroid(ST_LocateAlong(geom, %.2f, %.2f)) from  %s."Breaklines_m" where gid = %i;\n' % (rgis.rdb.SCHEMA, cs_min, m*leng, j*odl+odl/2, rgis.rdb.SCHEMA, id)
                        # qry += 'insert into %s.mesh_pts (lid, aid, cellsize, geom) select gid, aid, %.2f, ST_Centroid(ST_LocateAlong(geom, %.2f, -%.2f)) from %s."Breaklines_m" where gid = %i;' % (rgis.rdb.SCHEMA, cs_min, m*leng, j*odl+odl/2, rgis.rdb.SCHEMA, id)
                        # rgis.rdb.run_query(qry)

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
        NOT ST_Contains(ST_Buffer(a.geom,-0.3*a."CellSize"), p.geom );
    '''.format(rgis.rdb.SCHEMA)
    rgis.rdb.run_query(qry)
    rgis.addInfo('Done')

    QApplication.setOverrideCursor(Qt.ArrowCursor)
