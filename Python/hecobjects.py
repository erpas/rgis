__author__ = 'ldebek'
import psycopg2
import sys
from qgis.core import QgsVectorLayer, QgsMapLayerRegistry, QgsDataSourceURI

class HecRasObject(object):
    """
    Class for HEC-RAS geometry objects processing.
    """
    dbname = 'CMPiS_Gdynia'
    host = 'pzrpgeosrv.imgw.ad'
    port = '5432'
    user = 'ldebek'
    password = ''
    schema = 'public'
    srid = '2180'

    def __init__(self):
        self.con = None
        self.uri = None
        self.vlayer = None
        self.name = self.__class__.__name__
        self.tab_sql = None

    def build_table_sql(self):
        qry = ['id serial PRIMARY KEY', 'geom geometry({0}, {1})'.format(self.geom_type, self.srid)]
        qry += [' '.join(field) for field in self.attrs]
        self.tab_sql = 'CREATE TABLE {0}."{1}"(\n\t{2});'.format(self.schema, self.name, ',\n\t'.join(qry))

    def connect_pg(self):
        try:
            self.con = psycopg2.connect(database=self.dbname, host=self.host, port=self.port, user=self.user, password=self.password)
        except Exception, e:
            print(e)
            sys.exit(1)

    def run_sql(self, sql):
        try:
            cur = self.con.cursor()
            cur.execute(sql)
            self.con.commit()
        except Exception, e:
            if self.con:
                self.con.rollback()
            else:
                pass
            print(e)
            sys.exit(1)
        finally:
            if self.con:
                self.con.close()
            else:
                pass

    def add_to_view(self):
        self.uri = QgsDataSourceURI()
        self.uri.setConnection(self.host, self.port, self.dbname, self.user, self.password)
        self.uri.setDataSource(self.schema, self.name, 'geom')
        self.vlayer = QgsVectorLayer(self.uri.uri(), self.name, 'postgres')
        QgsMapLayerRegistry.instance().addMapLayer(self.vlayer)


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
    x.build_table_sql()
    x.connect_pg()
    x.run_sql(x.tab_sql)
    x.add_to_view()
    print(x.tab_sql)
