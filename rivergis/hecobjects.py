# -*- coding: utf-8 -*-

__author__ = 'Łukasz Dębek'


class HecRasObject(object):
    """
    Class for HEC-RAS geometry objects processing.
    """
    SCHEMA = None
    SRID = None

    def __init__(self):
        self.schema = self.SCHEMA
        self.srid = self.SRID
        self.name = self.__class__.__name__
        self.geom_type = None
        self.attrs = None

    def pg_create_table(self):
        schema_name = '"{0}"."{1}"'.format(self.schema, self.name)
        attrs = ['geom geometry({0}, {1})'.format(self.geom_type, self.srid)]
        attrs += [' '.join(field) for field in self.attrs]
        qry = 'DROP TABLE IF EXISTS {0};\nCREATE TABLE {1}(\n\t{2});\n'.format(schema_name, schema_name, ',\n\t'.join(attrs))
        qry += 'SELECT create_spatial_index(\'{0}\', \'{1}\')'.format(self.schema, self.name)
        return qry


class StreamCenterlines(HecRasObject):
    """
    Geometry and table.
    """
    def __init__(self):
        super(StreamCenterlines, self).__init__()
        self.hdf_dataset = u'River Centerlines'
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
DROP TABLE IF EXISTS "{0}"."NodesTable";
CREATE TABLE "{0}"."NodesTable"(
    geom geometry(POINT, {1}),
    "NodeID" serial primary key,
    "X" double precision,
    "Y" double precision);
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
    UPDATE "{0}"."StreamCenterlines" SET
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
        qry = qry.format(self.schema, self.srid)
        return qry

    def pg_lengths_stations(self):
        qry = '''
CREATE TABLE "{0}".tmp1 AS
SELECT "RiverCode", "ReachCode", ST_StartPoint(geom) AS geom, 'start' AS typ_punktu
FROM "{0}"."StreamCenterlines"
UNION ALL
SELECT "RiverCode", "ReachCode", ST_EndPoint(geom) AS geom, 'end' AS typ_punktu
FROM "{0}"."StreamCenterlines";

CREATE TABLE "{0}".tmp2 AS
SELECT "RiverCode", geom
FROM "{0}".tmp1
GROUP BY "RiverCode", geom
HAVING COUNT(geom) = 1;

DROP TABLE IF EXISTS "{0}"."Endpoints";
SELECT tmp1.geom::geometry(POINT, {1}), tmp1."RiverCode", tmp1."ReachCode", "NodesTable"."NodeID" INTO "{0}"."Endpoints"
FROM "{0}".tmp1, "{0}".tmp2, "{0}"."NodesTable"
WHERE tmp1."RiverCode" = tmp2."RiverCode" AND tmp1.geom = tmp2.geom AND tmp1.typ_punktu = 'end' AND tmp1.geom = "NodesTable".geom;

DROP TABLE "{0}".tmp1;
DROP TABLE "{0}".tmp2;
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
BEGIN
FOR r IN c LOOP
    river := r."RiverCode";
    tonode_id := r."NodeID";
    fromsta := 0;
    tosta := 0;
    FOR i in 1..(SELECT COUNT(*) FROM "{0}"."StreamCenterlines" WHERE "StreamCenterlines"."RiverCode" = river) LOOP
        SELECT "FromNode", ST_Length(geom) INTO fromnode_id, len FROM "{0}"."StreamCenterlines" WHERE "RiverCode" = river AND "ToNode" = tonode_id;
        tosta := fromsta + len;
        UPDATE {0}."StreamCenterlines" SET
        "ReachLen" = len,
        "FromSta" = fromsta,
        "ToSta" = tosta
        WHERE "RiverCode" = river AND "ToNode" = tonode_id;
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
        qry = qry.format(self.schema, self.srid)
        return qry


class XSCutLines(HecRasObject):
    """
    Geometry and table.
    """
    def __init__(self):
        super(XSCutLines, self).__init__()
        self.hdf_dataset = u'Cross Sections'
        self.geom_type = 'LINESTRING'
        self.attrs = [
            ('"XsecID"', 'serial primary key'),
            ('"ReachID"', 'integer'),
            ('"Nr"', 'integer'),
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
UPDATE {0}."XSCutLines" AS xs
SET
  "ReachID" = riv."ReachID",
  "RiverCode" = riv."RiverCode",
  "ReachCode" = riv."ReachCode"
FROM
  {0}."StreamCenterlines" AS riv
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
------------------------------------------------------------------------------------------------------------------------
WITH orderedXsecs AS (
SELECT
    "XsecID",
    xs."ReachID",
    rank() OVER (PARTITION BY xs."RiverCode" ORDER BY xs."Station" ASC) AS rank
  FROM
    "{0}"."XSCutLines" AS xs
  LEFT JOIN
    "{0}"."StreamCenterlines" sc ON  sc."ReachID" = xs."ReachID"
)
UPDATE "{0}"."XSCutLines" xs
  SET
    "Nr" = rank
  FROM
    orderedXsecs ox
  WHERE
    xs."XsecID" = ox."XsecID";
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


    def pg_downstream_reach_lengths(self):
        qry = '''
