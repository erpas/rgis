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
            host (str): Host of the database
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
        self.register = {}
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
            self.con = None
        else:
            print('There is no opened connection!')

    def run_query(self, qry):
        """
        Running PostgreSQL queries.

        Args:
            qry (str): Query for database
        """
        result = False
        try:
            if self.con:
                cur = self.con.cursor()
                cur.execute(qry)
                self.con.commit()
                result = True
            else:
                print('There is no opened connection! Use "connect_pg" method before running query.')
        except Exception, e:
            self.con.rollback()
            print(e)
            sys.exit(1)
        finally:
            return result

    def register_object(self, obj):
        """
        Registering object in database as dictionary entry.

        Args:
            obj: Instance of a hydrodynamic model object class
        """
        key = obj.name
        if key not in self.register:
            self.register[key] = obj
        else:
            print('Object already exists inside RiverGIS registry.')

    def process_hecobject(self, hecobject, pg_method, schema, srid):
        """
        Creating and processing tables inside PostGIS database.

        Args:
            hecobject (class): HEC-RAS class object
            pg_method (str): String representation of method that will be called on the hecobject class
            schema (str): Schema where tables will be created or processed
            srid (int): A Spatial Reference System Identifier

        Returns:
            obj: Instance of HEC-RAS class object
        """
        hecobject.SCHEMA = schema
        hecobject.SRID = srid
        obj = hecobject()
        method = getattr(obj, pg_method)
        qry = method()
        result = self.run_query(qry)
        if result is True:
            self.register_object(obj)
            self.queries[method.__name__] = qry
            return obj
        else:
            print('Process aborted!')

    def import_hecobject(self, sdf):
        """
        Importing geometry objects from HEC-RAS SDF file to PostGIS database.

        Args:
            sdf (str): path to SDF file
        """
        pass

    def exists(self, hydroclass):
        """
        Checking if hydrodynamic model object exists in database.

        Args:
            hydroclass (class): hydrodynamic model class object
        """
        pass

    def add_to_view(self, obj):
        """
        Adding PostGIS table as QGIS layer.

        Args:
            obj: Instance of a hydrodynamic model object class
        """
        self.uri = QgsDataSourceURI()
        self.uri.setConnection(self.host, self.port, self.dbname, self.user, self.password)
        self.uri.setDataSource(obj.schema, obj.name, 'geom')
        self.vlayer = QgsVectorLayer(self.uri.uri(), obj.name, 'postgres')
        QgsMapLayerRegistry.instance().addMapLayer(self.vlayer)

    def getRasGisImportHeader(self):
        """
        Return header of RAS GIS Import file.
        """
        pass


if __name__ == '__main__':
    baza = RiverDatabase('CMPiS_Gdynia', 'pzrpgeosrv.imgw.ad', '5432', 'ldebek', '')
    baza.connect_pg()

    baza.process_hecobject(StreamCenterlines3D, 'pg_create_table', 'public', 2180)
    baza.process_hecobject(StreamCenterlines, 'pg_from_to_node', 'public', 2180)
    baza.process_hecobject(StreamCenterlines, 'pg_lengths_stations', 'public', 2180)
    for qry in baza.queries:
        print(qry)
        print(baza.queries[qry])
    print(baza.register)

    baza.disconnect_pg()
