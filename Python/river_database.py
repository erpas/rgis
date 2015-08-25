__author__ = 'ldebek'

import psycopg2
import sys
from hecobjects import *
from qgis.core import QgsVectorLayer, QgsMapLayerRegistry, QgsDataSourceURI

class RiverDatabase(object):
    """
    Class for PostgreSQL database and hydrodynamic models handling.
    """
    def __init__(self, dbname, host, port, user, password):
        """
        Constructor for databse object
        :param dbname: Name of the database
        :param host: Host of the databse
        :param port: Port of the database
        :param user: User login
        :param password: Password for user
        """
        self.dbname = dbname
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.con = None
        self.uri = None
        self.vlayer = None
        self.objects_register = {}

    def connect_pg(self):
        """
        Method for setting up PostgreSQL connection object as RiverDatabase class instance attribute.
        """
        try:
            self.con = psycopg2.connect(database=self.dbname, host=self.host, port=self.port, user=self.user, password=self.password)
        except Exception, e:
            print(e)
            sys.exit(1)

    def disconnect_pg(self):
        """
        Closing connection to database.
        """
        if self.con:
            self.con.close()
        else:
            print('There is no opened connection!')

    def run_sql(self, sql):
        """
        Running PostgreSQL queries.
        :param sql: Query for database
        """
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

    def chack_if_exists(self, obj):
        """
        Checking if geometry object exists in database.
        :param obj: Instance of geometry object
        """
        if obj.name in obj.schema:
            return True
        else:
            return False

    def register(self, obj):
        """
        Registering object in database as dictionary entry.
        :param obj: Instance of geometry object
        """
        key = obj.name
        if key not in self.objects_register:
            self.objects_register[key] = obj
        else:
            print('Object already exists inside RiverGIS registry.')

    def crete_hecobject(self, hecobject, schema, srid):
        """
        Creating table templates inside PostGIS database.
        :param hecobject: HEC-RAS class object
        :param schema: Schema where tables will be created
        :param srid: A Spatial Reference System Identifier
        """
        hecobject.SCHEMA = schema
        hecobject.SRID = srid
        obj = hecobject()
        if self.chack_if_exists(obj) is False:
            qry = obj.build_table()
            print(qry)
            self.run_sql(qry)
            self.register(obj)
        else:
            pass
        return obj

    def process_hecobject(self, hecobject, pg_method, schema, srid):
        hecobject.SCHEMA = schema
        hecobject.SRID = srid
        obj = hecobject()
        method = getattr(obj, pg_method)
        qry = method()
        print(qry)
        self.run_sql(qry)
        self.register(obj)

    def import_hecobject(self, sdf):
        """
        Importing geometry objects from HEC-RAS SDF file to PostGIS database.
        :param sdf: SDF file
        """
        pass

    def add_to_view(self, obj):
        """
        Adding PostGIS table to QGIS view.
        :param obj: Instance of geometry object
        """
        self.uri = QgsDataSourceURI()
        self.uri.setConnection(self.host, self.port, self.dbname, self.user, self.password)
        self.uri.setDataSource(obj.schema, obj.name, 'geom')
        self.vlayer = QgsVectorLayer(self.uri.uri(), obj.name, 'postgres')
        QgsMapLayerRegistry.instance().addMapLayer(self.vlayer)


if __name__ == '__main__':
    baza = RiverDatabase('CMPiS_Gdynia', 'pzrpgeosrv.imgw.ad', '5432', 'ldebek', '')
    baza.connect_pg()

    baza.crete_hecobject(StreamCenterline3D, 'public', 2180)
    baza.process_hecobject(StreamCenterline, 'pg_from_to_node', 'public', 2180)
    baza.process_hecobject(StreamCenterline, 'pg_lengths_stations', 'public', 2180)
    print(baza.objects_register)

    baza.disconnect_pg()
