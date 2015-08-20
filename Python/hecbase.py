__author__ = 'ldebek'

import psycopg2
import sys
from qgis.core import QgsVectorLayer, QgsMapLayerRegistry, QgsDataSourceURI
from hecbase import *

class HecDatabase(object):
    """
    Class handling database and hecobjects.
    """
    def __init__(self, dbname, host, port, user, password):
        self.dbname = dbname
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.con = None
        self.uri = None
        self.vlayer = None
        self.hecobjects = {}

    def connect_pg(self):
        try:
            self.con = psycopg2.connect(database=self.dbname, host=self.host, port=self.port, user=self.user, password=self.password)
        except Exception, e:
            print(e)
            sys.exit(1)

    def disconnect_pg(self):
        if self.con:
            self.con.close()
        else:
            print('There is no opened connection!')

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

    def register(self, obj):
        key = obj.name
        self.hecobjects[key] = obj

    def crete_hecobject(self, hecobject, schema, srid):
        obj = hecobject(schema, srid)
        qry = obj.build_table_sql
        HecDatabase.run_sql(qry)
        HecDatabase.register(obj)


    def add_to_view(self):
        self.uri = QgsDataSourceURI()
        self.uri.setConnection(self.host, self.port, self.dbname, self.user, self.password)
        self.uri.setDataSource(self.schema, self.name, 'geom')
        self.vlayer = QgsVectorLayer(self.uri.uri(), self.name, 'postgres')
        QgsMapLayerRegistry.instance().addMapLayer(self.vlayer)
