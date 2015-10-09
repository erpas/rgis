# -*- coding: utf-8 -*-

__author__ = 'Łukasz Dębek'


class HecRasObject(object):
    """
    Class for HEC-RAS geometry objects processing.
    """
    SCHEMA = None
    SRID = None
    OVERWRITE = True

    def __init__(self):
        self.main = True
        self.visible = True
        self.spatial_index = True
        self.schema = self.SCHEMA
        self.srid = self.SRID
        self.name = self.__class__.__name__
        self.geom_type = None
        self.attrs = None

    def pg_create_table(self):
        schema_name = '"{0}"."{1}"'.format(self.schema, self.name)
        attrs = ['geom geometry({0}, {1})'.format(self.geom_type, self.srid)]
        attrs += [' '.join(field) for field in self.attrs]
        if self.OVERWRITE is True:
            qry = 'DROP TABLE IF EXISTS {0};\nCREATE TABLE {1}(\n\t{2});\n'.format(schema_name, schema_name, ',\n\t'.join(attrs))
        else:
            qry = 'CREATE TABLE {0}(\n\t{1});\n'.format(schema_name, ',\n\t'.join(attrs))
        if self.spatial_index is True:
            qry += 'SELECT create_spatial_index(\'{0}\', \'{1}\');'.format(self.schema, self.name)
        else:
            pass
        return qry


class StreamCenterlines(HecRasObject):
    def __init__(self):
        super(StreamCenterlines, self).__init__()
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
CREATE TABLE "{0}".tmp1 AS
SELECT "RiverCode", "ReachCode", ST_StartPoint(geom) AS geom, 'start' AS point_type
FROM "{0}"."StreamCenterlines"
UNION ALL
SELECT "RiverCode", "ReachCode", ST_EndPoint(geom) AS geom, 'end' AS point_type
FROM "{0}"."StreamCenterlines";

CREATE TABLE "{0}".tmp2 AS
SELECT "RiverCode", geom
FROM "{0}".tmp1
GROUP BY "RiverCode", geom
HAVING COUNT(geom) = 1;

INSERT INTO "{0}"."Endpoints"(geom, "RiverCode", "ReachCode", "NodeID")
SELECT
    tmp1.geom,
    tmp1."RiverCode",
    tmp1."ReachCode",
    "NodesTable"."NodeID"
FROM
    "{0}".tmp1,
    "{0}".tmp2,
    "{0}"."NodesTable"
WHERE
    tmp1."RiverCode" = tmp2."RiverCode" AND
    tmp1.geom = tmp2.geom AND
    tmp1.point_type = 'end' AND
    tmp1.geom = "NodesTable".geom;

DROP TABLE
    "{0}".tmp1,
    "{0}".tmp2;
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
        self.main = False
        self.spatial_index = False
        self.geom_type = 'POINT'
        self.attrs = [
            ('"NodeID"', 'serial primary key'),
            ('"X"', 'double precision'),
            ('"Y"', 'double precision')]


class Endpoints(HecRasObject):
    def __init__(self):
        super(Endpoints, self).__init__()
        self.main = False
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
  xs.geom && riv.geom AND
  ST_Intersects(xs.geom, riv.geom);
'''
        qry = qry.format(self.schema)
        return qry

    def pg_stationing(self):
        qry = '''
WITH xspts AS (
  SELECT
    xs."XsecID" AS "XsecID",
    riv."ReachID" AS "ReachID",
    ST_LineLocatePoint(riv.geom, ST_Intersection(xs.geom, riv.geom)) AS "Fraction"
  FROM
    "{0}"."StreamCenterlines" AS riv,
    "{0}"."XSCutLines" AS xs
  WHERE
    xs.geom && riv.geom AND
    ST_Intersects(xs.geom, riv.geom)
)
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
WITH bankpts AS (
  SELECT
    xs."XsecID" AS "XsecID",
    ST_LineLocatePoint(xs.geom, ST_Intersection(xs.geom, bl.geom)) AS "Fraction"
  FROM
    "{0}"."BankLines" AS bl,
    "{0}"."XSCutLines" AS xs
  WHERE
    xs.geom && bl.geom AND
    ST_Intersects(xs.geom, bl.geom)
)
UPDATE "{0}"."XSCutLines" AS xs
SET
  "LeftBank" = minmax."minFrac",
  "RightBank" = minmax."maxFrac"
FROM
  (
  SELECT
    "XsecID",
    min("Fraction") AS "minFrac",
    max("Fraction") AS "maxFrac"
  FROM
    bankpts AS bp
  GROUP BY "XsecID"
  ) minmax
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
'''.format(self.schema)
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
        r.geom && path.geom AND
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


class XSSurface(HecRasObject):
    def __init__(self):
        super(XSSurface, self).__init__()
        self.main = False
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
        self.geom_type = 'LINESTRING'
        self.attrs = [('"BankID"', 'serial primary key')]


class BankPoints(HecRasObject):
    def __init__(self):
        super(BankPoints, self).__init__()
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
    (SELECT (ST_Dump(geom)).geom AS geom, 'Channel'
    FROM (SELECT ST_LineMerge(ST_Union(geom)) AS geom
        FROM "{0}"."StreamCenterlines"
        WHERE "ReachCode" IS NOT NULL
        GROUP BY "RiverCode") AS river_union);
'''
        qry = qry.format(self.schema)
        return qry


