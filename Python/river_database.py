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

        Args:
            dbname (str): Name of the database
            host (str): Host of the databse
            port (str): Port of the database
            user (str): User login
            password (str): Password for user
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
        self.queries = {}

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

    def run_query(self, qry):
        """
        Running PostgreSQL queries.
        :param qry: Query for database
        """
        try:
            cur = self.con.cursor()
            cur.execute(qry)
            self.con.commit()
        except Exception, e:
            if self.con:
                self.con.rollback()
            else:
                pass
            print(e)
            sys.exit(1)

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

    def process_hecobject(self, hecobject, pg_method, schema, srid):
        """
        Creating and processing tables inside PostGIS database.
        :param hecobject: HEC-RAS class object
        :param pg_method: String representation of method that will be called on the hecobject class
        :param schema: Schema where tables will be created or processed
        :param srid: A Spatial Reference System Identifier
        :return: Instance of HEC-RAS class object
        """
        hecobject.SCHEMA = schema
        hecobject.SRID = srid
        obj = hecobject()
        method = getattr(obj, pg_method)
        qry = method()
        self.run_query(qry)
        self.register(obj)
        self.queries[method.__name__] = qry
        return obj

    def import_hecobject(self, sdf):
        """
        Importing geometry objects from HEC-RAS SDF file to PostGIS database.
        :param sdf: SDF file
        """
        pass

    def exists(self, hecobject):
        """
        Checking if geometry object exists in database.
        :param hecobject: HEC-RAS class object
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

    baza.process_hecobject(StreamCenterline3D, 'pg_create_table', 'public', 2180)
    baza.process_hecobject(StreamCenterline, 'pg_from_to_node', 'public', 2180)
    baza.process_hecobject(StreamCenterline, 'pg_lengths_stations', 'public', 2180)
    for qry in baza.queries:
        print(qry)
        print(baza.queries[qry])
    print(baza.objects_register)

    baza.disconnect_pg()
