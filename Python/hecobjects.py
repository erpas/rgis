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

    def build_table(self):
        qry = ['id serial PRIMARY KEY', 'geom geometry({0}, {1})'.format(self.geom_type, self.srid)]
        qry += [' '.join(field) for field in self.attrs]
        qry = 'CREATE TABLE {0}."{1}"(\n\t{2});'.format(self.schema, self.name, ',\n\t'.join(qry))
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
            ('"HydroID"', 'decimal'),
            ('"RiverCode"', 'varchar(16)'),
            ('"ReachCode"', 'varchar(16)'),
            ('"FromNode"', 'numeric'),
            ('"ToNode"', 'numeric'),
            ('"ArcLength"', 'real'),
            ('"FromSta"', 'real'),
            ('"ToSta"', 'real')]

    def pg_from_to_node(self):
        qry = '''
CREATE OR REPLACE FUNCTION from_to_node ()
    RETURNS VOID AS
$BODY$
DECLARE
    c cursor FOR SELECT * FROM "StreamCenterline";
    r "StreamCenterline"%ROWTYPE;
    start_geom geometry;
    end_geom geometry;
    start_node integer := 0;
    end_node integer := 0;
    nr integer := 0;
BEGIN
DROP TABLE IF EXISTS "NodesTable";
CREATE TABLE "NodesTable"(
    geom geometry(POINT, 2180),
    "NodeID" integer,
    "X" real,
    "Y" real);
FOR r in c LOOP
    start_geom := ST_StartPoint(r.geom);
    end_geom := ST_EndPoint(r.geom);
    IF (SELECT exists (SELECT 1 FROM "NodesTable" WHERE geom = start_geom LIMIT 1)) THEN
        start_node := (SELECT "NodeID" FROM "NodesTable" WHERE geom = start_geom LIMIT 1);
    ELSE
        nr := nr + 1;
        start_node := nr;
        INSERT INTO "NodesTable" VALUES (start_geom, nr, ST_X(start_geom), ST_Y(start_geom));
    END IF;
    IF (SELECT exists (SELECT 1 FROM "NodesTable" WHERE geom = end_geom LIMIT 1)) THEN
        end_node := (SELECT "NodeID" FROM "NodesTable" WHERE geom = end_geom LIMIT 1);
    ELSE
        nr := nr + 1;
        end_node := nr;
        INSERT INTO "NodesTable" VALUES (end_geom, nr, ST_X(end_geom), ST_Y(end_geom));
    END IF;
    UPDATE "StreamCenterline" SET
    "FromNode" = start_node,
    "ToNode" = end_node
    WHERE CURRENT OF c;
END LOOP;
END;
$BODY$
    LANGUAGE plpgsql;

SELECT from_to_node ();
DROP FUNCTION IF EXISTS from_to_node ()
'''
        return qry

    def pg_lengths_stations(self):
        qry = '''

CREATE OR REPLACE VIEW pnts1 AS
SELECT "RiverCode", "ReachCode", ST_StartPoint(geom) AS geom, 'start' AS typ_punktu
FROM "StreamCenterline"
UNION ALL
SELECT "RiverCode", "ReachCode", ST_EndPoint(geom) AS geom, 'end' AS typ_punktu
FROM "StreamCenterline";

CREATE OR REPLACE VIEW pnts2 AS
SELECT "RiverCode", geom
FROM pnts1
GROUP BY "RiverCode", geom
HAVING COUNT(geom) = 1;

DROP TABLE IF EXISTS "Endpoints";
SELECT pnts1."RiverCode", pnts1."ReachCode", pnts1.geom::geometry(POINT, 2180) INTO "Endpoints"
FROM pnts1, pnts2
WHERE pnts1."RiverCode" = pnts2."RiverCode" AND pnts1.geom = pnts2.geom AND pnts1.typ_punktu = 'end';

DROP VIEW pnts1 CASCADE;

SELECT * FROM "StreamCenterline"
WHERE "StreamCenterline"."ReachCode" = ANY((SELECT "Endpoints"."ReachCode" FROM "Endpoints"))
'''
        return qry

class BankLines(HecRasObject):
    """
    Geometry and table.
    """
    def __init__(self):
        super(BankLines, self).__init__()
        self.hdf_dataset = u'River Bank Lines'
        self.geom_type = 'LINESTRING'
        self.attrs = [('"HydroID"', 'decimal')]


class BankPoints(HecRasObject):
    """
    Geometry and table.
    """
    def __init__(self):
        super(BankPoints, self).__init__()
        self.hdf_dataset = u'River Bank Lines'
        self.geom_type = 'POINT'
        self.attrs = [('"HydroID"', 'decimal')]


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
        self.attrs = [('"LineType"', 'varchar(7)')]


