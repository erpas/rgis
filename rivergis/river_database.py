# -*- coding: utf-8 -*-

__author__ = 'ldebek'

import psycopg2
from qgis.core import QgsVectorLayer, QgsMapLayerRegistry, QgsDataSourceURI, NULL
from qgis.gui import QgsMessageBar
from os.path import join

class RiverDatabase(object):
    """
    Class for PostgreSQL database and hydrodynamic models handling.
    """
    SCHEMA = 'start'
    SRID = 2180

    def __init__(self, rgis, dbname, host, port, user, password):
        """
        Constructor for databse object

        Args:
            iface (QgsInterface instance): Instance of QGIS interface
            dbname (str): Name of the database
            host (str): Host of the database
            port (str): Port of the database
            user (str): User login
            password (str): Password for user
        """
        self.rgis = rgis
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
            # connection parameters using the dsn
            # http://initd.org/psycopg/docs/module.html#psycopg2.connect
            conn_params = 'dbname={0} host={1} port={2} user={3} password={4}'.format(self.dbname, self.host, self.port, self.user, self.password)
            self.con = psycopg2.connect(conn_params)
            msg = 'Connection established.'
        except Exception, e:
            self.rgis.iface.messageBar().pushMessage("Error", 'Can\'t connect to PostGIS database. Check connection details!', level=QgsMessageBar.CRITICAL, duration=10)
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
            print("Can not disconnect. There is no opened connection!")

    def setup_hydro_object(self, hydro_object, schema=None, srid=None):
        """
        Setting SCHEMA and SRID on hydro object.

        Args:
            hydro_object (class): Hydro object class
            schema (str): Schema where tables will be created or processed
            srid (int): A Spatial Reference System Identifier
        """
        if schema is None:
            hydro_object.SCHEMA = self.SCHEMA
        else:
            hydro_object.SCHEMA = schema
        if srid is None:
            hydro_object.SRID = self.SRID
        else:
            hydro_object.SRID = srid

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
                self.con.commit()
                if fetch is True:
                    result = cur.fetchall()
                else:
                    result = []
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

    def register_existing(self, hydro_module, schema=None, srid=None):
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
                self.setup_hydro_object(hydro_object, schema, srid)
                obj = hydro_object()
                self.register_object(obj)
                print 'registered {0}'.format(obj.name)
            else:
                pass

    def load_registered(self):
        """
        Load hydrodynamic model objects from register.
        """
        for k in sorted(self.register.keys()):
            self.add_to_view(self.register[k])

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
        self.setup_hydro_object(hecobject, schema, srid)
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
        mapLayer = QgsMapLayerRegistry.instance().addMapLayer(self.vlayer)
        styleFile = join(self.rgis.rivergisPath, 'styles', '{0}.qml'.format(obj.name))
        try:
            mapLayer.loadNamedStyle(styleFile)
        except:
            self.rgis.addInfo('Could not find style: {0}'.format(styleFile))


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
        # TODO: first check if the target table is in editing mode in QGIS

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
        layer_fields_names = ['{0}'.format(f.name()) for f in layer_fields]

        # check if the layer has attributes to import
        # get all fields except the ID
        attrs_to_import = []
        for field in hecobject.attrs[1:]:
            if field[0].strip('\"') in layer_fields_names:
                attrs_to_import.append(field)

        # create SQL for inserting the layer into PG database
        schema_name = '"{0}"."{1}"'.format(SCHEMA, hecobject.name)
        attrs_names = ['{0}'.format(attr[0]) for attr in attrs_to_import]
        qry = 'INSERT INTO {0} \n\t({1}'.format(schema_name, ', '.join(attrs_names))
        qry += ', ' if attrs_names else ''
        qry += 'geom) \nVALUES\n\t'
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

    def create_spatial_index(self):
        """
        Create PostgreSQL function create_st_index_if_not_exists(schema, table).
        The function checks if a spatial index exists for the table - if not, it is created.
        """
        qry = '''
        CREATE OR REPLACE FUNCTION create_st_index_if_not_exists
          (schema text, t_name text) RETURNS void AS $$
        DECLARE
          full_index_name varchar;
        BEGIN
        full_index_name = schema || '_' || t_name || '_' || 'geom_idx';
        IF NOT EXISTS (
            SELECT 1
            FROM   pg_class c
            JOIN   pg_namespace n ON n.oid = c.relnamespace
            WHERE  c.relname = full_index_name
            AND    n.nspname = schema
            ) THEN

            execute 'CREATE INDEX ' || full_index_name || ' ON "' || schema || '"."' || t_name || '" USING GIST (geom)';
        END IF;
        END
        $$
        LANGUAGE plpgsql VOLATILE
        '''
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
