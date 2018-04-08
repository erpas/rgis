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
from builtins import object


class HecRasObject(object):
    """
    Class for HEC-RAS geometry objects processing.
    """
    SCHEMA = None
    SRID = None
    OVERWRITE = None

    def __init__(self):
        self.order = 0
        self.main = True
        self.visible = True
        self.spatial_index = True
        self.schema = self.SCHEMA
        self.srid = self.SRID
        self.overwrite = self.OVERWRITE
        self.name = self.__class__.__name__
        self.geom_type = None
        self.attrs = None

    def pg_create_table(self):
        schema_name = '"{0}"."{1}"'.format(self.schema, self.name)
        if self.geom_type is not None:
            attrs = ['geom geometry({0}, {1})'.format(self.geom_type, self.srid)]
        else:
            attrs = []
        attrs += [' '.join(field) for field in self.attrs]
        if self.overwrite is True:
            qry = 'DROP TABLE IF EXISTS {0};\nCREATE TABLE {0}(\n\t{1});\n'.format(schema_name, ',\n\t'.join(attrs))
        else:
            qry = 'CREATE TABLE {0}(\n\t{1});\n'.format(schema_name, ',\n\t'.join(attrs))
        if self.spatial_index is True:
            qry += 'SELECT "{0}".create_spatial_index(\'{0}\', \'{1}\');'.format(self.schema, self.name)
        else:
            pass
        return qry


class StreamCenterlines(HecRasObject):
    def __init__(self):
        super(StreamCenterlines, self).__init__()
        self.order = 6
        self.geom_type = 'LINESTRING'
        self.attrs = [
            ('"ReachID"', 'serial primary key'),
            ('"RiverCode"', 'text'),
            ('"ReachCode"', 'text'),
            ('"FromNode"', 'integer'),
            ('"ToNode"', 'integer'),
            ('"ReachLen"', 'double precision'),
            ('"FromSta"', 'double precision'),
            ('"ToSta"', 'double precision'),
            ('"Notes"', 'text')]

    def pg_topology(self):
        qry = '''
CREATE OR REPLACE FUNCTION "{0}".from_to_node ()
    RETURNS VOID AS
$BODY$
DECLARE
    c cursor FOR SELECT * FROM "{0}"."StreamCenterlines";
    r "{0}"."StreamCenterlines"%ROWTYPE;
    start_geom geometry;
    end_geom geometry;
    start_node integer := 0;
    end_node integer := 0;
    nr integer := 0;
BEGIN
FOR r IN c LOOP
    start_geom := ST_StartPoint(r.geom);
    end_geom := ST_EndPoint(r.geom);
    IF (SELECT exists (SELECT 1 FROM "{0}"."NodesTable" WHERE geom = start_geom LIMIT 1)) THEN
        start_node := (SELECT "NodeID" FROM "{0}"."NodesTable" WHERE geom = start_geom LIMIT 1);
    ELSE
        nr := nr + 1;
        start_node := nr;
        INSERT INTO "{0}"."NodesTable" VALUES (start_geom, nr, ST_X(start_geom), ST_Y(start_geom));
    END IF;
    IF (SELECT exists (SELECT 1 FROM "{0}"."NodesTable" WHERE geom = end_geom LIMIT 1)) THEN
        end_node := (SELECT "NodeID" FROM "{0}"."NodesTable" WHERE geom = end_geom LIMIT 1);
    ELSE
        nr := nr + 1;
        end_node := nr;
        INSERT INTO "{0}"."NodesTable" VALUES (end_geom, nr, ST_X(end_geom), ST_Y(end_geom));
    END IF;
    UPDATE
        "{0}"."StreamCenterlines"
    SET
        "FromNode" = start_node,
        "ToNode" = end_node
    WHERE CURRENT OF c;
END LOOP;
END;
$BODY$
    LANGUAGE plpgsql;
------------------------------------------------------------------------------------------------------------------------
SELECT "{0}".from_to_node ();
DROP FUNCTION IF EXISTS "{0}".from_to_node ();
'''
        qry = qry.format(self.schema)
        return qry

    def pg_lengths_stations(self):
        qry = '''
WITH all_nodes AS
    (SELECT
        "RiverCode",
        "ReachCode",
        ST_StartPoint(geom) AS geom,
        'start' AS point_type
    FROM
        "{0}"."StreamCenterlines"
    UNION ALL
    SELECT
        "RiverCode",
        "ReachCode",
        ST_EndPoint(geom) AS geom,
        'end' AS point_type
    FROM
        "{0}"."StreamCenterlines"),
    single_nodes AS
    (SELECT
        "RiverCode",
        geom
    FROM
        all_nodes
    GROUP BY
        "RiverCode",
        geom
    HAVING
        COUNT(geom) = 1)

    INSERT INTO "{0}"."Endpoints"(geom, "RiverCode", "ReachCode", "NodeID")
    SELECT
        all_nodes.geom,
        all_nodes."RiverCode",
        all_nodes."ReachCode",
        "NodesTable"."NodeID"
    FROM
        all_nodes,
        single_nodes,
        "{0}"."NodesTable"
    WHERE
        all_nodes."RiverCode" = single_nodes."RiverCode" AND
        all_nodes.geom = single_nodes.geom AND
        all_nodes.point_type = 'end' AND
        all_nodes.geom = "NodesTable".geom;

------------------------------------------------------------------------------------------------------------------------
CREATE OR REPLACE FUNCTION "{0}".from_to_stations ()
    RETURNS VOID AS
$BODY$
DECLARE
    c cursor FOR SELECT * FROM "{0}"."Endpoints";
    r "{0}"."Endpoints"%ROWTYPE;
    river text;
    tonode_id integer;
    fromnode_id integer;
    fromsta double precision;
    tosta double precision;
    len double precision;
    counter integer;
BEGIN
FOR r IN c LOOP
    river := r."RiverCode";
    tonode_id := r."NodeID";
    fromsta := 0;
    tosta := 0;
    counter := (SELECT COUNT(*) FROM "{0}"."StreamCenterlines" WHERE "RiverCode" = river);
    FOR i IN 1..counter LOOP
        SELECT
            "FromNode", ST_Length(geom)
        INTO
            fromnode_id, len
        FROM
            "{0}"."StreamCenterlines"
        WHERE
            "RiverCode" = river AND
            "ToNode" = tonode_id;
        tosta := fromsta + len;
        UPDATE
            "{0}"."StreamCenterlines"
        SET
            "ReachLen" = len,
            "FromSta" = fromsta,
            "ToSta" = tosta
        WHERE
            "RiverCode" = river AND
            "ToNode" = tonode_id;
        tonode_id := fromnode_id;
        fromsta := tosta;
    END LOOP;
END LOOP;
END;
$BODY$
    LANGUAGE plpgsql;
------------------------------------------------------------------------------------------------------------------------
SELECT "{0}".from_to_stations ();
DROP FUNCTION IF EXISTS "{0}".from_to_stations ();
'''
        qry = qry.format(self.schema)
        return qry


class NodesTable(HecRasObject):
    def __init__(self):
        super(NodesTable, self).__init__()
        self.order = 17
        self.main = False
        self.visible = False
        self.spatial_index = False
        self.geom_type = 'POINT'
        self.attrs = [
            ('"NodeID"', 'serial primary key'),
            ('"X"', 'double precision'),
            ('"Y"', 'double precision')]