DROP TABLE IF EXISTS "{0}"."FlowpathStations";
------------------------------------------------------------------------------------------------------------------------
CREATE TABLE "{0}"."FlowpathStations" (
  "XsecID" integer primary key,
  "RiverCode" text,
  "Nr" integer,
  "LeftSta" double precision,
  "ChanSta" double precision,
  "RightSta" double precision);

------------------------------------------------------------------------------------------------------------------------
INSERT INTO "{0}"."FlowpathStations"
  ("XsecID", "RiverCode", "Nr")
SELECT
  xs."XsecID",
  sc."RiverCode",
  xs."Nr"
FROM
  "{0}"."XSCutLines" AS xs
  LEFT JOIN "{0}"."StreamCenterlines" AS sc ON xs."ReachID" = sc."ReachID";

------------------------------------------------------------------------------------------------------------------------
WITH xspts AS (
  SELECT
    xs."XsecID" AS "XsecID",
    path."LineType" AS "LineType",
    ST_LineLocatePoint(path.geom, ST_Intersection(xs.geom, path.geom)) * ST_Length(path.geom) AS "Station"
  FROM
    "{0}"."Flowpaths" AS path,
    "{0}"."XSCutLines" AS xs
  WHERE
    path."LineType" = 'Channel' AND
    xs.geom && path.geom AND
    ST_Intersects(xs.geom, path.geom)
)
UPDATE "{0}"."FlowpathStations" AS flowsta
SET
  "ChanSta" = xspts."Station"
FROM
  xspts
WHERE
  xspts."XsecID" = flowsta."XsecID";

------------------------------------------------------------------------------------------------------------------------
WITH xspts AS (
  SELECT
    xs."XsecID" AS "XsecID",
    path."LineType" AS "LineType",
    ST_LineLocatePoint(path.geom, ST_Intersection(xs.geom, path.geom)) * ST_Length(path.geom) AS "Station"
  FROM
    "{0}"."Flowpaths" AS path,
    "{0}"."XSCutLines" AS xs
  WHERE
    path."LineType" = 'Left' AND
    xs.geom && path.geom AND
    ST_Intersects(xs.geom, path.geom)
)
UPDATE "{0}"."FlowpathStations" AS flowsta
SET
  "LeftSta" = xspts."Station"
FROM
  xspts
WHERE
  xspts."XsecID" = flowsta."XsecID";

------------------------------------------------------------------------------------------------------------------------
WITH xspts AS (
  SELECT
    xs."XsecID" AS "XsecID",
    path."LineType" AS "LineType",
    ST_LineLocatePoint(path.geom, ST_Intersection(xs.geom, path.geom)) * ST_Length(path.geom) AS "Station"
  FROM
    "{0}"."Flowpaths" AS path,
    "{0}"."XSCutLines" AS xs
  WHERE
    path."LineType" = 'Right' AND
    xs.geom && path.geom AND
    ST_Intersects(xs.geom, path.geom)
)
UPDATE "{0}"."FlowpathStations" AS flowsta
SET
  "RightSta" = xspts."Station"
FROM
  xspts
WHERE
  xspts."XsecID" = flowsta."XsecID";

------------------------------------------------------------------------------------------------------------------------
WITH xsdata AS (
SELECT
  x."XsecID",
  s."RiverCode"
FROM
  "{0}"."XSCutLines" AS x
  LEFT JOIN "{0}"."StreamCenterlines" AS s ON x."ReachID" = s."ReachID"
)
UPDATE "{0}"."XSCutLines" AS xs
SET
  "LLength" = abs(nfs."LeftSta" - flowsta."LeftSta"),
  "ChLength" = abs(nfs."ChanSta" - flowsta."ChanSta"),
  "RLength" = abs(nfs."RightSta" - flowsta."RightSta")
FROM
  xsdata,
  "{0}"."FlowpathStations" AS flowsta,
  "{0}"."FlowpathStations" AS nfs
WHERE
  xs."Nr" > 1 AND
  xs."XsecID" = xsdata."XsecID" AND
  xsdata."RiverCode" = flowsta."RiverCode" AND
  flowsta."RiverCode" = nfs."RiverCode" AND
  xs."XsecID" = flowsta."XsecID" AND
  xs."Nr" = flowsta."Nr" AND
  xs."Nr" = nfs."Nr" + 1;

------------------------------------------------------------------------------------------------------------------------
UPDATE "{0}"."XSCutLines" AS xs
SET
  "LLength" = 0,
  "ChLength" = 0,
  "RLength" = 0
WHERE
  xs."Nr" = 1;