class XSCutLines(HecRasObject):
    """
    Geometry and table.
    """
    def __init__(self):
        super(XSCutLines, self).__init__()
        self.hdf_dataset = u'Cross Sections'
        self.geom_type = 'LINESTRING'
        self.attrs = [
            ('"HydroID"', 'decimal'),
            ('"Station"', 'real'),
            ('"RiverCode"', 'varchar(16)'),
            ('"ReachCode"', 'varchar(16)'),
            ('"LeftBank"', 'real'),
            ('"RightBank"', 'real'),
            ('"Llength"', 'real'),
            ('"ChLength"', 'real'),
            ('"Rlength"', 'real'),
            ('"NodeName"', 'varchar(32)')]


class Bridges(HecRasObject):
    def __init__(self):
        super(Bridges, self).__init__()
        self.hdf_dataset = u'Structures'
        self.geom_type = 'LINESTRING'
        self.attrs = [
            ('"HydroID"', 'decimal'),
            ('"RiverCode"', 'varchar(16)'),
            ('"ReachCode"', 'varchar(16)'),
            ('"Station"', 'real'),
            ('"USDistance"', 'real'),
            ('"TopWidth"', 'real'),
            ('"NodeName"', 'varchar(32)')]


class IneffAreas(HecRasObject):
    def __init__(self):
        super(IneffAreas, self).__init__()
        self.hdf_dataset = None
        self.geom_type = 'POLYGON'
        self.attrs = [('"HydroID"', 'decimal')]


class BlockedObs(HecRasObject):
    def __init__(self):
        super(BlockedObs, self).__init__()
        self.hdf_dataset = None
        self.geom_type = 'POLYGON'
        self.attrs = [('"HydroID"', 'decimal')]


class LanduseAreas(HecRasObject):
    def __init__(self):
        super(LanduseAreas, self).__init__()
        self.hdf_dataset = None
        self.geom_type = 'MULTIPOLYGON'
        self.attrs = [
            ('"LUCode"', 'varchar(32)'),
            ('"N_Value"', 'real')]


class LeveeAlignment(HecRasObject):
    def __init__(self):
        super(LeveeAlignment, self).__init__()
        self.hdf_dataset = None
        self.geom_type = 'LINESTRING'
        self.attrs = [('"HydroID"', 'decimal')]


class LeveePoints(HecRasObject):
    def __init__(self):
        super(LeveePoints, self).__init__()
        self.hdf_dataset = None
        self.geom_type = 'POINTS'
        self.attrs = [
            ('"LeveeID"', 'decimal'),
            ('"Station"', 'decimal'),
            ('"Elevation"', 'decimal')]


class InlineStructures(HecRasObject):
    def __init__(self):
        super(InlineStructures, self).__init__()
        self.hdf_dataset = u'Structures'
        self.geom_type = 'LINESTRING'
        self.attrs = [
            ('"HydroID"', 'decimal'),
            ('"RiverCode"', 'varchar(16)'),
            ('"ReachCode"', 'varchar(16)'),
            ('"Station"', 'real'),
            ('"USDistance"', 'real'),
            ('"TopWidth"', 'real'),
            ('"NodeName"', 'varchar(32)')]


class LateralStructures(HecRasObject):
    def __init__(self):
        super(LateralStructures, self).__init__()
        self.hdf_dataset = u'Structures'
        self.geom_type = 'LINESTRING'
        self.attrs = [
            ('"HydroID"', 'decimal'),
            ('"RiverCode"', 'varchar(16)'),
            ('"ReachCode"', 'varchar(16)'),
            ('"Station"', 'real'),
            ('"USDistance"', 'real'),
            ('"TopWidth"', 'real'),
            ('"NodeName"', 'varchar(32)')]


class StorageAreas(HecRasObject):
    def __init__(self):
        super(StorageAreas, self).__init__()
        self.hdf_dataset = None
        self.geom_type = 'POLYGON'
        self.attrs = [
            ('"HydroID"', 'decimal'),
            ('"MaxElev"', 'real'),
            ('"MinElev"', 'real'),
            ('"UserElev"', 'real')]


class SAConnections(HecRasObject):
    def __init__(self):
        super(SAConnections, self).__init__()
        self.hdf_dataset = None
        self.geom_type = 'POLYGON'
        self.attrs = [
            ('"HydroID"', 'decimal'),
            ('"USSA"', 'decimal'),
            ('"DSSA"', 'decimal'),
            ('"TopWidth"', 'real')]


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


if __name__ == '__main__':
    x = StreamCenterline3D()
    x.build_table()