class IneffAreas(HecRasObject):
    def __init__(self):
        super(IneffAreas, self).__init__()
        self.geom_type = 'POLYGON'
        self.attrs = [
            ('"IneffID"', 'serial primary key'),
            ('"Elevation"', 'double precision')]

    def pg_ineffective_positions(self):
        qry = '''
INSERT INTO "{0}"."IneffLines"(geom, "XsecID", "IneffID", "Elevation")
SELECT
    ST_Intersection(xs.geom, ineff.geom) as geom,
    xs."XsecID",
    ineff."IneffID",
    ineff."Elevation"
FROM
    "{0}"."XSCutLines" AS xs,
    "{0}"."IneffAreas" AS ineff
WHERE
    xs.geom && ineff.geom AND
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
        self.geom_type = 'POLYGON'
        self.attrs = [
            ('"BlockID"', 'serial primary key'),
            ('"Elevation"', 'double precision')]

    def pg_blocked_positions(self):
        qry = '''
INSERT INTO "{0}"."BlockLines"(geom, "XsecID", "BlockID", "Elevation")
SELECT
    ST_Intersection(xs.geom, block.geom) as geom,
    xs."XsecID",
    block."BlockID",
    block."Elevation"
FROM
    "{0}"."XSCutLines" AS xs,
    "{0}"."BlockedObs" AS block
WHERE
    xs.geom && block.geom AND
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
DROP TABLE IF EXISTS "{0}"."Manning";

SELECT "LUID", "LUCode", "N_Value", ST_AsText((ST_Dump(geom)).geom) AS geom
INTO "{0}".ludump
FROM "{0}"."LanduseAreas";

ALTER TABLE "{0}".ludump
ALTER COLUMN geom TYPE geometry(POLYGON, {1})
USING ST_SetSRID(geom, {1});

CREATE INDEX idx_ludump
ON "{0}".ludump
USING gist(geom);

------------------------------------------------------------------------------------------------------------------------
SELECT "XSCutLines"."XsecID", ludump."N_Value", ludump."LUCode", ST_Intersection(ludump.geom, "XSCutLines".geom) AS geom
INTO "{0}".intercrossection
FROM "{0}".ludump, "{0}"."XSCutLines"
WHERE
    ludump.geom && "XSCutLines".geom AND
    ST_Intersects(ludump.geom, "XSCutLines".geom)
ORDER BY "XSCutLines"."XsecID";

SELECT "XsecID","N_Value","LUCode" ,ST_AsText((ST_Dump(geom)).geom) AS geom
INTO "{0}".intercrossectiondump
FROM "{0}".intercrossection;


ALTER TABLE "{0}".intercrossectiondump
ALTER COLUMN geom TYPE geometry(LINESTRING, {1})
USING ST_SetSRID(geom, {1});

CREATE INDEX idx_intercrossectiondump
ON"{0}".intercrossectiondump
USING gist(geom);

------------------------------------------------------------------------------------------------------------------------
-- Multilinestring to line string --
------------------------------------------------------------------------------------------------------------------------
SELECT "XsecID", ST_AsText((ST_Dump("XSCutLines".geom)).geom) AS geom
INTO "{0}".single_line
FROM "{0}"."XSCutLines"
ORDER BY "XsecID";

ALTER TABLE "{0}".single_line
ALTER COLUMN geom TYPE geometry(LINESTRING, {1})
USING ST_SetSRID(geom, {1});

CREATE INDEX idx_single_line
ON "{0}".single_line
USING gist(geom);

------------------------------------------------------------------------------------------------------------------------
-- Creation of points on the line start points, 5 mm shifting for appropriate "N_Value" application    --
------------------------------------------------------------------------------------------------------------------------
SELECT "XsecID", "N_Value", "LUCode", ST_Line_Interpolate_Point(intercrossectiondump.geom, 0.00005) AS geom
INTO "{0}".shiftpoints
FROM "{0}".intercrossectiondump
ORDER BY "XsecID";

ALTER TABLE "{0}".shiftpoints
ALTER COLUMN geom TYPE geometry(POINT, {1})
USING ST_SetSRID(geom, {1});

CREATE INDEX idx_shiftpoints
ON "{0}".shiftpoints
USING gist(geom);