'''
        qry = qry.format(self.schema)
        return qry


class BankLines(HecRasObject):
    """
    Geometry and table.
    """
    def __init__(self):
        super(BankLines, self).__init__()
        self.hdf_dataset = u'River Bank Lines'
        self.geom_type = 'LINESTRING'
        self.attrs = [('"BankID"', 'serial primary key')]


class BankPoints(HecRasObject):
    """
    Geometry and table.
    """
    def __init__(self):
        super(BankPoints, self).__init__()
        self.hdf_dataset = u'River Bank Lines'
        self.geom_type = 'POINT'
        self.attrs = [('"BankID"', 'serial primary key')]


class Flowpaths(HecRasObject):
    """
    Geometry only in PostGIS.
    Table in PostGIS and HDF (Cross Sections dataset).
    StreamCenterline and XSCutLines objects must exist.
    """
    def __init__(self):
        super(Flowpaths, self).__init__()
        self.hdf_dataset = None
        self.geom_type = 'LINESTRING'
        self.attrs = [('"FpID"', 'serial primary key'),
                      ('"LineType"', 'text')]

    def pg_get_flowpaths_linetype(self):
        qry = '''
SELECT "LineType" FROM "{0}"."Flowpaths";
'''
        qry = qry.format(self.schema)
        return qry


class Bridges(HecRasObject):
    def __init__(self):
        super(Bridges, self).__init__()
        self.hdf_dataset = u'Structures'
        self.geom_type = 'LINESTRING'
        self.attrs = [
            ('"BridgeID"', 'serial primary key'),
            ('"RiverCode"', 'text'),
            ('"ReachCode"', 'text'),
            ('"Station"', 'double precision'),
            ('"USDistance"', 'double precision'),
            ('"TopWidth"', 'double precision'),
            ('"NodeName"', 'text')]


class IneffAreas(HecRasObject):
    def __init__(self):
        super(IneffAreas, self).__init__()
        self.hdf_dataset = None
        self.geom_type = 'POLYGON'
        self.attrs = [('"IneffID"', 'serial primary key'),
            ('"Elevation"', 'double precision')]


class BlockedObs(HecRasObject):
    def __init__(self):
        super(BlockedObs, self).__init__()
        self.hdf_dataset = None
        self.geom_type = 'POLYGON'
        self.attrs = [('"BlockID"', 'serial primary key'),
            ('"Elevation"', 'double precision')]


class LanduseAreas(HecRasObject):
    def __init__(self):
        super(LanduseAreas, self).__init__()
        self.hdf_dataset = None
        self.geom_type = 'MULTIPOLYGON'
        self.attrs = [
            ('"LUID"', 'serial primary key'),
            ('"LUCode"', 'text'),
            ('"N_Value"', 'double precision')]


class LeveeAlignment(HecRasObject):
    def __init__(self):
        super(LeveeAlignment, self).__init__()
        self.hdf_dataset = None
        self.geom_type = 'LINESTRING'
        self.attrs = [('"LeveeID"', 'serial primary key')]


class LeveePoints(HecRasObject):
    def __init__(self):
        super(LeveePoints, self).__init__()
        self.hdf_dataset = None
        self.geom_type = 'POINTS'
        self.attrs = [
            ('"LeveeID"', 'serial primary key'),
            ('"Station"', 'integer'),
            ('"Elevation"', 'integer')]


class InlineStructures(HecRasObject):
    def __init__(self):
        super(InlineStructures, self).__init__()
        self.hdf_dataset = u'Structures'
        self.geom_type = 'LINESTRING'
        self.attrs = [
            ('"InlineStrID"', 'serial primary key'),
            ('"RiverCode"', 'text'),
            ('"ReachCode"', 'text'),
            ('"Station"', 'double precision'),
            ('"USDistance"', 'double precision'),
            ('"TopWidth"', 'double precision'),
            ('"NodeName"', 'text')]


class LateralStructures(HecRasObject):
    def __init__(self):
        super(LateralStructures, self).__init__()
        self.hdf_dataset = u'Structures'
        self.geom_type = 'LINESTRING'
        self.attrs = [
            ('"LateralStrID"', 'serial primary key'),
            ('"RiverCode"', 'text'),
            ('"ReachCode"', 'text'),
            ('"Station"', 'double precision'),
            ('"USDistance"', 'double precision'),
            ('"TopWidth"', 'double precision'),
            ('"NodeName"', 'text')]


class StorageAreas(HecRasObject):
    def __init__(self):
        super(StorageAreas, self).__init__()
        self.hdf_dataset = None
        self.geom_type = 'POLYGON'
        self.attrs = [
            ('"StorageID"', 'serial primary key'),
            ('"MaxElev"', 'double precision'),
            ('"MinElev"', 'double precision'),
            ('"UserElev"', 'double precision')]


class SAConnections(HecRasObject):
    def __init__(self):
        super(SAConnections, self).__init__()
        self.hdf_dataset = None
        self.geom_type = 'POLYGON'
        self.attrs = [
            ('"SAconID"', 'serial primary key'),
            ('"USSA"', 'integer'),
            ('"DSSA"', 'integer'),
            ('"TopWidth"', 'double precision')]


class StreamCenterlines3D(StreamCenterlines):
    def __init__(self):
        super(StreamCenterlines3D, self).__init__()


class XSCutLines3D(XSCutLines):
    def __init__(self):
        super(XSCutLines3D, self).__init__()


class Bridges3D(Bridges):
    def __init__(self):
        super(Bridges3D, self).__init__()
