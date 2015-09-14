__author__ = 'ldebek'

import psycopg2
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
        msg = None
        try:
            self.con = psycopg2.connect(database=self.dbname, host=self.host, port=self.port, user=self.user, password=self.password)
            msg = 'Connection established.'
        except Exception, e:
            msg = e
        finally:
            print(msg)
            return msg

    def disconnect_pg(self):
        """
        Closing connection to database.
        """
        if self.con:
            self.con.close()
            self.con = None
        else:
            print('Can\'t disconnect. There is no opened connection!')

    def run_query(self, qry, fetch=False):
        """
        Running PostgreSQL queries.

        Args:
            qry (str): Query for database
            fetch (bool): Flag for returning result from query
        """
        result = None
        try:
            if self.con:
                cur = self.con.cursor()
                cur.execute(qry)
                if fetch is True:
                    result = cur.fetchall()
                else:
                    result = []
                self.con.commit()
            else:
                print('There is no opened connection! Use "connect_pg" method before running query.')
        except Exception, e:
            self.con.rollback()
            print(e)
        finally:
            return result

    def list_tables(self, schema=None):
        """
        Listing tables in schema.

        Args:
            schema (str): Schema where tables will be created or processed
        Returns:
            tabs (list): List of tuples with table names in schema
        """
        if schema is None:
            SCHEMA = self.SCHEMA
        else:
            SCHEMA = schema
        qry = 'SELECT table_name FROM information_schema.tables WHERE table_schema = \'{0}\''.format(SCHEMA)
        tabs = self.run_query(qry, True)
        return tabs

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
            print('{0} already exists inside RiverGIS registry.'.format(key))

    def register_existing(self, hydro_module, schema=None):
        """
        Registering hydrodynamic model objects which exists in schema.

        Args:
            hydro_module (module): hydrodynamic model module
            schema (str): Schema where tables will be created or processed
        """
        tabs = self.list_tables(schema)
        for tab in tabs:
            tab_name = tab[0]
            if tab_name in dir(hydro_module):
                hydro_object = getattr(hydro_module, tab_name)
                obj = hydro_object()
                self.register_object(obj)
            else:
                pass

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
        if result is not None:
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
        layer_fields = layer.dataProvider().fields().toList()

        # check if the layer has attributes to import
        # get all fields except the ID
        attrs_to_import = []
        for field in hecobject.attrs[1:]:
            if field[0].strip('"') in layer_fields:
                attrs_to_import.append(field)

        # create SQL for inserting the layer into PG database
        schema_name = '"{0}"."{1}"'.format(SCHEMA, hecobject.name)
        attrs_names = ['{0}'.format(attr[0]) for attr in attrs_to_import]
        qry = 'INSERT INTO {0} \n\t({1}, geom) \nVALUES\n\t'.format(schema_name, ', '.join(attrs_names))
        # list of attributes data
        feats_def = []
        for feat in features:
            # list of field values of the current feature
            vals = []
            geom_wkt = feat.geometry().exportToWkt()
            for attr in attrs_to_import:
                val = feat.attribute(attr[0].strip('"'))
                if not val == NULL:
                    vals.append('\'{0}\'::{1}'.format(val, attr[1]))
                else:
                    vals.append('NULL')
            vals.append('ST_GeomFromText(\'{0}\', {1})'.format(geom_wkt, SRID))
            feats_def.append('({0})'.format(', '.join(vals)))
        qry += '{0};'.format(',\n\t'.join(feats_def))

        self.run_query(qry)

    def get_ras_gis_import_header(self):
        """
        Return header of RAS GIS Import file.
        """
        pass


if __name__ == '__main__':
    import hecobjects as heco
    baza = RiverDatabase('CMPiS_Gdynia', 'pzrpgeosrv.imgw.ad', '5432', 'ldebek', '')

    baza.SCHEMA = 'public'
    baza.SRID = 2180

    baza.connect_pg()
    baza.register_existing(heco)
    baza.process_hecobject(heco.StreamCenterlines3D, 'pg_create_table')
    baza.process_hecobject(heco.StreamCenterlines, 'pg_from_to_node')
    baza.process_hecobject(heco.StreamCenterlines, 'pg_lengths_stations')

    for qry in baza.queries:
        print(qry)
        print(baza.queries[qry])
    print(baza.register)

    baza.disconnect_pg()