class Endpoints(HecRasObject):
    def __init__(self):
        super(Endpoints, self).__init__()
        self.order = 18
        self.main = False
        self.visible = False
        self.spatial_index = False
        self.geom_type = 'POINT'
        self.attrs = [
            ('"EndID"', 'serial primary key'),
            ('"RiverCode"', 'text'),
            ('"ReachCode"', 'text'),
            ('"NodeID"', 'integer')]


class XSCutLines(HecRasObject):
    def __init__(self):
        super(XSCutLines, self).__init__()
        self.order = 7
        self.geom_type = 'LINESTRING'
        self.attrs = [
            ('"XsecID"', 'serial primary key'),
            ('"ReachID"', 'integer'),
            ('"Station"', 'double precision'),
            ('"RiverCode"', 'text'),
            ('"ReachCode"', 'text'),
            ('"LeftBank"', 'double precision'),
            ('"RightBank"', 'double precision'),
            ('"LLength"', 'double precision'),
            ('"ChLength"', 'double precision'),
            ('"RLength"', 'double precision'),
            ('"NodeName"', 'text'),
            ('"DtmID"', 'integer')]

    def pg_river_reach_names(self):
        qry = '''
UPDATE "{0}"."XSCutLines" AS xs
SET
    "ReachID" = riv."ReachID",
    "RiverCode" = riv."RiverCode",
    "ReachCode" = riv."ReachCode"
FROM
    "{0}"."StreamCenterlines" AS riv
WHERE
    ST_Intersects(xs.geom, riv.geom);
'''
        qry = qry.format(self.schema)
        return qry

    def pg_stationing(self):
        qry = '''
WITH xspts AS
    (SELECT
        xs."XsecID" AS "XsecID",
        riv."ReachID" AS "ReachID",
        ST_LineLocatePoint(riv.geom, ST_Intersection(xs.geom, riv.geom)) AS "Fraction"
    FROM
        "{0}"."StreamCenterlines" AS riv,
        "{0}"."XSCutLines" AS xs
    WHERE
        ST_Intersects(xs.geom, riv.geom))

UPDATE "{0}"."XSCutLines" AS xs
SET
    "Station" = riv."ToSta" + xspts."Fraction" * (riv."FromSta" - riv."ToSta")
FROM
    xspts,
    "{0}"."StreamCenterlines" AS riv
WHERE
    xspts."ReachID" = riv."ReachID" AND
    xspts."XsecID" = xs."XsecID";
'''
        qry = qry.format(self.schema)
        return qry

    def pg_bank_stations(self):
        qry = '''
WITH bankpts AS
    (SELECT
        xs."XsecID" AS "XsecID",
        ST_LineLocatePoint(xs.geom, ST_Intersection(xs.geom, bl.geom)) AS "Fraction"
    FROM
        "{0}"."BankLines" AS bl,
        "{0}"."XSCutLines" AS xs
    WHERE
        ST_Intersects(xs.geom, bl.geom))

UPDATE "{0}"."XSCutLines" AS xs
SET
    "LeftBank" = minmax."minFrac",
    "RightBank" = minmax."maxFrac"
FROM
    (SELECT
        "XsecID",
        min("Fraction") AS "minFrac",
        max("Fraction") AS "maxFrac"
    FROM
        bankpts AS bp
    GROUP BY
        "XsecID") AS minmax
WHERE
    xs."XsecID" = minmax."XsecID";
'''
        qry = qry.format(self.schema)
        return qry

    def pg_downstream_reach_lengths(self, line_type='Channel', sort=True):
        index = ''
        if sort is True:
            index = '''
DROP INDEX IF EXISTS "{0}"."{0}_XSCutLines_order_idx";
CREATE INDEX "{0}_XSCutLines_order_idx" ON "{0}"."XSCutLines" ("RiverCode", "Station");
CLUSTER "{0}"."XSCutLines" USING "{0}_XSCutLines_order_idx";
'''
            index = index.format(self.schema)
        else:
            pass
        if line_type == 'Left':
            column = 'LLength'
        elif line_type == 'Channel':
            column = 'ChLength'
        elif line_type == 'Right':
            column = 'RLength'
        else:
            raise ValueError('Invalid line type!')
        qry = '''
CREATE OR REPLACE FUNCTION "{0}".downstream_reach_lengths ()
    RETURNS VOID AS
$BODY$
DECLARE
    c cursor FOR SELECT * FROM "{0}"."XSCutLines";
    r "{0}"."XSCutLines"%ROWTYPE;
    river_code text := '';
    distance double precision := 0;
    station double precision := 0;
    prev_station double precision := 0;
BEGIN
FOR r IN c LOOP
    SELECT
        (1 - ST_LineLocatePoint(path.geom, ST_Intersection(r.geom, path.geom))) * ST_Length(path.geom)
    INTO
        station
    FROM
        "{0}"."Flowpaths" AS path
    WHERE
        path."LineType" = '{1}' AND
        ST_Intersects(r.geom, path.geom);
    distance := station - prev_station;
    IF river_code <> r."RiverCode" OR distance <= 0 THEN
        UPDATE "{0}"."XSCutLines" SET
        "{2}" = 0
        WHERE CURRENT OF c;
    ELSE
        UPDATE "{0}"."XSCutLines" SET
        "{2}" = distance
        WHERE CURRENT OF c;
    END IF;
    prev_station := station;
    river_code := r."RiverCode";
END LOOP;
END;
$BODY$
    LANGUAGE plpgsql;
------------------------------------------------------------------------------------------------------------------------
{3}
SELECT "{0}".downstream_reach_lengths ();
DROP FUNCTION IF EXISTS "{0}".downstream_reach_lengths ();
'''
        qry = qry.format(self.schema, line_type, column, index)
        return qry

    def pg_surface_points(self):
        qry = '''
------------------------------------------------------------------------------------------------------------------------
-- insert xs points along each xsection --
------------------------------------------------------------------------------------------------------------------------
WITH line AS
    (SELECT
        xs."XsecID" AS "XsecID",
        dtm."CellSize" AS "CellSize",
        (ST_Dump(xs.geom)).geom AS geom
    FROM
        "{0}"."XSCutLines" AS xs,
        "{0}"."DTMs" AS dtm
    WHERE
        xs."DtmID" = dtm."DtmID"),
    linemeasure AS
    (SELECT
        "XsecID",
        ST_AddMeasure(line.geom, 0, ST_Length(line.geom)) AS linem,
        generate_series(0, (ST_Length(line.geom)*100)::int, (line."CellSize"*100)::int) AS "Station"
    FROM line),
    geometries AS
    (SELECT
        "XsecID",
        "Station",
        (ST_Dump(ST_GeometryN(ST_LocateAlong(linem, "Station"/100), 1))).geom AS geom
    FROM linemeasure)

    INSERT INTO "{0}"."XSSurface" (geom, "XsecID", "Station")
    SELECT
        ST_SetSRID(ST_MakePoint(ST_X(geom), ST_Y(geom)), {1}) AS geom,
        "XsecID",
        "Station"/100
    FROM geometries;

    INSERT INTO "{0}"."XSSurface" (geom, "XsecID", "Station")
    SELECT
        ST_Endpoint(geom),
        "XsecID",
        ST_Length(geom)
    FROM "{0}"."XSCutLines";
'''
        qry = qry.format(self.schema, self.srid)
        return qry

    def pg_update_banks(self, area='Channel', xs_tol=0):
        """
        Update XSSurface points using bathymetry points data.
        The update extents is defined by bank lines and choice of the xsection part: channel, left or right overbank.
        """
        qry = '''
------------------------------------------------------------------------------------------------------------------------
-- check which xsections have some bathymetry points --
-- points must be located within a given tolerance from xs --
------------------------------------------------------------------------------------------------------------------------
UPDATE "{0}"."Bathymetry" AS b
SET
    "XsecID" = xs."XsecID"
FROM
    "{0}"."XSCutLines" AS xs
WHERE
    ST_DWithin(b.geom, xs.geom, {1});

UPDATE "{0}"."Bathymetry" AS b
SET
    "Station" = ST_LineLocatePoint(xs.geom, b.geom) * ST_Length(xs.geom)
FROM
    "{0}"."XSCutLines" AS xs
WHERE
    b."XsecID" IS NOT NULL AND
    b."XsecID" = xs."XsecID";
'''
        qry = qry.format(self.schema, xs_tol)
        if area == 'Channel':
            cond = 'p."Station" > xs."LeftBank" * ST_Length(xs.geom) AND p."Station" < xs."RightBank" * ST_Length(xs.geom)'
        elif area == 'Left':
            cond = 'p."Station" < xs."LeftBank" * ST_Length(xs.geom)'
        else:
            cond = 'p."Station" > xs."RightBank" * ST_Length(xs.geom)'
        qry += '''
------------------------------------------------------------------------------------------------------------------------
-- delete original xsec points --
------------------------------------------------------------------------------------------------------------------------
WITH ids AS
    (SELECT DISTINCT
        b."XsecID"
    FROM
        "{0}"."Bathymetry" AS b
    WHERE
        b."XsecID" IS NOT NULL)

DELETE FROM "{0}"."XSSurface" AS p
USING
    "{0}"."XSCutLines" AS xs,
    ids
WHERE
    ids."XsecID" = xs."XsecID" AND
    ids."XsecID" = p."XsecID" AND
    {1};
------------------------------------------------------------------------------------------------------------------------
-- insert bathymetry points --
------------------------------------------------------------------------------------------------------------------------
WITH bathy AS
    (SELECT
        p."XsecID",
        p."Station",
        p."Elevation",
        p.geom
    FROM
        "{0}"."Bathymetry" AS p,
        "{0}"."XSCutLines" AS xs
    WHERE
        p."XsecID" = xs."XsecID" AND
        {1})

INSERT INTO "{0}"."XSSurface" ("XsecID", "Station", "Elevation", geom)
(SELECT * FROM bathy);
'''
        qry = qry.format(self.schema, cond)
        return qry

    def pg_update_polygons(self, xs_tol=0):
        """
        Update XSSurface points using bathymetry points data.
        Only points inside the polygons of bathymetry extents will be updated.
        """
        qry = '''
UPDATE "{0}"."Bathymetry" AS b
SET
    "XsecID" = xs."XsecID"
FROM
    "{0}"."XSCutLines" AS xs,
    "{0}"."BathymetryExtents" AS be
WHERE
    ST_Intersects(b.geom, be.geom) AND
    ST_DWithin(b.geom, xs.geom, {1});
------------------------------------------------------------------------------------------------------------------------
-- set points stations along a xscutline --
------------------------------------------------------------------------------------------------------------------------
UPDATE "{0}"."Bathymetry" b
SET
    "Station" = ST_LineLocatePoint(xs.geom, b.geom) * ST_Length(xs.geom)
FROM
    "{0}"."XSCutLines" AS xs
WHERE
    b."XsecID" IS NOT NULL AND
    b."XsecID" = xs."XsecID";
------------------------------------------------------------------------------------------------------------------------
-- delete original xsec points --
------------------------------------------------------------------------------------------------------------------------
WITH ids AS
    (SELECT DISTINCT
        b."XsecID"
    FROM
        "{0}"."Bathymetry" AS b
    WHERE
        b."XsecID" IS NOT NULL)

DELETE FROM "{0}"."XSSurface" AS p
USING
    "{0}"."BathymetryExtents" AS be,
    ids
WHERE
    ids."XsecID" = p."XsecID" AND
    ST_Intersects(p.geom, be.geom);
------------------------------------------------------------------------------------------------------------------------
-- insert bathymetry points --
------------------------------------------------------------------------------------------------------------------------
WITH bathy AS
    (SELECT
        p."XsecID",
        p."Station",
        p."Elevation",
        p.geom
    FROM
        "{0}"."Bathymetry" AS p,
        "{0}"."BathymetryExtents" AS be
    WHERE
        p."XsecID" IS NOT NULL AND
        ST_Intersects(p.geom, be.geom))

INSERT INTO "{0}"."XSSurface" ("XsecID", "Station", "Elevation", geom)
(SELECT * FROM bathy);
'''
        qry = qry.format(self.schema, xs_tol)
        return qry


