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

from PyQt4.QtCore import *
from PyQt4.QtGui import *
import psycopg2
import psycopg2.extras
import processing
from miscFunctions import *
from time import sleep

debug = 1

def ras1dCreateTables(rgis):
  if rgis.passwd == '':
    addInfo(rgis,'\n<b>Please, define your password for the database in the connection settings!</b>')
    return
  connParams = "dbname = '%s' user = '%s' host = '%s' password = '%s'" % (rgis.dbname,rgis.user,rgis.host,rgis.passwd)
  conn = psycopg2.connect(connParams)
  srid = rgis.crs.postgisSrid()

  cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
  rgis.createPgFunctionCreateIndexIfNotExists()
  addInfo(rgis, "  Creating tables..." )
  
  # versions table --- points and xsections have a version id. A version can reflect natural changes in xsection shape or different xsection variants (different land cover)

  # gid - pkey
  # vid - version id, (i.e. ISOK, W0, PZRP, itp.)
  # name - version name
  # desript - version description
  # no geometry
  qry = 'drop table if exists %s.versions cascade;' % rgis.schName
  qry += 'create table %s.versions (gid serial primary key, vid text, name text, descript text);' % (rgis.schName)

  # rivers table

  # gid - pkey
  # river_id - river id (id_hyd_r)
  # name - river full name
  # shortname - short name
  # descript - river description
  # no geometry
  qry += 'drop table if exists %s.rivers cascade;' % rgis.schName
  qry += 'create table %s.rivers (gid serial primary key, rid integer not null, name text, shortname text, descript text);' % (rgis.schName)

  # river reaches table

  # gid - pkey
  # rid - river gid
  # name - full name of a reach
  # shortname - short name
  # statup - station of the upstream end of a reach (for easier life this MUST be integer in [m] or [ft])
  # statdown - station of the downstream end
  # descript - description of a reach
  # geom - linestring
  qry += 'drop table if exists %s.reaches cascade;' % rgis.schName
  qry += 'create table %s.reaches (gid serial primary key, rid integer not null, name text, shortname text, statup integer, statdown integer, descript text, geom geometry(LINESTRING, %i));' % (rgis.schName, srid)
  qry += "select create_st_index_if_not_exists('%s','reaches');" % (rgis.schName)

  # cross-sections table

  # gid - pkey
  # rid - REACH id
  # station - xsection station along a reach
  # descript - description of a reach
  # vid - version id
  qry += 'drop table if exists %s.xsecs cascade;' % rgis.schName
  qry += 'create table %s.xsecs (gid serial primary key, rid integer not null, station integer, descript text, geom geometry(LINESTRING, %i));' % (rgis.schName, srid)
  qry += "select create_st_index_if_not_exists('%s','xsecs');" % (rgis.schName)

  # points table

  # gid - pkey
  # xid - xsection gid
  # station - point station along a xsection
  # elevation - point elevation
  # cover - a land cover code
  # is_node - if it is a node (a key point of a xsection), it cannot be filtered out
  # vid - version id
  # active - is it an active point or is it filtered out or deactivated
  # descript - a description
  # geom - point geometry
  qry += 'drop table if exists %s.points cascade;' % rgis.schName
  qry += 'create table %s.points (gid serial primary key, xid integer, station double precision, elevation double precision, cover text, is_node integer, vid integer, active double precision, descript text, geom geometry(POINT, %i));' % (rgis.schName, srid)
  qry += "select create_st_index_if_not_exists('%s','points');" % (rgis.schName)

  #  banks table

  # gid - pkey
  # rid - reach id
  # side - left or right
  # descript - description of a levee
  qry += 'drop table if exists %s.banks cascade;' % rgis.schName
  qry += 'create table %s.banks (gid serial primary key, rid integer, side text, descript text, geom geometry(LINESTRING, %i));' % (rgis.schName, srid)
  qry += "select create_st_index_if_not_exists('%s','banks');" % (rgis.schName)

  #  levees table

  # gid - pkey
  # rid - reach id
  # side - left or right
  # descript - description of a bank
  qry += 'drop table if exists %s.levees cascade;' % rgis.schName
  qry += 'create table %s.levees (gid serial primary key, rid integer, side text, descript text, geom geometry(LINESTRING, %i));' % (rgis.schName, srid)
  qry += "select create_st_index_if_not_exists('%s','levees');" % (rgis.schName)

  # models table

  # gid - pkey
  # name - model name
  # xsecs - xsections' gids array (http://www.postgresql.org/docs/current/static/arrays.html)
  # vid - version id
  # descript - description of a model
  # no geometry
  qry += 'drop table if exists %s.models cascade;' % rgis.schName
  qry += 'create table %s.models (gid serial primary key, rid integer not null, station integer, descript text, geom geometry(LINESTRING, %i));' % (rgis.schName, srid)


  sleep(0.05)
  cur.execute(qry)
  conn.commit()

