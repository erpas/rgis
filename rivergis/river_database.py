# -*- coding: utf-8 -*-

"""
/***************************************************************************
Name                 : RiverGIS
Description          : HEC-RAS tools for QGIS
Date                 : December, 2015
copyright            : (C) 2015 by RiverGIS Group
email                : rpasiok@gmail.com, damnback333@gmail.com
***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""
from builtins import object

import psycopg2
import psycopg2.extras

from qgis.core import QgsVectorLayer, QgsProject, QgsDataSourceUri, NULL
from qgis.gui import QgsMessageBar
import os


class RiverDatabase(object):
    """
    Class for PostgreSQL database and hydrodynamic models handling.
    """
    SCHEMA = 'start'
    SRID = 2180
    OVERWRITE = True
    LOAD_ALL = True
    CHECK_URI = True

    def __init__(self, rgis, dbname, host, port, user, password):
        """
        Constructor for database object

        Args:
            rgis (QgsInterface instance): Instance of QGIS interface.
            dbname (str): Name of the database.
            host (str): Host of the database.
            port (str): Port of the database.
            user (str): User login.
            password (str): Password for user.
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
        Connection parameters are passed using the dsn.

        Returns:
            str: String message.
        """
        msg = None
        try:
            conn_params = 'dbname={0} host={1} port={2} user={3} password={4}'.format(self.dbname, self.host, self.port, self.user, self.password)
            self.con = psycopg2.connect(conn_params)
            msg = 'Connection established.'
        except Exception as e:
            self.rgis.iface.messageBar().pushMessage("Error", 'Can\'t connect to PostGIS database. Check connection details!', level=QgsMessageBar.CRITICAL, duration=10)
            msg = repr(e)
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

    def run_query(self, qry, fetch=False, arraysize=0, be_quiet=False):
        """
        Running PostgreSQL queries.

        Args:
            qry (str): Query for database.
            fetch (bool): Flag for returning result from query.
            arraysize (int): Number of items returned from query - default 0 mean using fetchall method.
            be_quiet (bool): Flag for printing exception message.

        Returns:
            list/generator/None: Returned value depends on the 'fetch' and 'arraysize' parameters.
        """
        result = None
        try:
            if self.con:
                cur = self.con.cursor(cursor_factory=psycopg2.extras.DictCursor)
                cur.execute(qry)
                if fetch is True and arraysize <= 0:
                    result = cur.fetchall()
                elif fetch is True and arraysize > 0:
                    result = self.result_iter(cur, arraysize)
                else:
                    result = []
                self.con.commit()
            else:
                msg = 'There is no opened connection!'
                msg += 'Please check your database connection authentication settings.'
                self.rgis.addInfo(msg)
        except Exception as e:
            self.con.rollback()
            if be_quiet is False:
                self.rgis.addInfo(repr(e))
            else:
                pass
        finally:
            return result

    @staticmethod
    def result_iter(cursor, arraysize):
        """
        Generator for getting partial results from query.

        Args:
            cursor (psycopg2 cursor object): Cursor with query.
            arraysize (int): Number of items returned from query.

        Yields:
            list: Items returned from query which length <= arraysize.
        """
        while True:
            results = cursor.fetchmany(arraysize)
            if not results:
                break
            else:
                pass
            yield results

    def setup_hydro_object(self, hydro_object, schema=None, srid=None, overwrite=None):
        """
        Setting SCHEMA, SRID and OVERWRITE on hydro object.

        Args:
            hydro_object (class): Hydro object class.
            schema (str): Schema where tables will be created or processed.
            srid (int): A Spatial Reference System Identifier.
            overwrite (bool): Flag deciding if objects can be overwrite.
        """
        if schema is None:
            hydro_object.SCHEMA = self.SCHEMA
        else:
            hydro_object.SCHEMA = schema
        if srid is None:
            hydro_object.SRID = self.SRID
        else:
            hydro_object.SRID = srid
        if overwrite is None:
            hydro_object.OVERWRITE = self.OVERWRITE
        else:
            hydro_object.OVERWRITE = overwrite

    def process_hecobject(self, hecobject, pg_method, schema=None, srid=None, overwrite=None, **kwargs):
        """
        Creating and processing tables inside PostGIS database.

        Args:
            hecobject (class): HEC-RAS class object.
            pg_method (str): String representation of method that will be called on the hecobject class.
            schema (str): Schema where tables will be created or processed.
            srid (int): A Spatial Reference System Identifier.
            overwrite (bool): Flag deciding if objects can be overwrite.
            **kwargs (dict): Additional keyword arguments passed to pg_method.

        Returns:
            obj: Instance of HEC-RAS class object
        """
        self.setup_hydro_object(hecobject, schema, srid, overwrite)
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

    def register_object(self, obj):
        """
        Registering object in database as dictionary entry.

        Args:
            obj: Instance of a hydrodynamic model object class.
        """
        key = obj.name
        if key not in self.register:
            self.register[key] = obj
        else:
            if self.rgis.DEBUG:
                self.rgis.addInfo('{0} already exists inside RiverGIS registry.'.format(key))

    def register_existing(self, hydro_module, schema=None, srid=None):
        """
        Registering hydrodynamic model objects which already exists inside schema.

        Args:
            hydro_module (module): hydrodynamic model module.
            schema (str): Schema where tables will be created or processed.
            srid (int): A Spatial Reference System Identifier.
        """
        tabs = self.list_tables(schema)
        for tab in tabs:
            if tab in dir(hydro_module):
                hydro_object = getattr(hydro_module, tab)
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
        for k in sorted(list(self.register.keys()), key=lambda x: self.register[x].order):
            obj = self.register[k]
            if obj.visible is True or self.LOAD_ALL is True:
                self.add_to_view(obj)
            else:
                pass
        self.rgis.iface.mapCanvas().refresh()

    def list_tables(self, schema=None):
        """
        Listing tables in schema.

        Args:
            schema (str): Schema where tables will be created or processed.

        Returns:
            list: List of table names in schema.
        """
        if schema is None:
            SCHEMA = self.SCHEMA
        else:
            SCHEMA = schema
        qry = 'SELECT table_name FROM information_schema.tables WHERE table_schema = \'{0}\''.format(SCHEMA)
        tabs = [tab[0] for tab in self.run_query(qry, fetch=True)]
        return tabs

    def refresh_uris(self):
        """
        Setting layers uris list from QgsProject
        """
        self.uris = [vl.source() for vl in list(QgsProject.instance().mapLayers().values())]
        if self.rgis.DEBUG:
            self.rgis.addInfo('Layers sources:\n    {0}'.format('\n    '.join(self.uris)))

    def make_vlayer(self, obj):
        """
        Making layer from PostGIS table.

        Args:
            obj: Instance of a hydrodynamic model object class.

        Returns:
            QgsVectorLayer: QGIS Vector Layer object.
        """
        vl_schema, vl_name = obj.schema, obj.name
        uri = QgsDataSourceUri()
        uri.setConnection(self.host, self.port, self.dbname, self.user, self.password)
        if obj.geom_type is not None:
            uri.setDataSource(vl_schema, vl_name, 'geom')
        else:
            uri.setDataSource(vl_schema, vl_name, None)
        vlayer = QgsVectorLayer(uri.uri(), vl_name, 'postgres')
        return vlayer

    def add_vlayer(self, vlayer):
        """
        Handling adding layer process to QGIS view.

        Args:
            vlayer (QgsVectorLayer): QgsVectorLayer object.
        """
        try:
            style_file = os.path.join(self.rgis.rivergisPath, 'styles', '{0}.qml'.format(vlayer.name()))
            vlayer.loadNamedStyle(style_file)
            QgsProject.instance().addMapLayer(vlayer)
        except Exception as e:
            self.rgis.addInfo(repr(e))

    def add_to_view(self, obj):
        """
        Handling adding layer process to QGIS view.

        Args:
            obj: Instance of a hydrodynamic model object class.
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

    def import_layer(self, layer, fields, attr_map, selected):
        """
        Import a vector layer's features with attributes specified inside attr_map dictionary.

        Args:
            layer (QgsVectorLayer): Source QGIS layer containing the features to insert.
            fields (list): List of tuples ('field_name', 'field_type') for hecobject attributes definition.
            attr_map (dict): Attribute mapping dictionary, i.e. {'target_table_attr': 'src_layer_field', ...}.
            selected (bool): Flag for processing selected features only.

        Returns:
            tuple: Tuple of features and fields lists.
        """
        self.rgis.addInfo('Importing data from {0}...'.format(layer.name()))
        features = layer.selectedFeatures() if selected and layer.selectedFeatureCount() > 0 else layer.getFeatures()
        layer_fields = layer.dataProvider().fields().toList()
        field_names = ['{0}'.format(f.name()) for f in layer_fields]

        imp_attrs = []
        for attr in fields[1:]:
            attr_name = attr[0].strip('"')
            if attr_map:
                if attr_name in list(attr_map.keys()):
                    imp_attrs.append([attr[0], attr_map[attr_name], attr[1]])
                else:
                    pass
            else:
                if attr_name in field_names:
                    imp_attrs.append([attr[0], attr[0], attr[1]])
                else:
                    pass
        return features, imp_attrs

    def layer_to_pgsql(self, features, fields, hecobject, schema, srid):
        """
        Create SQL for inserting the layer into PG database.

        Args:
            features (list): List of WKT geometry objects.
            fields (list): List of fields imported from layer.
            hecobject (HecRasObject): Target HEC-RAS object.
            schema (str): Target schema.
            srid (int): Spatial Reference System Identifier.

        Returns:
            str: Query for inserting features into a PostGIS table.
        """
        schema_name = '"{0}"."{1}"'.format(schema, hecobject.name)
        attrs_names = ['{0}'.format(attr[0]) for attr in fields]
        qry = 'INSERT INTO {0} \n\t({1}'.format(schema_name, ', '.join(attrs_names))
        qry += ', ' if attrs_names else ''
        qry += 'geom) \nVALUES\n\t'

        feats_def = []
        single2multi = False
        for feat in features:
            vals = []
            geom_wkt = feat.geometry().asWkt()
            target_multi = hecobject.geom_type.startswith('MULTI')
            src_multi = feat.geometry().isMultipart()
            if not target_multi and src_multi:

                # try to convert a copy of the feature geometry to singlepart
                geom_copy = feat.geometry()
                is_single = geom_copy.convertToSingleType()
                if is_single:
                    geometry = 'ST_GeomFromText(\'{0}\', {1})'.format(geom_copy.asWkt(), srid)
                else:
                    self.rgis.addInfo('WARNING:<br>Source geometry is reported as MULTIPART but target \
                        is SINGLEPART! skipping...')
                    continue
            elif target_multi and not src_multi:
                single2multi = True
                geometry = 'ST_Multi(ST_GeomFromText(\'{0}\', {1}))'.format(geom_wkt, srid)
            else:
                geometry = 'ST_GeomFromText(\'{0}\', {1})'.format(geom_wkt, srid)
            for attr in fields:
                val = feat.attribute(attr[1].strip('"'))
                if not val == NULL:
                    vals.append('\'{0}\'::{1}'.format(val, attr[2]))
                else:
                    vals.append('NULL')
            vals.append(geometry)
            feats_def.append('({0})'.format(', '.join(vals)))
        qry += '{0};'.format(',\n\t'.join(feats_def))
        if single2multi is True:
            self.rgis.addInfo('Source geometry is SINGLEPART but the target is MULTIPART!')
        else:
            pass
        return qry

    def insert_layer(self, layer, hecobject, attr_map=None, schema=None, srid=None, selected=False):
        """
        Insert a vector layer's features into a PostGIS table of a hecras object.
        If an attribute map attr_map is specified, only the mapped attributes are imported. If 'attr_map'
        is None, it checks source layer's attribute names and compares them to column names of a target table.
        If the attribute has a corresponding name in target table then it is copied into table table.

        It can be used to copy hecobject table from one schema to another.

        Args:
            layer (QgsVectorLayer): Source QGIS layer containing the features to insert.
            hecobject (HecRasObject): Target HEC-RAS object.
            attr_map (dict): Attribute mapping dictionary, i.e. {'target_table_attr': 'src_layer_field', ...}.
            schema (str): Target schema.
            srid (int): Spatial Reference System Identifier.
            selected (bool): Flag for processing selected features only.
        """

        if schema is None:
            SCHEMA = self.SCHEMA
        else:
            SCHEMA = schema
        if srid is None:
            SRID = self.SRID
        else:
            SRID = srid

        if self.rgis.DEBUG:
            if attr_map:
                am = ['{0} - {1}'.format(key, value) for key, value in attr_map.items()]
                info = '  attr_map:\n    '
                info += '\n    '.join(am)
                self.rgis.addInfo(info)
            else:
                pass
        else:
            pass

        features, imp_attrs = self.import_layer(layer, hecobject.attrs, attr_map, selected)
        qry = self.layer_to_pgsql(features, imp_attrs, hecobject, SCHEMA, SRID)
        if qry is not None:
            self.run_query(qry)
            self.add_to_view(hecobject)
            self.rgis.addInfo('OK')
        else:
            pass

    def create_schema(self, schema_name):
        """
        Create empty schema inside PostgreSQL database.

        Args:
            schema_name (str): Name of the new schema.
        """
        qry = '''CREATE SCHEMA "{0}";'''
        qry = qry.format(schema_name)
        if self.run_query(qry) is None:
            return
        else:
            self.rgis.addInfo('<br>Schema "{0}" created.'.format(schema_name))

    def drop_schema(self, schema_name, cascade=False):
        """
        Delete schema inside PostgreSQL database.

        Args:
            schema_name (str): Name of the schema which will be deleted.
            cascade (bool): Flag forcing cascade delete.
        """
        qry = '''DROP SCHEMA "{0}" CASCADE;''' if cascade is True else '''DROP SCHEMA "{0}";'''
        qry = qry.format(schema_name)
        if self.run_query(qry) is None:
            return
        else:
            self.rgis.addInfo('<br>Schema "{0}" deleted.'.format(schema_name))

    def create_spatial_index(self):
        """
        Create PostgreSQL function create_st_index_if_not_exists(schema, table).
        The function checks if a spatial index exists for the table - if not, it is created.
        """
        qry = '''
CREATE OR REPLACE FUNCTION "{0}".create_spatial_index(schema text, t_name text)
    RETURNS VOID AS
$BODY$
DECLARE
    full_index_name text;
BEGIN
    full_index_name = schema || '_' || t_name || '_' || 'geom_idx';
    IF NOT EXISTS (
        SELECT 1
        FROM pg_class c
        JOIN pg_namespace n ON n.oid = c.relnamespace
        WHERE c.relname = full_index_name AND n.nspname = schema
        )
    THEN
        EXECUTE 'CREATE INDEX "' || full_index_name || '" ON "' || schema || '"."' || t_name || '" USING GIST (geom)';
    END IF;
END;
$BODY$
    LANGUAGE plpgsql;
'''
        qry = qry.format(self.SCHEMA)
        self.run_query(qry)