class XSSurface(HecRasObject):
    def __init__(self):
        super(XSSurface, self).__init__()
        self.order = 19
        self.main = False
        self.visible = False
        self.spatial_index = False
        self.geom_type = 'POINT'
        self.attrs = [
            ('"PtID"', 'bigserial primary key'),
            ('"XsecID"', 'integer'),
            ('"Station"', 'double precision'),
            ('"Elevation"', 'double precision'),
            ('"CoverCode"', 'text'),
            ('"SrcId"', 'integer'),
            ('"Notes"', 'text')]


class BankLines(HecRasObject):
    def __init__(self):
        super(BankLines, self).__init__()
        self.order = 9
        self.geom_type = 'LINESTRING'
        self.attrs = [('"BankID"', 'serial primary key')]


class BankPoints(HecRasObject):
    def __init__(self):
        super(BankPoints, self).__init__()
        self.order = 20
        self.main = False
        self.spatial_index = False
        self.visible = False
        self.geom_type = 'POINT'
        self.attrs = [
            ('"BankID"', 'serial primary key'),
            ('"XsecID"', 'integer'),
            ('"Elevation"', 'double precision')]


class Flowpaths(HecRasObject):
    def __init__(self):
        super(Flowpaths, self).__init__()
        self.order = 8
        self.geom_type = 'LINESTRING'
        self.attrs = [
            ('"FpID"', 'serial primary key'),
            ('"LineType"', 'text')]

    def pg_get_flowpaths_linetype(self):
        qry = '''SELECT "LineType" FROM "{0}"."Flowpaths";'''
        qry = qry.format(self.schema)
        return qry

    def pg_channel_from_stream(self):
        qry = '''
INSERT INTO "{0}"."Flowpaths"(geom, "LineType")
    (SELECT
        (ST_Dump(geom)).geom AS geom,
        'Channel'
    FROM
        (SELECT
            ST_LineMerge(ST_Union(geom)) AS geom
        FROM
            "{0}"."StreamCenterlines"
        WHERE
            "ReachCode" IS NOT NULL
        GROUP BY
            "RiverCode") AS river_union);
'''
        qry = qry.format(self.schema)
        return qry


