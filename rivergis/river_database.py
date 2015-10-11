# -*- coding: utf-8 -*-

__author__ = 'Łukasz Dębek'

import psycopg2
import psycopg2.extras

from qgis.core import QgsVectorLayer, QgsMapLayerRegistry, QgsDataSourceURI, NULL, QGis
from qgis.gui import QgsMessageBar
from os.path import join


class RiverDatabase(object):
    """
    Class for PostgreSQL database and hydrodynamic models handling.
    """
    SCHEMA = 'start'
    SRID = 2180
    CHECK_URI = True

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
        self.register = {}
        self.queries = {}
        self.uris = []
        self.refresh_uris()

    def connect_pg(self):
        """
        Method for setting up PostgreSQL connection object as RiverDatabase class instance attribute.
        """
        msg = None
        try:
            # connection parameters using the dsn
            conn_params = 'dbname={0} host={1} port={2} user={3} password={4}'.format(self.dbname, self.host, self.port, self.user, self.password)
            self.con = psycopg2.connect(conn_params)
            msg = 'Connection established.'
        except Exception, e:
            self.rgis.iface.messageBar().pushMessage("Error", 'Can\'t connect to PostGIS database. Check connection details!', level=QgsMessageBar.CRITICAL, duration=10)
            msg = e
        finally:
            self.rgis.addInfo(msg)
            return msg

    def disconnect_pg(self):
        """
        Closing connection to database.
        """
        if self.con:
            self.con.close()
            self.con = None
            self.register.clear()
            self.queries.clear()
        else:
            self.rgis.addInfo('Can not disconnect. There is no opened connection!')

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
                cur = self.con.cursor(cursor_factory=psycopg2.extras.DictCursor)
                cur.execute(qry)
                if fetch is True:
                    result = cur.fetchall()
                else:
                    result = []
                self.con.commit()
            else:
                self.rgis.addInfo('There is no opened connection! Use "connect_pg" method before running query.')
        except Exception, e:
            self.con.rollback()
            self.rgis.addInfo(repr(e))
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
            if self.rgis.DEBUG:
                self.rgis.addInfo('{0} already exists inside RiverGIS registry.'.format(key))

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
                if self.rgis.DEBUG:
                    self.rgis.addInfo('{0} registered'.format(obj.name))
            else:
                pass

    def load_registered(self):
        """
        Load hydrodynamic model objects from register.
        """
        for k in sorted(self.register.keys()):
            obj = self.register[k]
            if obj.visible is True:
                self.add_to_view(obj)
            else:
                pass
        self.rgis.iface.mapCanvas().refresh()

    def process_hecobject(self, hecobject, pg_method, schema=None, srid=None, **kwargs):
        """
        Creating and processing tables inside PostGIS database.

        Args:
            hecobject (class): HEC-RAS class object
            pg_method (str): String representation of method that will be called on the hecobject class
            schema (str): Schema where tables will be created or processed
            srid (int): A Spatial Reference System Identifier
            **kwargs (dict): Additional keyword arguments passed to pg_method

        Returns:
            obj: Instance of HEC-RAS class object
        """
        self.setup_hydro_object(hecobject, schema, srid)
        obj = hecobject()
        method = getattr(obj, pg_method)
        qry = method(**kwargs)
        result = self.run_query(qry)
        if result is not None:
            self.register_object(obj)
            self.queries[method.__name__] = qry
            return obj
        else:
            self.rgis.addInfo('Process aborted!')

    def make_vlayer(self, obj):
        """
        Making layer from PostGIS table.

        Args:
            obj: Instance of a hydrodynamic model object class
        """
        uri = QgsDataSourceURI()
        uri.setConnection(self.host, self.port, self.dbname, self.user, self.password)
        uri.setDataSource(obj.schema, obj.name, 'geom')
        vlayer = QgsVectorLayer(uri.uri(), obj.name, 'postgres')
        return vlayer

    def add_vlayer(self, vlayer):
        """
        Handling adding layer process to QGIS view.

        Args:
            vlayer (QgsVectorLayer): QgsVectorLayer object
        """
        try:
            map_registry = QgsMapLayerRegistry.instance()
            map_layer = map_registry.addMapLayer(vlayer)
            style_file = join(self.rgis.rivergisPath, 'styles', '{0}.qml'.format(vlayer.name()))
            map_layer.loadNamedStyle(style_file)
        except Exception, e:
            self.rgis.addInfo(vlayer.name())
            self.rgis.addInfo(repr(e))

    def refresh_uris(self):
        """
        Setting layers uris list from QgsMapLayerRegistry
        """
        self.uris = [vl.source() for vl in QgsMapLayerRegistry.instance().mapLayers().values()]
        if self.rgis.DEBUG:
            self.rgis.addInfo('Layers sources:\n    {0}'.format('\n    '.join(self.uris)))

    def add_to_view(self, obj):
        """
        Handling adding layer process to QGIS view.

        Args:
            obj: Instance of a hydrodynamic model object class
        """
        vlayer = self.make_vlayer(obj)
        src = vlayer.source()
        if self.CHECK_URI is True:
            if src not in self.uris:
                self.add_vlayer(vlayer)
            else:
                pass
        else:
            self.add_vlayer(vlayer)

    def insert_layer(self, layer, hecobject, schema=None, srid=None, attr_map=None, onlySelected=False):
        """
        Insert a vector layer's features into a PostGIS table of a hecras object.
        If an attribute map attr_map is specified, only the mapped attributes are imported. If attr_map
        is None, it checks source layer's attribute names and compares them to column names of a target table.
        If the attribute has a corresponding name in target table then it is copied into table table.

        It can be used to copy hecobject table from one schema to another.

        Args:
            layer (QgsVectorLayer): source QGIS layer containing the features to insert
            hecobject (class): target HEC-RAS class object
            schema (str): a target schema
            srid (int): a Spatial Reference System Identifier
            attr_map(dict): attribute mapping dictionary, i.e. {'target_table_attr': 'src_layer_field', ...}
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
        # check if only selected features should be imported
        if onlySelected:
            # get only selected
            features = layer.selectedFeatures()
        else:
            # get all features
            features = layer.getFeatures()
        layer_fields = layer.dataProvider().fields().toList()
        field_names = ['{0}'.format(f.name()) for f in layer_fields]

        if self.rgis.DEBUG:
            if attr_map:
                am = ['{0} - {1}'.format(key, value) for key, value in attr_map.iteritems()]
                info = '  attr_map:\n    '
                info += '\n    {0}'.join(am)
                self.rgis.addInfo(info)
            else:
                pass
        else:
            pass

        # list of imported attributes tuples (target_attr, src_attr, attr_type)
        # check if the layer has attributes to import
        # get all fields except the ID
        imp_attrs = []
        for attr in hecobject.attrs[1:]:
            attr_name = attr[0].strip('"')
            if attr_map:
                if attr_name in attr_map.keys():
                    imp_attrs.append([attr[0], attr_map[attr_name], attr[1]])
                else:
                    pass
            else:
                if attr_name in field_names:
                    imp_attrs.append([attr[0], attr[0], attr[1]])
                else:
                    pass

        self.rgis.addInfo('<br>  Importing {0}'.format(hecobject.name))
        for i in imp_attrs:
            self.rgis.addInfo('      {0} as {1} with type {2}'.format(i[0], i[1], i[2]))

        # create SQL for inserting the layer into PG database
        schema_name = '"{0}"."{1}"'.format(SCHEMA, hecobject.name)
        attrs_names = ['{0}'.format(attr[0]) for attr in imp_attrs]
        qry = 'INSERT INTO {0} \n\t({1}'.format(schema_name, ', '.join(attrs_names))
        qry += ', ' if attrs_names else ''
        qry += 'geom) \nVALUES\n\t'
        # list of attributes data
        feats_def = []
        singleToMultiConversion = False

        for feat in features:
            # field values of the feature
            vals = []
            geom_wkt = feat.geometry().exportToWkt()
            # Geometry type check:
            # is target geometry of type multi?
            # is source layer geom multi?
            target_multi = hecobject.geom_type.startswith('MULTI')
            src_multi = feat.geometry().isMultipart()
            if not target_multi and src_multi:
                self.rgis.addInfo('WARNING:<br>Source geometry is of type MULTI but the target is a {0} --- skipping the layer.'.format(hecobject.geom_type))
                qry = ''
            elif target_multi and not src_multi:
                singleToMultiConversion = True
                geometry = 'ST_Multi(ST_GeomFromText(\'{0}\', {1}))'.format(geom_wkt, SRID)
            else:
                geometry = 'ST_GeomFromText(\'{0}\', {1})'.format(geom_wkt, SRID)

            for attr in imp_attrs:
                val = feat.attribute(attr[1].strip('"'))
                if not val == NULL:
                    vals.append('\'{0}\'::{1}'.format(val, attr[2]))
                else:
                    vals.append('NULL')
            vals.append(geometry)
            feats_def.append('({0})'.format(', '.join(vals)))
        qry += '{0};'.format(',\n\t'.join(feats_def))
        if singleToMultiConversion:
            self.rgis.addInfo('Source geometry is of type SINGLE but the target is a {0}.'.format(hecobject.geom_type))
            self.rgis.addInfo('Will try to convert SINGLE geometries to MULTI - check the results!')
        if self.rgis.DEBUG:
            self.rgis.addInfo(qry)
        else:
            pass
        self.run_query(qry)
        self.rgis.addInfo('OK')

    def create_spatial_index(self):
        """
        Create PostgreSQL function create_st_index_if_not_exists(schema, table).
        The function checks if a spatial index exists for the table - if not, it is created.
        """
        qry = '''
CREATE OR REPLACE FUNCTION create_spatial_index(schema text, t_name text)
    RETURNS VOID AS
$BODY$
DECLARE
    full_index_name text;
BEGIN
    full_index_name = schema || '_' || t_name || '_' || 'geom_idx';
    IF NOT EXISTS (
        SELECT 1
        FROM   pg_class c
        JOIN   pg_namespace n ON n.oid = c.relnamespace
        WHERE  c.relname = full_index_name AND n.nspname = schema
        )
    THEN
        EXECUTE 'CREATE INDEX "' || full_index_name || '" ON "' || schema || '"."' || t_name || '" USING GIST (geom)';
    END IF;
END;
$BODY$
    LANGUAGE plpgsql;
'''
        self.run_query(qry)


if __name__ == '__main__':
    baza = RiverDatabase('CMPiS_Gdynia', 'pzrpgeosrv.imgw.ad', '5432', 'ldebek', '')

    baza.SCHEMA = 'public'
    baza.SRID = 2180

    baza.connect_pg()
    baza.disconnect_pg()
