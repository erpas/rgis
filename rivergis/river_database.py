__author__ = 'ldebek'

import psycopg2
import sys
from hecobjects import *
from qgis.core import QgsVectorLayer, QgsMapLayerRegistry, QgsDataSourceURI, NULL

class RiverDatabase(object):
    """
    Class for PostgreSQL database and hydrodynamic models handling.
    """
    SCHEMA = None
    SRID = None

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
            print('Can\'t disconnect. There is no opened connection!')

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

    def process_hecobject(self, hecobject, pg_method, schema=None, srid=None):
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
        if schema is None:
            hecobject.SCHEMA = self.SCHEMA
        else:
            hecobject.SCHEMA = schema
        if srid is None:
            hecobject.SRID = self.SRID
        else:
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

    def insert_layer(self, layer, hecobject, schema=None, srid=None):
        """
        Insert a vector layer's features into a PostGIS table of a hecras object.
        It checks source layer's attribute names and compares them to column names of a target table.
        If the attribute has a corresponding name in target table then it is copied into table table.

        It can be used to copy hecobject table from one schema to another.

        Args:
            layer (QgsVectorLayer): source QGIS layer containing the features to insert
            hecobject (class): target HEC-RAS class object
            schema (str): a target schema
            srid (int): a Spatial Reference System Identifier
        """
        if schema is None:
            SCHEMA = self.SCHEMA
        else:
            SCHEMA = schema
        if srid is None:
            SRID = self.SRID
        else:
            SRID = srid

        # get the layer's features
        features = layer.getFeatures()

        # get the layer's field name list
        layerFields = []
        for attr in layer.pendingFields():
            layerFields.append(attr.name())

        attrs_to_import = [] # list of fields that will be imported

        # check if the layer has attributes to import
        for field in hecobject.attrs[1:]: # get all fields except the ID
            if field[0].strip('\"') in layerFields:
                attrs_to_import.append(field)

        # create SQL for inserting the layer into PG database
        schTable = '"{0}"."{1}"'.format(SCHEMA, hecobject.name)
        attrsNames = ['{0}'.format(attr[0]) for attr in attrs_to_import]
        qry = 'INSERT INTO {0} \n\t({1}, geom) \nVALUES\n\t'.format(schTable, ', '.join(attrsNames))
        featsDef = [] # list of attributes' data
        for feat in features:
            vals = [] # list of field values of the current feature
            geomWkt = feat.geometry().exportToWkt()
            for attr in attrs_to_import:
                val = feat.attribute(attr[0].strip('\"'))
                if not val == NULL:
                    vals.append('\'{0}\'::{1}'.format(val, attr[1]))
                else:
                    vals.append('NULL')
            vals.append('ST_GeomFromText(\'{0}\', {1})'.format(geomWkt, SRID))
            featsDef.append('({0})'.format(', '.join(vals)))
        qry += '{0};'.format(',\n\t'.join(featsDef))

        self.run_query(qry)


    def get_ras_gis_import_header(self):
        """
        Return header of RAS GIS Import file.
        """
        pass


if __name__ == '__main__':
    baza = RiverDatabase('CMPiS_Gdynia', 'pzrpgeosrv.imgw.ad', '5432', 'ldebek', '')

    baza.SCHEMA = 'public'
    baza.SRID = 2180

    baza.connect_pg()

    baza.process_hecobject(StreamCenterlines3D, 'pg_create_table')
    baza.process_hecobject(StreamCenterlines, 'pg_from_to_node')
    baza.process_hecobject(StreamCenterlines, 'pg_lengths_stations')

    for qry in baza.queries:
        print(qry)
        print(baza.queries[qry])
    print(baza.register)

    baza.disconnect_pg()