class IneffAreas(HecRasObject):
    def __init__(self):
        super(IneffAreas, self).__init__()
        self.order = 4
        self.geom_type = 'POLYGON'
        self.attrs = [
            ('"IneffID"', 'serial primary key'),
            ('"Elevation"', 'double precision')]

    def pg_ineffective_positions(self):
        qry = '''
INSERT INTO "{0}"."IneffLines"(geom, "XsecID", "IneffID", "Elevation")
SELECT
    ST_Intersection(xs.geom, ineff.geom) AS geom,
    xs."XsecID",
    ineff."IneffID",
    ineff."Elevation"
FROM
    "{0}"."XSCutLines" AS xs,
    "{0}"."IneffAreas" AS ineff
WHERE
    ST_Intersects(xs.geom, ineff.geom);

UPDATE "{0}"."IneffLines" AS il
SET
    "FromFract" = ST_LineLocatePoint(xs.geom, ST_StartPoint(il.geom)),
    "ToFract" = ST_LineLocatePoint(xs.geom, ST_EndPoint(il.geom))
FROM
    "{0}"."XSCutLines" AS xs
WHERE
    il."XsecID" = xs."XsecID";
'''
        qry = qry.format(self.schema)
        return qry


class IneffLines(HecRasObject):
    def __init__(self):
        super(IneffLines, self).__init__()
        self.order = 15
        self.main = False
        self.visible = False
        self.geom_type = 'LINESTRING'
        self.attrs = [
            ('"IneffLID"', 'serial primary key'),
            ('"IneffID"', 'integer'),
            ('"XsecID"', 'integer'),
            ('"FromFract"', 'double precision'),
            ('"ToFract"', 'double precision'),
            ('"Elevation"', 'double precision')]


class BlockedObs(HecRasObject):
    def __init__(self):
        super(BlockedObs, self).__init__()
        self.order = 5
        self.geom_type = 'POLYGON'
        self.attrs = [
            ('"BlockID"', 'serial primary key'),
            ('"Elevation"', 'double precision')]

    def pg_blocked_positions(self):
        qry = '''
INSERT INTO "{0}"."BlockLines"(geom, "XsecID", "BlockID", "Elevation")
SELECT
    ST_Intersection(xs.geom, block.geom) AS geom,
    xs."XsecID",
    block."BlockID",
    block."Elevation"
FROM
    "{0}"."XSCutLines" AS xs,
    "{0}"."BlockedObs" AS block
WHERE
    ST_Intersects(xs.geom, block.geom);

UPDATE "{0}"."BlockLines" AS bl
SET
    "FromFract" = ST_LineLocatePoint(xs.geom, ST_StartPoint(bl.geom)),
    "ToFract" = ST_LineLocatePoint(xs.geom, ST_EndPoint(bl.geom))
FROM
    "{0}"."XSCutLines" AS xs
WHERE
    bl."XsecID" = xs."XsecID";
'''
        qry = qry.format(self.schema)
        return qry


class BlockLines(HecRasObject):
    def __init__(self):
        super(BlockLines, self).__init__()
        self.order = 16
        self.main = False
        self.visible = False
        self.geom_type = 'LINESTRING'
        self.attrs = [
            ('"BlockLID"', 'serial primary key'),
            ('"BlockID"', 'integer'),
            ('"XsecID"', 'integer'),
            ('"FromFract"', 'double precision'),
            ('"ToFract"', 'double precision'),
            ('"Elevation"', 'double precision')]


class LanduseAreas(HecRasObject):
    def __init__(self):
        super(LanduseAreas, self).__init__()
        self.order = 2
        self.geom_type = 'MULTIPOLYGON'
        self.attrs = [
            ('"LUID"', 'serial primary key'),
            ('"LUCode"', 'text'),
            ('"N_Value"', 'double precision')]

    def pg_extract_manning(self):
        qry = '''
------------------------------------------------------------------------------------------------------------------------
-- Intersect of land use layer with cross section layer  --
------------------------------------------------------------------------------------------------------------------------
SELECT
    "LUID",
    "LUCode",
    "N_Value",
    (ST_Dump(geom)).geom::geometry(POLYGON, {1}) AS geom
INTO
    "{0}".ludump
FROM
    "{0}"."LanduseAreas";

CREATE INDEX idx_ludump ON "{0}".ludump USING gist(geom);
------------------------------------------------------------------------------------------------------------------------
WITH inter_xs_dump AS
    (SELECT
        xs."XsecID",
        lud."N_Value",
        lud."LUCode",
        (ST_Dump(ST_Intersection(lud.geom, xs.geom))).geom::geometry(LINESTRING, {1}) AS geom
    FROM
        "{0}".ludump AS lud,
        "{0}"."XSCutLines" AS xs
    WHERE
        ST_Intersects(lud.geom, xs.geom)),
    single_line AS
    (SELECT
        "XsecID",
        (ST_Dump(xs.geom)).geom::geometry(LINESTRING, {1}) AS geom
    FROM
        "{0}"."XSCutLines" AS xs),
    shiftpoints AS
    (SELECT
        "XsecID",
        "N_Value",
        "LUCode",
        ST_Line_Interpolate_Point(inter_xs_dump.geom, 0.00005)::geometry(POINT, {1}) AS geom
    FROM
        inter_xs_dump),
    tmpman AS
    (SELECT
         sp."XsecID",
         sp."N_Value",
         sp."LUCode",
         ST_LineLocatePoint(sl.geom, sp.geom) AS "Fraction"
    FROM
        single_line AS sl,
        shiftpoints AS sp
    WHERE
        sl."XsecID" = sp."XsecID")
------------------------------------------------------------------------------------------------------------------------
-- Creation of table with Manning's coefficients  --
------------------------------------------------------------------------------------------------------------------------
INSERT INTO "{0}"."Manning" ("XsecID", "Fraction", "N_Value", "LUCode")
SELECT
    "XsecID",
    CASE WHEN
        "Fraction" < 0.0001 THEN 0
    ELSE
        "Fraction"
    END AS "Fraction",
    "N_Value",
    "LUCode"
FROM
    tmpman
ORDER BY
    "XsecID",
    "Fraction";
------------------------------------------------------------------------------------------------------------------------
DROP TABLE "{0}".ludump;
------------------------------------------------------------------------------------------------------------------------
'''
        qry = qry.format(self.schema, self.srid)
        return qry


class Manning(HecRasObject):
    def __init__(self):
        super(Manning, self).__init__()
        self.order = 28
        self.visible = False
        self.spatial_index = False
        self.attrs = [
            ('"XsecID"', 'integer'),
            ('"Fraction"', 'double precision'),
            ('"N_Value"', 'double precision'),
            ('"LUCode"', 'text')]


class LeveeAlignment(HecRasObject):
    def __init__(self):
        super(LeveeAlignment, self).__init__()
        self.order = 10
        self.geom_type = 'LINESTRING'
        self.attrs = [('"LeveeID"', 'serial primary key')]

    def pg_levee_positions(self):
        qry = '''
INSERT INTO "{0}"."LeveePoints"(geom, "LeveeID", "XsecID", "Fraction")
    SELECT
        ST_Intersection(lev.geom, xs.geom) AS geom,
        lev."LeveeID",
        xs."XsecID",
        ST_LineLocatePoint(xs.geom, ST_Intersection(lev.geom, xs.geom)) AS "Fraction"
    FROM
        "{0}"."LeveeAlignment" AS lev,
        "{0}"."XSCutLines" AS xs
    WHERE
        ST_Intersects(xs.geom, lev.geom);
'''
        qry = qry.format(self.schema)
        return qry


class LeveePoints(HecRasObject):
    def __init__(self):
        super(LeveePoints, self).__init__()
        self.order = 21
        self.main = False
        self.spatial_index = False
        self.visible = False
        self.geom_type = 'POINT'
        self.attrs = [
            ('"LeveePID"', 'serial primary key'),
            ('"LeveeID"', 'integer'),
            ('"XsecID"', 'integer'),
            ('"Fraction"', 'double precision'),
            ('"Elevation"', 'double precision')]