------------------------------------------------------------------------------------------------------------------------
-- Calculation of fraction along line cross sections  --
------------------------------------------------------------------------------------------------------------------------
SELECT  b."XsecID", b."N_Value", b."LUCode", ST_LineLocatePoint(a.geom,b.geom) AS "Fraction"
INTO "{0}".tempmann
FROM "{0}".single_line AS a, "{0}".shiftpoints AS b
WHERE a."XsecID" = b."XsecID"
ORDER BY "XsecID", "Fraction";

------------------------------------------------------------------------------------------------------------------------
-- Creation of table with Manning's coefficients  --
------------------------------------------------------------------------------------------------------------------------
SELECT
    "XsecID",
    CASE WHEN
        "Fraction" < 0.0001 THEN 0
    ELSE
        "Fraction"
    END AS "Fraction",
    "N_Value",
    "LUCode"
INTO "{0}"."Manning"
FROM "{0}".tempmann;

DROP TABLE
    "{0}".intercrossection,
    "{0}".intercrossectiondump,
    "{0}".single_line,
    "{0}".shiftpoints,
    "{0}".tempmann,
    "{0}".ludump;

------------------------------------------------------------------------------------------------------------------------
'''
        qry = qry.format(self.schema, self.srid)
        return qry


class LeveeAlignment(HecRasObject):
    def __init__(self):
        super(LeveeAlignment, self).__init__()
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
        xs.geom && lev.geom AND
        ST_Intersects(xs.geom, lev.geom);
'''
        qry = qry.format(self.schema)
        return qry


class LeveePoints(HecRasObject):
    def __init__(self):
        super(LeveePoints, self).__init__()
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
        self.geom_type = 'LINESTRING'
        self.attrs = [
            ('"BridgeID"', 'serial primary key'),
            ('"RiverCode"', 'text'),
            ('"ReachCode"', 'text'),
            ('"Station"', 'double precision'),
            ('"USDistance"', 'double precision'),
            ('"TopWidth"', 'double precision'),
            ('"NodeName"', 'text')]


class InlineStructures(HecRasObject):
    def __init__(self):
        super(InlineStructures, self).__init__()
        self.geom_type = 'LINESTRING'
        self.attrs = [
            ('"InlineSID"', 'serial primary key'),
            ('"RiverCode"', 'text'),
            ('"ReachCode"', 'text'),
            ('"Station"', 'double precision'),
            ('"USDistance"', 'double precision'),
            ('"TopWidth"', 'double precision'),
            ('"NodeName"', 'text')]


class LateralStructures(HecRasObject):
    def __init__(self):
        super(LateralStructures, self).__init__()
        self.geom_type = 'LINESTRING'
        self.attrs = [
            ('"LateralSID"', 'serial primary key'),
            ('"RiverCode"', 'text'),
            ('"ReachCode"', 'text'),
            ('"Station"', 'double precision'),
            ('"USDistance"', 'double precision'),
            ('"TopWidth"', 'double precision'),
            ('"NodeName"', 'text')]


class StorageAreas(HecRasObject):
    def __init__(self):
        super(StorageAreas, self).__init__()
        self.geom_type = 'POLYGON'
        self.attrs = [
            ('"StorageID"', 'serial primary key'),
            ('"MaxElev"', 'double precision'),
            ('"MinElev"', 'double precision'),
            ('"UserElev"', 'double precision')]


class SAConnections(HecRasObject):
    def __init__(self):
        super(SAConnections, self).__init__()
        self.geom_type = 'LINESTRING'
        self.attrs = [
            ('"SAconID"', 'serial primary key'),
            ('"USSA"', 'integer'),
            ('"DSSA"', 'integer'),
            ('"TopWidth"', 'double precision')]


class DTMs(HecRasObject):
    def __init__(self):
        super(DTMs, self).__init__()
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
        self.geom_type = 'POLYGON'
        self.attrs = [
            ('"AreaID"', 'serial primary key'),
            ('"Name"', 'text'),
            ('"CellSize"', 'double precision')]


class BreakLines2d(HecRasObject):
    def __init__(self):
        super(BreakLines2d, self).__init__()
        self.geom_type = 'LINESTRING'
        self.attrs = [
            ('"BLID"', 'serial primary key'),
            ('"AreaID"', 'integer'),
            ('"CellSizeAlong"', 'double precision'),
            ('"CellSizeAcross"', 'double precision'),
            ('"RowsAligned"', 'integer')]


class BreakPoints2d(HecRasObject):
    def __init__(self):
        super(BreakPoints2d, self).__init__()
        self.geom_type = 'POINT'
        self.attrs = [
            ('"BPID"', 'serial primary key'),
            ('"AreaID"', 'integer'),
            ('"BLID"', 'integer'),
            ('"Fraction"', 'double precision')]


class MeshPoints2d(HecRasObject):
    def __init__(self):
        super(MeshPoints2d, self).__init__()
        self.main = False
        self.geom_type = 'POINT'
        self.attrs = [
            ('"MPID"', 'serial primary key'),
            ('"AreaID"', 'integer'),
            ('"BLID"', 'integer'),
            ('"CellSize"', 'double precision')]

