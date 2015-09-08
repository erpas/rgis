__author__ = 'ldebek'

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
        qry = ['geom geometry({0}, {1})'.format(self.geom_type, self.srid)]
        qry += [' '.join(field) for field in self.attrs]
        qry = 'DROP TABLE IF EXISTS {0};\nCREATE TABLE {1}(\n\t{2});'.format(schema_name, schema_name, ',\n\t'.join(qry))
        return qry


class StreamCenterline(HecRasObject):
    """
    Geometry and table.
    """
    def __init__(self):
        super(StreamCenterline, self).__init__()
        self.hdf_dataset = u'River Centerlines'
        self.geom_type = 'LINESTRING'
        self.attrs = [
            ('"RiverID"', 'serial primary key'),
            ('"RiverCode"', 'text'),
            ('"ReachCode"', 'text'),
            ('"FromNode"', 'integer'),
            ('"ToNode"', 'integer'),
            ('"ArcLength"', 'double precision'),
            ('"FromSta"', 'double precision'),
            ('"ToSta"', 'double precision')]

    def pg_from_to_node(self):
        qry = '''
CREATE OR REPLACE FUNCTION "{0}".from_to_node ()
    RETURNS VOID AS
$BODY$
DECLARE
    c cursor FOR SELECT * FROM "{0}"."StreamCenterline";
    r "{0}"."StreamCenterline"%ROWTYPE;
    start_geom geometry;
    end_geom geometry;
    start_node integer := 0;
    end_node integer := 0;
    nr integer := 0;
BEGIN
DROP TABLE IF EXISTS "{0}"."NodesTable";
CREATE TABLE "{0}"."NodesTable"(
    geom geometry(POINT, 2180),
    "NodeID" serial primary key,
    "X" double precision,
    "Y" double precision);
FOR r in c LOOP
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
    UPDATE "{0}"."StreamCenterline" SET
    "FromNode" = start_node,
    "ToNode" = end_node
    WHERE CURRENT OF c;
END LOOP;
END;
$BODY$
    LANGUAGE plpgsql;

SELECT "{0}".from_to_node ();
DROP FUNCTION IF EXISTS "{0}".from_to_node ()
'''
        qry = qry.format(self.schema)
        return qry

    def pg_lengths_stations(self):
        qry = '''
CREATE OR REPLACE VIEW "{0}".pnts1 AS
SELECT "RiverCode", "ReachCode", ST_StartPoint(geom) AS geom, 'start' AS typ_punktu
FROM "{0}"."StreamCenterline"
UNION ALL
SELECT "RiverCode", "ReachCode", ST_EndPoint(geom) AS geom, 'end' AS typ_punktu
FROM "{0}"."StreamCenterline";

CREATE OR REPLACE VIEW "{0}".pnts2 AS
SELECT "RiverCode", geom
FROM "{0}".pnts1
GROUP BY "RiverCode", geom
HAVING COUNT(geom) = 1;

DROP TABLE IF EXISTS "{0}"."Endpoints";
SELECT pnts1."RiverCode", pnts1."ReachCode", pnts1.geom::geometry(POINT, 2180) INTO "{0}"."Endpoints"
FROM "{0}".pnts1, "{0}".pnts2
WHERE pnts1."RiverCode" = pnts2."RiverCode" AND pnts1.geom = pnts2.geom AND pnts1.typ_punktu = 'end';

DROP VIEW "{0}".pnts1 CASCADE;

SELECT * FROM "{0}"."StreamCenterline"
WHERE "StreamCenterline"."ReachCode" = ANY((SELECT "Endpoints"."ReachCode" FROM "{0}"."Endpoints"))
'''
        qry = qry.format(self.schema)
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
            ('"Station"', 'double precision'),
            ('"RiverCode"', 'text'),
            ('"ReachCode"', 'text'),
            ('"LeftBank"', 'double precision'),
            ('"RightBank"', 'double precision'),
            ('"Llength"', 'double precision'),
            ('"ChLength"', 'double precision'),
            ('"Rlength"', 'double precision'),
            ('"NodeName"', 'text')]


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
        self.attrs = [('"LineType"', 'text')]


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
        self.attrs = [('""IneffID"', 'serial primary key')]


class BlockedObs(HecRasObject):
    def __init__(self):
        super(BlockedObs, self).__init__()
        self.hdf_dataset = None
        self.geom_type = 'POLYGON'
        self.attrs = [('"BlockID"', 'serial primary key')]


class LanduseAreas(HecRasObject):
    def __init__(self):
        super(LanduseAreas, self).__init__()
        self.hdf_dataset = None
        self.geom_type = 'MULTIPOLYGON'
        self.attrs = [
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


class StreamCenterline3D(StreamCenterline):
    def __init__(self):
        super(StreamCenterline3D, self).__init__()


class XSCutLines3D(XSCutLines):
    def __init__(self):
        super(XSCutLines3D, self).__init__()


class Bridges3D(Bridges):
    def __init__(self):
        super(Bridges3D, self).__init__()


"""
class Junctions(HecRasObject):

    Only table.
    StreamCenterline and XSCutLines objects must exist.
    Length calculated based on the nearest XSCutLines chainages.

    def __init__(self, stream_centerline, cross_sections):
        super(Junctions, self).__init__()
"""


class CommonMethods(object):
    pass