class Bridges(HecRasObject):
    def __init__(self):
        super(Bridges, self).__init__()
        self.order = 13
        self.geom_type = 'LINESTRING'
        self.attrs = [
            ('"BridgeID"', 'serial primary key'),
            ('"RiverCode"', 'text'),
            ('"ReachCode"', 'text'),
            ('"Station"', 'double precision'),
            ('"USDistance"', 'double precision'),
            ('"TopWidth"', 'double precision'),
            ('"NodeName"', 'text'),
            ('"DtmID"', 'integer')]

    def pg_river_reach_names(self):
        qry = '''
UPDATE "{0}"."Bridges" AS br
SET
    "RiverCode" = riv."RiverCode",
    "ReachCode" = riv."ReachCode"
FROM
    "{0}"."StreamCenterlines" AS riv
WHERE
    ST_Intersects(br.geom, riv.geom);
'''
        qry = qry.format(self.schema)
        return qry

    def pg_stationing(self):
        qry = '''
WITH brpts AS
    (SELECT
        br."BridgeID" AS "BridgeID",
        riv."ReachID" AS "ReachID",
        ST_LineLocatePoint(riv.geom, ST_Intersection(br.geom, riv.geom)) AS "Fraction"
    FROM
        "{0}"."StreamCenterlines" AS riv,
        "{0}"."Bridges" AS br
    WHERE
        ST_Intersects(br.geom, riv.geom))

UPDATE "{0}"."Bridges" AS br
SET
    "Station" = riv."ToSta" + brpts."Fraction" * (riv."FromSta" - riv."ToSta")
FROM
    brpts,
    "{0}"."StreamCenterlines" AS riv
WHERE
    brpts."ReachID" = riv."ReachID" AND
    brpts."BridgeID" = br."BridgeID";
'''
        qry = qry.format(self.schema)
        return qry

    def pg_surface_points(self):
        qry = '''
WITH line AS
    (SELECT
        br."BridgeID" AS "BridgeID",
        dtm."CellSize" AS "CellSize",
        (ST_Dump(br.geom)).geom AS geom
    FROM
        "{0}"."Bridges" AS br,
        "{0}"."DTMs" AS dtm
    WHERE
        br."DtmID" = dtm."DtmID"),
    linemeasure AS
    (SELECT
        "BridgeID",
        ST_AddMeasure(line.geom, 0, ST_Length(line.geom)) AS linem,
        generate_series(0, (ST_Length(line.geom)*100)::int, (line."CellSize"*100)::int) AS "Station"
    FROM line),
    geometries AS
    (SELECT
        "BridgeID",
        "Station",
        (ST_Dump(ST_GeometryN(ST_LocateAlong(linem, "Station"/100), 1))).geom AS geom
    FROM linemeasure)

    INSERT INTO "{0}"."BRSurface" (geom, "BridgeID", "Station")
    SELECT
        ST_SetSRID(ST_MakePoint(ST_X(geom), ST_Y(geom)), {1}) AS geom,
        "BridgeID",
        "Station"/100
    FROM geometries;

    INSERT INTO "{0}"."BRSurface" (geom, "BridgeID", "Station")
    SELECT
        ST_Endpoint(geom),
        "BridgeID",
        ST_Length(geom)
    FROM "{0}"."Bridges";
'''
        qry = qry.format(self.schema, self.srid)
        return qry


class BRSurface(HecRasObject):
    def __init__(self):
        super(BRSurface, self).__init__()
        self.order = 24
        self.main = False
        self.visible = False
        self.spatial_index = False
        self.geom_type = 'POINT'
        self.attrs = [
            ('"PtID"', 'bigserial primary key'),
            ('"BridgeID"', 'integer'),
            ('"Station"', 'double precision'),
            ('"Elevation"', 'double precision')]


class InlineStructures(HecRasObject):
    def __init__(self):
        super(InlineStructures, self).__init__()
        self.order = 12
        self.geom_type = 'LINESTRING'
        self.attrs = [
            ('"InlineSID"', 'serial primary key'),
            ('"RiverCode"', 'text'),
            ('"ReachCode"', 'text'),
            ('"Station"', 'double precision'),
            ('"USDistance"', 'double precision'),
            ('"TopWidth"', 'double precision'),
            ('"NodeName"', 'text'),
            ('"DtmID"', 'integer')]

    def pg_river_reach_names(self):
        qry = '''
UPDATE "{0}"."InlineStructures" AS ins
SET
    "RiverCode" = riv."RiverCode",
    "ReachCode" = riv."ReachCode"
FROM
    "{0}"."StreamCenterlines" AS riv
WHERE
    ST_Intersects(ins.geom, riv.geom);
'''
        qry = qry.format(self.schema)
        return qry

    def pg_stationing(self):
        qry = '''
WITH ispts AS
    (SELECT
        ins."InlineSID" AS "InlineSID",
        riv."ReachID" AS "ReachID",
        ST_LineLocatePoint(riv.geom, ST_Intersection(ins.geom, riv.geom)) AS "Fraction"
    FROM
        "{0}"."StreamCenterlines" AS riv,
        "{0}"."InlineStructures" AS ins
    WHERE
        ST_Intersects(ins.geom, riv.geom))

UPDATE "{0}"."InlineStructures" AS ins
SET
    "Station" = riv."ToSta" + ispts."Fraction" * (riv."FromSta" - riv."ToSta")
FROM
    ispts,
    "{0}"."StreamCenterlines" AS riv
WHERE
    ispts."ReachID" = riv."ReachID" AND
    ispts."InlineSID" = ins."InlineSID";
'''
        qry = qry.format(self.schema)
        return qry

    def pg_surface_points(self):
        qry = '''
WITH line AS
    (SELECT
        ins."InlineSID" AS "InlineSID",
        dtm."CellSize" AS "CellSize",
        (ST_Dump(ins.geom)).geom AS geom
    FROM
        "{0}"."InlineStructures" AS ins,
        "{0}"."DTMs" AS dtm
    WHERE
        ins."DtmID" = dtm."DtmID"),
    linemeasure AS
    (SELECT
        "InlineSID",
        ST_AddMeasure(line.geom, 0, ST_Length(line.geom)) AS linem,
        generate_series(0, (ST_Length(line.geom)*100)::int, (line."CellSize"*100)::int) AS "Station"
    FROM line),
    geometries AS
    (SELECT
        "InlineSID",
        "Station",
        (ST_Dump(ST_GeometryN(ST_LocateAlong(linem, "Station"/100), 1))).geom AS geom
    FROM linemeasure)

    INSERT INTO "{0}"."ISSurface" (geom, "InlineSID", "Station")
    SELECT
        ST_SetSRID(ST_MakePoint(ST_X(geom), ST_Y(geom)), {1}) AS geom,
        "InlineSID",
        "Station"/100
    FROM geometries;

    INSERT INTO "{0}"."ISSurface" (geom, "InlineSID", "Station")
    SELECT
        ST_Endpoint(geom),
        "InlineSID",
        ST_Length(geom)
    FROM "{0}"."InlineStructures";
'''
        qry = qry.format(self.schema, self.srid)
        return qry


class ISSurface(HecRasObject):
    def __init__(self):
        super(ISSurface, self).__init__()
        self.order = 23
        self.main = False
        self.visible = False
        self.spatial_index = False
        self.geom_type = 'POINT'
        self.attrs = [
            ('"PtID"', 'bigserial primary key'),
            ('"InlineSID"', 'integer'),
            ('"Station"', 'double precision'),
            ('"Elevation"', 'double precision')]


