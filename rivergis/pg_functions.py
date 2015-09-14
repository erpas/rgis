# -*- coding: utf-8 -*-

"""
/***************************************************************************
Name                 : RiverGIS
Description          : HEC-RAS tools for QGIS
Date                 : January, 2015
copyright            : (C) 2015 by RiverGIS Group
email                : rpasiok@gmail.com
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

import psycopg2
import psycopg2.extras

def createAllPgFunctions(rgis):
  createPgFunctionCreateIndexIfNotExists(rgis)



def createPgFunctionCreateIndexIfNotExists(rgis):
  cur = rgis.conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
  qry = '''CREATE OR REPLACE FUNCTION create_st_index_if_not_exists
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
  LANGUAGE plpgsql VOLATILE;'''
  cur.execute(qry)
  rgis.conn.commit()