class LateralStructures(HecRasObject):
    def __init__(self):
        super(LateralStructures, self).__init__()
        self.order = 11
        self.geom_type = 'LINESTRING'
        self.attrs = [
            ('"LateralSID"', 'serial primary key'),
            ('"RiverCode"', 'text'),
            ('"ReachCode"', 'text'),
            ('"Station"', 'double precision'),
            ('"USDistance"', 'double precision'),
            ('"TopWidth"', 'double precision'),
            ('"NodeName"', 'text'),
            ('"DtmID"', 'integer')]

    def pg_river_reach_names(self):
        qry = '''
WITH cpnt AS
    (SELECT
        geom,
        "LateralSID",
        "RiverCode",
        "ReachCode"
    FROM
        (SELECT
            ST_ClosestPoint(sc.geom, ST_StartPoint(ls.geom))::geometry(POINT, {1}) AS geom,
            ls."LateralSID",
            sc."RiverCode",
            sc."ReachCode",
            RANK() OVER (PARTITION BY ls."LateralSID" ORDER BY ST_Distance(sc.geom, ST_StartPoint(ls.geom))) AS rnk
        FROM
            "{0}"."StreamCenterlines" AS sc,
            "{0}"."LateralStructures" AS ls
        ORDER BY
            ls."LateralSID") AS pnt
    WHERE
        rnk = 1)

UPDATE "{0}"."LateralStructures" AS ls
SET
   "RiverCode" = cpnt."RiverCode",
   "ReachCode" = cpnt."ReachCode"
FROM
    cpnt
WHERE
   ls."LateralSID" = cpnt."LateralSID";
'''
        qry = qry.format(self.schema, self.srid)
        return qry

    def pg_stationing(self):
        qry = '''
WITH cpnt AS
    (SELECT
        geom,
        "LateralSID",
        "ReachCode",
         ("ToSta"-"FromSta") AS "Length",
         "FromSta"
    FROM
        (SELECT
            ST_ClosestPoint(sc.geom, ST_StartPoint(ls.geom))::geometry(POINT, {1}) AS geom,
            ls."LateralSID",
            sc."ReachCode",
            sc."FromSta",
            sc."ToSta",
            RANK() OVER (PARTITION BY ls."LateralSID" ORDER BY ST_Distance(sc.geom, ST_StartPoint(ls.geom))) AS rnk
        FROM
            "{0}"."StreamCenterlines" AS sc,
            "{0}"."LateralStructures" AS ls
        ORDER BY
            ls."LateralSID") AS pnt
    WHERE
        rnk = 1)

UPDATE "{0}"."LateralStructures" AS ls
SET
   "Station" = cpnt."Length"*(1-ST_Line_Locate_Point(sc.geom, cpnt.geom)) + cpnt."FromSta"
FROM
    cpnt,
    "{0}"."StreamCenterlines" AS sc
WHERE
    ls."LateralSID" = cpnt."LateralSID" AND
    sc."ReachCode" = cpnt."ReachCode";
'''
        qry = qry.format(self.schema, self.srid)
        return qry

    def pg_surface_points(self):
        qry = '''
WITH line AS
    (SELECT
        ls."LateralSID" AS "LateralSID",
        dtm."CellSize" AS "CellSize",
        (ST_Dump(ls.geom)).geom AS geom
    FROM
        "{0}"."LateralStructures" AS ls,
        "{0}"."DTMs" AS dtm
    WHERE
        ls."DtmID" = dtm."DtmID"),
    linemeasure AS
    (SELECT
        "LateralSID",
        ST_AddMeasure(line.geom, 0, ST_Length(line.geom)) AS linem,
        generate_series(0, (ST_Length(line.geom)*100)::int, (line."CellSize"*100)::int) AS "Station"
    FROM line),
    geometries AS
    (SELECT
        "LateralSID",
        "Station",
        (ST_Dump(ST_GeometryN(ST_LocateAlong(linem, "Station"/100), 1))).geom AS geom
    FROM linemeasure)

    INSERT INTO "{0}"."LSSurface" (geom, "LateralSID", "Station")
    SELECT
        ST_SetSRID(ST_MakePoint(ST_X(geom), ST_Y(geom)), {1}) AS geom,
        "LateralSID",
        "Station"/100
    FROM geometries;

    INSERT INTO "{0}"."LSSurface" (geom, "LateralSID", "Station")
    SELECT
        ST_Endpoint(geom),
        "LateralSID",
        ST_Length(geom)
    FROM "{0}"."LateralStructures";
'''
        qry = qry.format(self.schema, self.srid)
        return qry


class LSSurface(HecRasObject):
    def __init__(self):
        super(LSSurface, self).__init__()
        self.order = 22
        self.main = False
        self.visible = False
        self.spatial_index = False
        self.geom_type = 'POINT'
        self.attrs = [
            ('"PtID"', 'bigserial primary key'),
            ('"LateralSID"', 'integer'),
            ('"Station"', 'double precision'),
            ('"Elevation"', 'double precision')]


class StorageAreas(HecRasObject):
    def __init__(self):
        super(StorageAreas, self).__init__()
        self.order = 3
        self.geom_type = 'POLYGON'
        self.attrs = [
            ('"StorageID"', 'serial primary key'),
            ('"Name"', 'text'),
            ('"MaxElev"', 'double precision'),
            ('"MinElev"', 'double precision'),
            ('"UserElev"', 'double precision'),
            ('"DtmID"', 'integer')]

    def pg_surface_points(self):
        qry = '''
CREATE OR REPLACE FUNCTION "{0}".point_grid ()
    RETURNS VOID AS
$BODY$
DECLARE
    c cursor FOR SELECT * FROM "{0}"."StorageAreas";
    r "{0}"."StorageAreas"%ROWTYPE;
    x double precision;
    y double precision;
    pnt geometry;
    inside boolean;
    sa_id integer;
    row_nr integer;
    col_nr integer;
    cellsize double precision;
    min_x double precision;
    max_x double precision;
    min_y double precision;
    max_y double precision;
BEGIN
    FOR r IN c LOOP
        SELECT dtm."CellSize" INTO cellsize FROM "{0}"."DTMs" AS dtm WHERE dtm."DtmID" = r."DtmID";
        min_x := ST_Xmin(ST_Extent(r.geom));
        max_x := ST_Xmax(ST_Extent(r.geom));
        min_y := ST_Ymin(ST_Extent(r.geom));
        max_y := ST_Ymax(ST_Extent(r.geom));
        row_nr := ceiling((max_x - min_x) / cellsize);
        col_nr := ceiling((max_y - min_y) / cellsize);
        x := min_x;
        FOR i IN 1..row_nr LOOP
            y := min_y;
            FOR j IN 1..col_nr LOOP
                pnt := (ST_SetSRID(ST_Point(x, y), {1}));
                SELECT ST_Within(pnt, r.geom), r."StorageID" INTO inside, sa_id WHERE ST_Within(pnt, r.geom) IS True;
                IF inside IS True THEN
                    INSERT INTO "{0}"."SASurface"(geom, "StorageID")
                    VALUES (pnt, sa_id);
                END IF;
                y := y + cellsize;
            END LOOP;
            x := x + cellsize;
        END LOOP;
    END LOOP;
END;
$BODY$
    LANGUAGE plpgsql;


SELECT "{0}".point_grid ();
ALTER TABLE "{0}"."SASurface" ADD COLUMN "PtID" bigserial primary key;
'''
        qry = qry.format(self.schema, self.srid)
        return qry

    def pg_maxmin(self):
        qry = '''
WITH data AS
    (SELECT
        "StorageID",
        MAX("Elevation"),
        MIN("Elevation")
    FROM
        "{0}"."SASurface"
    GROUP BY
        "StorageID")
UPDATE "{0}"."StorageAreas" AS sa
SET
    "MaxElev" = data.max,
    "MinElev" = data.min
FROM
    data
WHERE
    sa."StorageID" = data."StorageID";
'''
        qry = qry.format(self.schema)
        return qry

    def pg_storage_calculator(self, slices=10):
        qry = '''
CREATE OR REPLACE FUNCTION "{0}".storage_calculator (slices integer)
    RETURNS VOID AS
$BODY$
DECLARE
    c cursor FOR SELECT * FROM "{0}"."StorageAreas";
    r "{0}"."StorageAreas"%ROWTYPE;
    area double precision;
    emin double precision;
    emax double precision;
    h double precision;
    lev double precision;
    vol double precision;
BEGIN
    FOR r IN c LOOP
        area := (SELECT dtm."CellSize" FROM "{0}"."DTMs" AS dtm WHERE dtm."DtmID" = r."DtmID")^2;
        emin := (SELECT MIN("Elevation") FROM "{0}"."SASurface" WHERE "StorageID" = r."StorageID");
        emax := (SELECT CASE WHEN r."UserElev" IS NULL THEN MAX("Elevation") ELSE r."UserElev" END FROM "{0}"."SASurface" WHERE "StorageID" = r."StorageID");
        h := (emax-emin)/slices;
        lev := emin+h;
        vol := 0;
        INSERT INTO "{0}"."SAVolume" VALUES (r."StorageID", emin, vol);
        FOR i IN 1..slices LOOP
            vol := vol + (SELECT COUNT("Elevation")*area*h FROM "{0}"."SASurface" WHERE "StorageID" = r."StorageID" AND "Elevation" <= lev+h);
            INSERT INTO "{0}"."SAVolume" ("StorageID", "level", "volume")
            SELECT r."StorageID", lev, vol;
            lev := lev+h;
        END LOOP;
    END LOOP;
END;
$BODY$
    LANGUAGE plpgsql;


SELECT "{0}".storage_calculator ({1});
'''
        qry = qry.format(self.schema, slices)
        return qry


class SASurface(HecRasObject):
    def __init__(self):
        super(SASurface, self).__init__()
        self.order = 25
        self.main = False
        self.visible = False
        self.spatial_index = False
        self.geom_type = 'POINT'
        self.attrs = [
            ('"StorageID"', 'integer'),
            ('"Elevation"', 'double precision')]


class SAVolume(HecRasObject):
    def __init__(self):
        super(SAVolume, self).__init__()
        self.order = 27
        self.visible = False
        self.spatial_index = False
        self.attrs = [
            ('"StorageID"', 'integer'),
            ('"level"', 'double precision'),
            ('"volume"', 'double precision')]


class SAConnections(HecRasObject):
    def __init__(self):
        super(SAConnections, self).__init__()
        self.order = 14
        self.geom_type = 'LINESTRING'
        self.attrs = [
            ('"SAConnID"', 'serial primary key'),
            ('"USSA"', 'integer'),
            ('"DSSA"', 'integer'),
            ('"TopWidth"', 'double precision'),
            ('"NodeName"', 'text'),
            ('"DtmID"', 'integer')]

    def pg_assign_nearest_sa(self):
        qry = '''
WITH distances AS
    (SELECT
        "StorageID",
        ST_Distance(sa.geom, ST_StartPoint(sac.geom)) AS usdist,
        ST_Distance(sa.geom, ST_EndPoint(sac.geom)) AS dsdist
    FROM
        "{0}"."StorageAreas" AS sa,
        "{0}"."SAConnections" AS sac)
UPDATE "{0}"."SAConnections"
SET
    "USSA" = (SELECT "StorageID" FROM distances ORDER BY usdist LIMIT 1),
    "DSSA" = (SELECT "StorageID" FROM distances ORDER BY dsdist LIMIT 1)
'''
        qry = qry.format(self.schema)
        return qry

    def pg_surface_points(self):
        qry = '''
WITH line AS
    (SELECT
        sac."SAConnID" AS "SAConnID",
        dtm."CellSize" AS "CellSize",
        (ST_Dump(sac.geom)).geom AS geom
    FROM
        "{0}"."SAConnections" AS sac,
        "{0}"."DTMs" AS dtm
    WHERE
        sac."DtmID" = dtm."DtmID"),
    linemeasure AS
    (SELECT
        "SAConnID",
        ST_AddMeasure(line.geom, 0, ST_Length(line.geom)) AS linem,
        generate_series(0, (ST_Length(line.geom)*100)::int, (line."CellSize"*100)::int) AS "Station"
    FROM line),
    geometries AS
    (SELECT
        "SAConnID",
        "Station",
        (ST_Dump(ST_GeometryN(ST_LocateAlong(linem, "Station"/100), 1))).geom AS geom
    FROM linemeasure)

    INSERT INTO "{0}"."SACSurface" (geom, "SAConnID", "Station")
    SELECT
        ST_SetSRID(ST_MakePoint(ST_X(geom), ST_Y(geom)), {1}) AS geom,
        "SAConnID",
        "Station"/100
    FROM geometries;

    INSERT INTO "{0}"."SACSurface" (geom, "SAConnID", "Station")
    SELECT
        ST_Endpoint(geom),
        "SAConnID",
        ST_Length(geom)
    FROM "{0}"."SAConnections";
'''
        qry = qry.format(self.schema, self.srid)
        return qry


class SACSurface(HecRasObject):
    def __init__(self):
        super(SACSurface, self).__init__()
        self.order = 26
        self.main = False
        self.visible = False
        self.spatial_index = False
        self.geom_type = 'POINT'
        self.attrs = [
            ('"PtID"', 'bigserial primary key'),
            ('"SAConnID"', 'integer'),
            ('"Station"', 'double precision'),
            ('"Elevation"', 'double precision')]


class DTMs(HecRasObject):
    def __init__(self):
        super(DTMs, self).__init__()
        self.order = 1
        self.main = False
        self.geom_type = 'POLYGON'
        self.attrs = [
            ('"DtmID"', 'bigserial primary key'),
            ('"Name"', 'text'),
            ('"DtmUri"', 'text'),
            ('"Provider"', 'text'),
            ('"LayerID"', 'text'),
            ('"CellSize"', 'double precision')]


class FlowAreas2d(HecRasObject):
    def __init__(self):
        super(FlowAreas2d, self).__init__()
        self.order = -5
        self.geom_type = 'POLYGON'
        self.attrs = [
            ('"AreaID"', 'serial primary key'),
            ('"Name"', 'text'),
            ('"CellSize"', 'double precision')]


class BreakLines2d(HecRasObject):
    def __init__(self):
        super(BreakLines2d, self).__init__()
        self.order = -4
        self.geom_type = 'LINESTRING'
        self.attrs = [
            ('"BLID"', 'serial primary key'),
            ('"AreaID"', 'integer'),
            ('"CellSizeAlong"', 'double precision'),
            ('"CellSizeAcross"', 'double precision'),
            ('"RowsAligned"', 'integer')]

    def pg_flow_to_breakline(self):
        qry = '''
WITH ids AS
    (SELECT
        a."AreaID",
        l."BLID"
    FROM
        "{0}"."BreakLines2d" AS l,
        "{0}"."FlowAreas2d" AS a
    WHERE
        ST_Contains(a.geom, l.geom))

UPDATE "{0}"."BreakLines2d" AS l
SET
    "AreaID" = ids."AreaID"
FROM
    ids
 WHERE
    ids."BLID" = l."BLID";
'''
        qry = qry.format(self.schema)
        return qry

    def pg_breaklines_m(self):
        qry = '''
DROP TABLE IF EXISTS "{0}"."BreakLines2d_m";

CREATE TABLE "{0}"."BreakLines2d_m"
    ("BLmID" serial primary key,
    "AreaID" integer,
    "CellSizeAlong" double precision,
    "CellSizeAcross" double precision,
    "RowsAligned" integer,
    geom geometry(LINESTRINGM, {1}));

INSERT INTO "{0}"."BreakLines2d_m"
    ("AreaID",
    "CellSizeAlong",
    "CellSizeAcross",
    "RowsAligned",
    geom)
SELECT
    "AreaID",
    "CellSizeAlong",
    "CellSizeAcross",
    "RowsAligned",
    (ST_Dump(ST_AddMeasure(geom, 0, ST_Length(geom)))).geom
FROM
    "{0}"."BreakLines2d";
'''
        qry = qry.format(self.schema, self.srid)
        return qry

    def pg_drop_by_buffer(self):
        qry = '''
WITH brbuf AS
    (SELECT
        ST_Buffer(geom, "RowsAligned" * "CellSizeAcross" + "CellSizeAlong" * 0.2, \'endcap=flat join=round\') AS geom
    FROM
        "{0}"."BreakLines2d_m")
DELETE FROM
    "{0}"."MeshPoints2d" AS p
USING
    brbuf
WHERE
    ST_Intersects(brbuf.geom, p.geom);
'''
        qry = qry.format(self.schema)
        return qry


class BreakPoints2d(HecRasObject):
    def __init__(self):
        super(BreakPoints2d, self).__init__()
        self.order = -2
        self.geom_type = 'POINT'
        self.attrs = [
            ('"BPID"', 'serial primary key'),
            ('"AreaID"', 'integer'),
            ('"BLmID"', 'integer'),
            ('"Fraction"', 'double precision')]

    def pg_bpoints_along_blines(self, tolerance=None, func_name=None):
        qry = '''
WITH ids AS
    (SELECT
        b."BLmID",
        p."BPID",
        b."AreaID"
    FROM
        "{0}"."BreakLines2d_m" AS b,
        "{0}"."BreakPoints2d" AS p
    WHERE
        ST_Buffer(p.geom, {1}) && b.geom AND
        ST_Contains(ST_Buffer(b.geom, {1}), p.geom))
UPDATE
    "{0}"."BreakPoints2d" AS p
SET
    "BLmID" = ids."BLmID",
    "AreaID" = ids."AreaID"
FROM
    ids
WHERE
    ids."BPID" = p."BPID";

UPDATE
    "{0}"."BreakPoints2d" AS p
SET
    "Fraction" = {2}(b.geom, p.geom)
FROM
    "{0}"."BreakLines2d_m" AS b
WHERE
    p."BLmID" = b."BLmID";
'''
        qry = qry.format(self.schema, tolerance, func_name)
        return qry


class MeshPoints2d(HecRasObject):
    def __init__(self):
        super(MeshPoints2d, self).__init__()
        self.order = -1
        self.main = False
        self.visible = False
        self.geom_type = 'POINT'
        self.attrs = [
            ('"MPID"', 'serial primary key'),
            ('"AreaID"', 'integer'),
            ('"BLID"', 'integer'),
            ('"CellSize"', 'double precision')]

    def pg_create_mesh(self):
        qry = '''
CREATE OR REPLACE FUNCTION "{0}".makegrid(geometry, float, integer)
    RETURNS geometry AS
$BODY$
    SELECT
        ST_Collect(ST_SetSRID(ST_POINT(x/1000000::float, y/1000000::float), $3))
    FROM
        generate_series(floor(st_xmin($1)*1000000)::bigint, ceiling(st_xmax($1)*1000000)::bigint, ($2*1000000)::bigint) AS x,
        generate_series(floor(st_ymin($1)*1000000)::bigint, ceiling(st_ymax($1)*1000000)::bigint, ($2*1000000)::bigint) AS y
    WHERE
        ST_Intersects($1, ST_SetSRID(ST_POINT(x/1000000::float, y/1000000::float), $3))
$BODY$
    LANGUAGE sql;

------------------------------------------------------------------------------------------------------------------------
INSERT INTO
    "{0}"."MeshPoints2d" ("AreaID", "BLID", geom)
SELECT
    "AreaID",
    -1,
    (ST_Dump("{0}".makegrid(geom, "CellSize", {1}))).geom AS geom
FROM
    "{0}"."FlowAreas2d";

WITH areas2dshrinked AS
    (SELECT
        "AreaID",
        ST_Buffer(a2d.geom, -0.3 * a2d."CellSize") AS geom
    FROM
        "{0}"."FlowAreas2d" AS a2d)
DELETE FROM
    "{0}"."MeshPoints2d" AS pts_a
WHERE
    pts_a."MPID" NOT IN
        (SELECT
            pts."MPID"
        FROM
            "{0}"."MeshPoints2d" AS pts,
            areas2dshrinked
        WHERE
            ST_Intersects(pts.geom, areas2dshrinked.geom));

DROP FUNCTION IF EXISTS "{0}".makegrid(geometry, float, integer);
'''
        qry = qry.format(self.schema, self.srid)
        return qry

    def pg_aligned_mesh(self, cellsize=None, measure=None, offset=None, blid=None):
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
'''
        qry = qry.format(self.schema, cellsize, measure, offset, blid)
        return qry

    def pg_clean_points(self):
        qry = '''
DELETE FROM
    "{0}"."MeshPoints2d" AS p1
USING
    "{0}"."MeshPoints2d" AS p2
WHERE
    p1."BLID" <> -1 AND
    p2."BLID" <> -1 AND
    p1."BLID" <> p2."BLID" AND
    p1."MPID" > p2."MPID" AND
    ST_DWithin(p1.geom, p2.geom, 0.75 * LEAST(p1."CellSize", p2."CellSize"));

DELETE FROM
    "{0}"."MeshPoints2d" AS p
USING
    "{0}"."FlowAreas2d" AS a
WHERE
    a."AreaID" = p."AreaID" AND
    NOT ST_Contains(ST_Buffer(a.geom, -0.3*a."CellSize"), p.geom);

DROP TABLE IF EXISTS "{0}"."BreakLines2d_m";
'''
        qry = qry.format(self.schema)
        return qry


class Bathymetry(HecRasObject):
    def __init__(self):
        super(Bathymetry, self).__init__()
        self.order = -3
        self.main = False
        self.visible = False
        self.geom_type = 'POINT'
        self.attrs = [
            ('"BID"', 'serial primary key'),
            ('"XsecID"', 'integer'),
            ('"Station"', 'double precision'),
            ('"Elevation"', 'double precision')]


class BathymetryExtents(HecRasObject):
    def __init__(self):
        super(BathymetryExtents, self).__init__()
        self.order = -6
        self.main = False
        self.visible = False
        self.geom_type = 'POLYGON'
        self.attrs = [
            ('"BID"', 'serial primary key')]
