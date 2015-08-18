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
from qgis.core import *
from qgis.utils import *

from qgis.gui import QgsMessageBar
from dlg_ras2dAreaMesh import *
from dlg_rasWaterSurfaceGeneration import *
from dlg_rasFloodplainDelineation import *

from subprocess import call
from os.path import expanduser, join, dirname, abspath, basename, isfile
import psycopg2
import psycopg2.extras
import time
import uuid
from math import sqrt, pow, atan2, pi, floor
import processing
from miscFunctions import *


debug = 1


def ras2dCreate2dArea(rgis):
  from bisect import *
  wrongGeo = False
  
  layers = Dlg2dAreaMeshLayers(rgis)
  if layers.exec_() == QDialog.Accepted:
    areas = layers.areasLayer
    nameAttr = layers.ui.cbo2dAreasNameAttr.currentText()
    meshSizeAttr = layers.ui.cbo2dAreasMeshSizeAttr.currentText()
    
    structures = layers.structuresLayer
    structMeshSizeAlongAttr = layers.ui.cboStructureMeshSizeAlongAttr.currentText()
    structMeshSizeAcrossAttr = layers.ui.cboStructureMeshSizeAcrossAttr.currentText()
    structMeshRowsAttr = layers.ui.cboStructureMeshRowsAttr.currentText()
    
    breakPoints = layers.breakPointsLayer

    srid = areas.dataProvider().crs().postgisSrid()
    geoFileName = layers.ui.lineEditGeoFile.text()
    if structures:
      addInfo(rgis, '\n\n<b>Running 2D Area</b> (%s, %s, %s, %s, %s, %s)\n' % (areas.name(), nameAttr, meshSizeAttr, structures.name(), structMeshSizeAlongAttr, structMeshSizeAcrossAttr) )
    else:
      addInfo(rgis, '\n\n<b>Running 2D Area</b> (%s, %s, %s)\n' % (areas.name(), nameAttr, meshSizeAttr) )
  elif layers.exec_() == QDialog.Rejected:
    return

  uid = str(uuid.uuid4())
  workDirName = join(expanduser("~"), "qgis_processing_temp", uid)
  call(["mkdir", join(expanduser("~"), "qgis_processing_temp")], shell=True)
  call(["mkdir", workDirName], shell=True)
  if rgis.passwd == '':
    addInfo(rgis,'\n<b>Please, define your password for the database in the connection settings!</b>')
    return
  connParams = "dbname = '%s' user = '%s' host = '%s' password = '%s'" % (rgis.dbname,rgis.user,rgis.host,rgis.passwd)
  conn = psycopg2.connect(connParams)

  
  cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
  rgis.createPgFunctionCreateIndexIfNotExists()
  addInfo(rgis, "  Creating tables..." )
  
  # create 2dareas table
  qry = 'drop table if exists %s.areas2d cascade;' % rgis.schName
  qry += 'create table %s.areas2d (gid serial primary key, name text, cellsize double precision, geom geometry(Polygon, %i));' % (rgis.schName, srid)
  qry += "select create_st_index_if_not_exists('%s','areas2d');" % (rgis.schName)

  # create structures table
  qry += 'drop table if exists %s.struct_lines cascade;' % rgis.schName
  qry += 'create table %s.struct_lines (gid serial primary key, aid integer, cellsizealong double precision, cellsizeacross double precision, meshrows integer, geom geometry(Linestring, %i));' % (rgis.schName, srid)
  qry += "select create_st_index_if_not_exists('%s','struct_lines');" % (rgis.schName)

  # create structure routes table
  qry += 'drop table if exists %s.struct_lines_m cascade;' % rgis.schName
  qry += 'create table %s.struct_lines_m (gid serial primary key, aid integer, cellsizealong double precision, cellsizeacross double precision, meshrows integer, geom geometry(LinestringM, %i));' % (rgis.schName, srid)
  qry += "select create_st_index_if_not_exists('%s','struct_lines_m');" % (rgis.schName)

  # create breakpoints table
  qry += 'drop table if exists %s.breakpoints cascade;' % rgis.schName
  qry += 'create table %s.breakpoints (gid serial primary key, aid integer, sid integer, m double precision, geom geometry(Point, %i));' % (rgis.schName, srid)
  
  # 2d mesh points table
  qry += 'drop table if exists %s.mesh_pts cascade;' % rgis.schName
  qry += 'create table %s.mesh_pts (gid serial primary key, aid integer, lid integer, cellsize double precision, geom geometry(Point, %i));' % (rgis.schName, srid)
  qry += "select create_st_index_if_not_exists('%s','mesh_pts');" % (rgis.schName)

  # structures buffers table
  qry += 'drop table if exists %s.wyciecie_pkt_org;' % rgis.schName
  qry += 'create table if not exists %s.wyciecie_pkt_org (gid serial primary key,geom geometry(Polygon, %i));' % (rgis.schName, srid)
  qry += "select create_st_index_if_not_exists('%s','wyciecie_pkt_org');" % (rgis.schName)


  # we need this to complete query execution
  time.sleep(0.05)
  cur.execute(qry)
  conn.commit()

  # addInfo(rgis, "Creating function makegrid..." )

  qry += '''CREATE OR REPLACE FUNCTION makegrid(geometry, float, integer)
  RETURNS geometry AS
  'SELECT ST_Collect(st_setsrid(ST_POINT(x/1000000::float,y/1000000::float),$3)) FROM 
    generate_series(floor(st_xmin($1)*1000000)::bigint, ceiling(st_xmax($1)*1000000)::bigint,($2*1000000)::bigint) as x,
    generate_series(floor(st_ymin($1)*1000000)::bigint, ceiling(st_ymax($1)*1000000)::bigint,($2*1000000)::bigint) as y 
  where st_intersects($1,st_setsrid(ST_POINT(x/1000000::float,y/1000000::float),$3))'
  LANGUAGE sql;'''

  cur.execute(qry)
  conn.commit()

  addInfo(rgis, "  Inserting polygons into 2D areas PostGIS table..." )

  areaFeats = areas.getFeatures()

  qry = 'INSERT INTO %s.areas2d (name, cellsize, geom) VALUES \n' % rgis.schName

  for feat in areaFeats:
    areaName = str(feat[nameAttr])
    cellSize = float(feat[meshSizeAttr])
    geom = feat.geometry()
    polygon = geom.asPolygon()
    qry += "('%s', %.6f, ST_GeomFromText('POLYGON((" % (areaName, cellSize)
    for pt in polygon[0]:
      qry += '%.4f %.4f, ' % (pt.x(), pt.y())
    
    qry = qry[:-2] + "))',%i)),\n" % srid
    
  qry = qry[:-2] + ';'

  cur.execute(qry)
  conn.commit()
    
  addInfo(rgis, "  Creating preliminary regular mesh points..." )

  qry = '''insert into %s.mesh_pts (aid, lid, geom)
  SELECT gid, -1, (ST_Dump(makegrid(geom, cellsize, %i))).geom as geom from %s.areas2d;''' % (rgis.schName, srid, rgis.schName)
  qry += '''
  with areas2dshrinked as (
    select gid, ST_Buffer(a2d.geom,-0.3*a2d.cellsize) as geom
    from %s.areas2d as a2d
  )
  delete from 
     %s.mesh_pts as pkts_a where pkts_a.gid not in (
     select pkts.gid from 
       %s.mesh_pts as pkts, areas2dshrinked where
     pkts.geom && areas2dshrinked.geom
     and
     ST_Intersects(pkts.geom, areas2dshrinked.geom));
  ''' % ((rgis.schName,) * 3)
  cur.execute(qry)

  addInfo(rgis, "  Inserting structures into PostGIS table" )

  if structures:
    structFeats = structures.getFeatures()

    qry = 'INSERT INTO %s.struct_lines (cellsizealong, cellsizeacross, meshrows, geom) VALUES \n' % rgis.schName

    for feat in structFeats:
      if not feat[structMeshSizeAlongAttr] or not feat[structMeshSizeAcrossAttr]:
        addInfo(rgis, "\n\n<b>Warning: Some structures have no cell size specified. Crash expected...</b>\n\n" )
      csalong = float(feat[structMeshSizeAlongAttr])
      csacross = float(feat[structMeshSizeAcrossAttr])
      rows = int(feat[structMeshRowsAttr])
      geom = feat.geometry()
      line = geom.asPolyline()
      qry += "(%.2f, %.2f, %i, ST_GeomFromText('LINESTRING(" % (csalong, csacross, rows)
      if line:
        for pt in line:
          qry += '%.4f %.4f, ' % (pt.x(), pt.y())
      else:
        addInfo(rgis,"&nbsp;&nbsp;<b>Structure line id=%i has a wrong (empty) geometry!</b>\n" % feat['Id'])
        wrongGeo = True
      qry = qry[:-2] + ")',%i)),\n" % srid

    qry = qry[:-2] + ';'
    if wrongGeo:
      print qry
      addInfo(rgis, "\n  Check (or replace) structure lines with wrong geometry and try again.\n\n")
      return
    cur.execute(qry)
    conn.commit()
  
  # insert breakpoints to database
  
  if breakPoints:
    breakFeats = breakPoints.getFeatures()

    qry = 'INSERT INTO %s.breakpoints (geom) VALUES \n' % rgis.schName

    for feat in breakFeats:
      geom = feat.geometry()
      pt = geom.asPoint()
      qry += "(ST_GeomFromText('POINT( %.4f %.4f )',%i)),\n" % (pt.x(), pt.y(), srid)
    
    qry = qry[:-2] + ';'
    cur.execute(qry)
    
  # find which structure line belongs to which 2d area
  qry = '''
  with ids as (
  select a.gid as agid, l.gid as lgid
  from
    %s.struct_lines l, %s.areas2d a
  where
    a.geom && l.geom and
    ST_Contains(a.geom, l.geom)
    )
  update %s.struct_lines l set aid = ids.agid
  from ids
  where ids.lgid = l.gid;
  ''' % ((rgis.schName,) * 3)
  cur.execute(qry)

  addInfo(rgis, "  Creating routes along structure lines..." )

  qry = 'insert into %s.struct_lines_m (aid, cellsizealong, cellsizeacross, meshrows, geom) select aid, cellsizealong, cellsizeacross, meshrows, (ST_Dump(ST_AddMeasure(geom, 0, ST_Length(geom)))).geom from %s.struct_lines;' % ((rgis.schName,) * 2)

  addInfo(rgis, "  Deleting orignal mesh points near structures..." )
  qry += 'insert into %s.wyciecie_pkt_org (geom) select ST_Buffer(geom, meshrows*cellsizeacross+cellsizealong*0.6, \'endcap=flat join=round\') from %s.struct_lines_m;' % ((rgis.schName,) * 2)
  qry += 'delete from %s.mesh_pts as p using %s.wyciecie_pkt_org as w where w.geom && p.geom and ST_Intersects(w.geom, p.geom);' % ((rgis.schName,) * 2)
  cur.execute(qry)
  conn.commit()
  
  addInfo(rgis, "  Creating mesh points along structures..." )
  
  # find structures that breakpoints is located on ( tolerance = 10 [map units] )
  breakPtsLocTol = 10
  
  if breakPoints:
    qry = '''
    with ids as (
    select s.gid as sgid, p.gid as pgid
    from
      %s.struct_lines s, %s.breakpoints p
    where
      ST_Buffer(s.geom, %.2f) && p.geom and
      ST_Contains(ST_Buffer(s.geom, 10), p.geom)
      )
    update %s.breakpoints p set sid = ids.sgid
    from ids
    where ids.pgid = p.gid;
    ''' % (rgis.schName, rgis.schName, breakPtsLocTol, rgis.schName)
    cur.execute(qry)
    
    # find measures of breakpoints along structure_lines
    # there was a change in the alg name between PostGIS 2.0 and 2.1
    # ST_Line_Locate_Point -> ST_LineLocatePoint
    qry = "select PostGIS_Full_Version() as ver;"
    cur.execute(qry)
    postgisVersion = cur.fetchall()[0]['ver'].split('\"')[1][:5]
    pgMajV = int(postgisVersion[:1])
    pgMinV = int(postgisVersion[2:3])
    if pgMajV < 2:
      locate = "ST_Line_Locate_Point"
    elif pgMajV >= 2 and pgMinV == 0:
      locate = "ST_Line_Locate_Point"
    else:
      locate = "ST_LineLocatePoint"
    qry = '''
    update %s.breakpoints p set m = %s(s.geom, p.geom)
    from
      %s.struct_lines s
    where p.sid = s.gid;
    ''' % (rgis.schName, locate, rgis.schName)
    cur.execute(qry)

  addInfo(rgis, "  Creating aligned mesh points along structures..." )
  
  qry = "SELECT gid, aid, cellsizealong, cellsizeacross, ST_Length(geom) as len, meshrows as rows from %s.struct_lines_m;" % rgis.schName
  cur.execute(qry)

  for line in cur.fetchall():
    odl = float(line['cellsizealong'])
    szer = float(line['cellsizeacross'])
    id = line['gid']
    leng = float(line['len'])
    rows = int(line['rows'])
    imax = int(leng/(odl)) 
    
    qry = "SELECT DISTINCT b.m from %s.breakpoints b, %s.struct_lines s where b.sid = %i;" % (rgis.schName, rgis.schName, id)
    cur.execute(qry)
    ms = cur.fetchall()
  
    if not ms: # no breakpoints: create aligned mesh at regular interval = cellsize
      addInfo(rgis, "  Creating aligned mesh points for structure id=%i" % id )
      for i in range(0, imax+1):
        dist = i * odl
        for j in range(0,rows):
          qry = 'insert into %s.mesh_pts (lid, aid, cellsize, geom) select gid, aid, %.2f, ST_Centroid(ST_LocateAlong(geom, %.2f, %.2f)) from %s.struct_lines_m where gid = %i;' % (rgis.schName, odl, dist, j*szer+szer/2, rgis.schName, id)
          qry += 'insert into %s.mesh_pts (lid, aid, cellsize, geom) select gid, aid, %.2f, ST_Centroid(ST_LocateAlong(geom, %.2f, -%.2f)) from %s.struct_lines_m where gid = %i;' % (rgis.schName, odl, dist, j*szer+szer/2, rgis.schName, id)
          cur.execute(qry)
    
    else: # create cellfaces at structure breakpoints
      addInfo(rgis, "  Creating breakpoints for structure id=%i " % id )
      sm_param = 4
      db_min = 10.**9
      bm = [] # breakpoints m list (linear locations on current structure) 
      mpts = [] # linear measures of mesh points to be created
      
      for i, m in enumerate(ms):
        bm.append(float(m['m']))
      
      # sort the list
      bm.sort()
      
      for i, m in enumerate(bm):
        # calculate minimal distance between breakpoints
        if i > 0:
          db_min = min( bm[i] - bm[i-1], db_min)
      # create 2 mesh points on both sides of a breakpoint at a distance db_min / sm_param
      dist_min = min( db_min / sm_param, 0.5 * odl / leng )
      cs_min = dist_min * leng
      for m in bm:
        mpts.append(max(0.0001, m - dist_min))
        mpts.append(min(m + dist_min, 0.9999))

      # find gaps between points along a structure longer than 3 * dist_min
      gaps = [] 
      for i, m in enumerate(mpts):
        if i > 0:
          dist = m - mpts[i-1]
          if dist > 3 * dist_min:
            gaps.append([m,dist])
      
      # create mesh points at gaps
      for g in gaps:
        m, dist = g
        # how many points to insert?
        k = int(floor(dist / (2*dist_min)))
        # distance between new points
        cs = dist / k 
        for j in range(0,k):
          mpts.append(m - j * cs)
          
      # insert aligned mesh points into table
      for m in sorted(mpts):
        for j in range(0,rows):
          qry = 'insert into %s.mesh_pts (lid, aid, cellsize, geom) select gid, aid, %.2f, ST_Centroid(ST_LocateAlong(geom, %.2f, %.2f)) from  %s.struct_lines_m where gid = %i;\n' % (rgis.schName, cs_min, m*leng, j*odl+odl/2, rgis.schName, id)
          qry += 'insert into %s.mesh_pts (lid, aid, cellsize, geom) select gid, aid, %.2f, ST_Centroid(ST_LocateAlong(geom, %.2f, -%.2f)) from %s.struct_lines_m where gid = %i;' % (rgis.schName, cs_min, m*leng, j*odl+odl/2, rgis.schName, id)
          cur.execute(qry)
      
  conn.commit()
  
  
  addInfo(rgis, "  Deleting mesh points located too close to each other or outside the 2D area..." )
  
  qry = '''delete from %s.mesh_pts as p1 using %s.mesh_pts as p2 
    where p1.lid <> -1 and p2.lid <> -1 and p1.lid <> p2.lid and p1.gid > p2.gid
    and ST_DWithin(p1.geom, p2.geom, 0.75 * least(p1.cellsize, p2.cellsize))
    ;''' % ((rgis.schName,) * 2)
  qry += '''delete from %s.mesh_pts as p using %s.areas2d as a 
    where 
      not ST_Contains( ST_Buffer(a.geom,-0.3*a.cellsize), p.geom )
    ;''' % ((rgis.schName,) * 2)
  cur.execute(qry)
  conn.commit()

  if geoFileName:
    ras2dSaveMeshPtsToGeometry(rgis, geoFileName)


def ras2dSaveMeshPtsToGeometry(rgis,geoFileName=None):
  """Saves mesh points from current schema and table 'mesh_pts' to HEC-RAS geometry file"""
  if not geoFileName:
    s = QSettings()
    lastGeoFileDir = s.value("rivergis/lastGeoDir", "")
    geoFileName = QFileDialog.getSaveFileName(None, 'Target HEC-RAS geometry file', directory=lastGeoFileDir, filter='HEC-RAS geometry (*.g**)')
    s.setValue("rivergis/lastGeoDir", dirname(geoFileName))

  connParams = "dbname = '%s' user = '%s' host = '%s' password = '%s'" % (rgis.dbname,rgis.user,rgis.host,rgis.passwd)
  conn = psycopg2.connect(connParams)
  cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
  addInfo(rgis, "  Saving mesh to HEC-RAS geometry file...")

  # get mesh points extent
  qry = 'select ST_XMin(ST_collect(geom)) as xmin, ST_XMax(ST_collect(geom)) as xmax,ST_YMin(ST_collect(geom)) as ymin, ST_YMax(ST_collect(geom)) as ymax from %s.mesh_pts;' % rgis.schName
  cur.execute(qry)
  pExt = cur.fetchone()
  xmin, xmax, ymin, ymax = [pExt['xmin'], pExt['xmax'], pExt['ymin'], pExt['ymax']]
  buf = 300
  pExtStr = '%.2f, %.2f, %.2f, %.2f' % (xmin-buf, xmax+buf, ymax+buf, ymin-buf)

  # get list of mesh areas
  qry = 'select gid, name, ST_X(ST_Centroid(geom)) as x, ST_Y(ST_Centroid(geom)) as y, ST_NPoints(geom) as ptsnr from %s.areas2d;' % rgis.schName
  cur.execute(qry)
  t = ''

  for area in cur.fetchall():
    t += '\r\n\r\nStorage Area={:14}             ,{:14},{:14}\r\n'.format(area['name'], area['x'], area['y'])
    t += 'Storage Area Surface Line= {:d}\r\n'.format(area['ptsnr'])
    
    qry = 'select ST_AsText(geom) as geom from %s.areas2d where gid=%i;' % (rgis.schName, area['gid'])
    cur.execute(qry)
    res = cur.fetchall()[0]['geom']
    ptsList = res[9:-2].split(',')
    for pt in ptsList:
      x = float( pt.split(' ')[0] )
      y = float( pt.split(' ')[1] )
      t += '{:>16.4f}'.format( x)
      t += '{:>16.4f}\r\n'.format(y)

    t += 'Storage Area Type= 0\r\n'
    t += 'Storage Area Area=\r\n'
    t += 'Storage Area Min Elev=\r\n'
    t += 'Storage Area Is2D=-1\r\n'
    t += 'Storage Area Point Generation Data=,,,\r\n'
    
    qry = 'select ST_X(geom) as x, ST_Y(geom) as y from %s.mesh_pts WHERE aid = %i;' % (rgis.schName, area['gid'])
    cur.execute(qry)
    pkty = cur.fetchall()
    
    t += 'Storage Area 2D Points= %i\r\n' % len(pkty)
    for i, pt in enumerate(pkty):
      if i % 2 == 0:
        t += '{:16.2f}{:16.2f}'.format(float(pt['x']), float(pt['y']))
      else:
        t += '{:16.2f}{:16.2f}\r\n'.format(float(pt['x']), float(pt['y']))
        
    t += '\r\nStorage Area 2D PointsPerimeterTime=25Jan2015 01:00:00\r\n'
    t += 'Storage Area Mannings=0.06\r\n'
    t += '2D Cell Volume Filter Tolerance=0.003\r\n'
    t += '2D Face Profile Filter Tolerance=0.003\r\n'
    t += '2D Face Area Elevation Profile Filter Tolerance=0.003\r\n'
    t += '2D Face Area Elevation Conveyance Ratio=0.02\r\n\r\n'

  cur.close()
  conn.close()
  
  if not isfile(geoFileName):
    createNewGeometry(geoFileName, pExtStr)

  geoFile = open(geoFileName, 'rb')
  geoLines = geoFile.readlines()
  geoFile.close()
  
  geoFile = open(geoFileName, 'wb')
  geo = ""
  for line in geoLines:
    if not line.startswith('Chan Stop Cuts'):
      geo += line
    else:
      geo += t
      geo += line
  geoFile.write(geo)
  geoFile.close()

  addInfo(rgis, '\n  Mesh points saved to HEC-RAS geometry file.\n')
  
def ras2dPreviewMesh(rgis):
  """Loads the mesh points to the canvas and builds Voronoi polygons"""
  if rgis.passwd == '':
    addInfo(rgis,'\n<b>Please, define your password for the database in the connection settings!</b>')
    return
  connParams = "dbname = '%s' user = '%s' host = '%s' password = '%s'" % (rgis.dbname,rgis.user,rgis.host,rgis.passwd)
  conn = psycopg2.connect(connParams)

  uri = QgsDataSourceURI()
  uri.setConnection(rgis.host, "5432", rgis.dbname, rgis.user, rgis.passwd)
  uri.setDataSource(rgis.schema.name, "mesh_pts", "geom")
  uri.setSrid(str(rgis.crs.postgisSrid()))
  mesh_pts = QgsVectorLayer(uri.uri(), "mesh_pts", "postgres")

  t = "dbname='%s' host=%s port=5432 user='%s' password='%s' sslmode=disable key='gid' table=\"%s\".\"mesh_pts\" (geom) sql=" % (rgis.dbname, rgis.host, rgis.user, rgis.passwd, rgis.schema.name)
  # print mesh_pts.dataProvider().crs().postgisSrid()
  # for a in mesh_pts.getFeatures():
  #   poly = a.geometry().asPolygon()[0]
  voronoi = processing.runalg("qgis:voronoipolygons",t,100,None)
  processing.load(voronoi, "Mesh preview")

  


  
def ras2dCreateWaterSurfaceRaster(rgis):
  addInfo(rgis, '\n<b>Running Create Water Surface Raster</b>' )
  layers = DlgRasWaterSurfaceGeneration(rgis)
  if layers.exec_() == QDialog.Accepted:
    ptsLayer = layers.ptsLayer
    Water_level_attribute = layers.ui.cboWselAttr.currentText()
    Cell_size = int(layers.ui.cellSize.text())
    Tile_size = int(layers.ui.tileSize.text())
    Tile_buffer_size = int(layers.ui.bufferSize.text())
  elif layers.exec_() == QDialog.Rejected:
    return
    
  Result_raster="WSEL_Raster_temporary"
  uid = str(uuid.uuid4())

  workDirName = join(expanduser("~"), "qgis_processing_temp", uid)
  stdoutFileName = join(expanduser("~"), "qgis_processing_temp\\stdout_%s.txt" % uid)
  call(["mkdir", join(expanduser("~"), "qgis_processing_temp")], shell=True)
  call(["mkdir", workDirName], shell=True)
  tileListFile = join(workDirName, 'tiles.txt')
  vrtFile = join(workDirName, 'tiles.vrt')
  sys.stdout = sys.stderr = open(stdoutFileName, 'w')

  addInfo(rgis,"  Creating tiles...")
  
  pExt = ptsLayer.extent()
  xmin = pExt.xMinimum()
  xmax = pExt.xMaximum()
  ymin = pExt.yMinimum()
  ymax = pExt.yMaximum()
  pExtStr = '%.2f, %.2f, %.2f, %.2f' % (xmin, xmax, ymin, ymax)

  xNrTiles = int(floor((ymax-ymin)/Tile_size))+1
  yNrTiles = int(floor((xmax-xmin)/Tile_size))+1

  nr_of_rows = '%i,%i' % (xNrTiles, yNrTiles)
  lower_left = '%.4f,%.4f' % (xmin, ymin)
  spacing = '%.4f,%.4f' % (Tile_size,Tile_size)
  # siatka = processing.runalg("grass7:v.mkgrid",nr_of_rows,0,lower_left,spacing,"0",False,False,"0,1,0,1",0,None)
  siatka = processing.runalg('qgis:vectorgrid', pExtStr, Tile_size, Tile_size, 0, None)

  siatkaLayer = processing.getObject(siatka['OUTPUT'])
  siatkaLayer.startEditing()
  attrs= siatkaLayer.pendingFields()
  siatkaLayer.dataProvider().addAttributes( [ QgsField("grid_id", QVariant.Int) ] )
  siatkaLayer.commitChanges()

  siatkaLayer.startEditing()
  feats = siatkaLayer.getFeatures()
  for feat in feats:
    feat['grid_id'] = feat.id()
    siatkaLayer.updateFeature(feat)
  siatkaLayer.commitChanges()

  rgis.statusBar.showMessage("Processed {} %".format('??'))

  siatkaBuf = processing.runalg("qgis:fixeddistancebuffer",siatkaLayer,Tile_buffer_size,5,False,None)
  siatkaLayer1 = processing.getObject( processing.runalg("qgis:fixeddistancebuffer",siatkaLayer,Cell_size,5,False,None)['OUTPUT'] )

  aaa = processing.runalg("qgis:intersection",ptsLayer,siatkaBuf['OUTPUT'],None)
  pts_in_tiles = processing.getObject( aaa['OUTPUT'] )

  ptsList = []
  tilesList = ""

  feats = siatkaLayer1.getFeatures()
  nFeats = siatkaLayer1.featureCount()
  tilesNr = 0

  addInfo(rgis,"  Creating data for tiles...")
  rgis.statusBar.showMessage("Processed {} %".format(2))

  for i, feat in enumerate(feats):
    perc = (2 + int(28 * i / nFeats))
    rgis.statusBar.showMessage("Processed {} %".format(int(perc)))
    fid = feat['grid_id']
    
    sel = pts_in_tiles.getFeatures( QgsFeatureRequest().setFilterExpression ( u'"grid_id" = %i' % fid ) )
    pts_in_tiles.setSelectedFeatures( [ f.id() for f in sel ] )
    if pts_in_tiles.selectedFeatureCount() < 10: # zbyt mala liczba punktow w kafelku - pomijam
      continue
    p1 = processing.runalg("qgis:saveselectedfeatures",pts_in_tiles,None)
    pts_in_tiles.removeSelection()
    
    sel = siatkaLayer1.getFeatures( QgsFeatureRequest().setFilterExpression ( u'"grid_id" = %i' % fid ) )
    siatkaLayer1.setSelectedFeatures( [ f.id() for f in sel ] )
    s1 = processing.runalg("qgis:saveselectedfeatures",siatkaLayer1,None)
    pts_in_tiles.removeSelection()
    
    ptsList.append([fid, p1['OUTPUT_LAYER'], s1['OUTPUT_LAYER']])
    tilesNr += 1

  addInfo(rgis,"  Interpolating tiles...")

  for i, p in enumerate(ptsList):
    perc = 30 + int(60 * i / tilesNr)
    rgis.statusBar.showMessage("Processed {} %".format(int(perc)))
    fid = p[0]
    pts_in_tile = processing.getObject( abspath(p[1]) )
    tile = processing.getObject( abspath(p[2]) )
    tExt = tile.extent()
    xmin = tExt.xMinimum()
    xmax = tExt.xMaximum()
    ymin = tExt.yMinimum()
    ymax = tExt.yMaximum()
    tExtStr = '%.2f, %.2f, %.2f, %.2f' % (xmin-Tile_buffer_size, xmax+Tile_buffer_size, ymin-Tile_buffer_size, ymax+Tile_buffer_size)
    
    r1 = processing.runalg("saga:naturalneighbour",pts_in_tile,Water_level_attribute,True,tExtStr,Cell_size,None)
    r2 = processing.runalg("saga:closegaps",r1['USER_GRID'],None,0.1,None)
    r3 = processing.runalg("saga:gaussianfilter",r2['RESULT'],1,0,4*Cell_size,None)
    r4 = processing.runalg("saga:clipgridwithpolygon",r3['RESULT'],tile,None)
    tilesList += r4['OUTPUT']+'\n'

  # addInfo(rgis,"\nSaving temporary results to:\n%s" % workDirName)

  velFile = open(tileListFile, "w")
  velFile.write(tilesList)
  velFile.close()

  call(["gdalbuildvrt", "-input_file_list", tileListFile, vrtFile])
  r5 = processing.runalg("gdalogr:cliprasterbyextent",vrtFile,"-9999",pExtStr,"",None)
  processing.load(r5['OUTPUT'], Result_raster)
  rgis.statusBar.clearMessage()
  addInfo(rgis,"  Done!\n Review temporary results and, eventually, save them to disk.")


def createNewGeometry(filename, extent):
  t = 'Geom Title=Import from RiverGIS\r\nProgram Version=5.00\r\n'
  t += 'Viewing Rectangle= %s' % extent
  t += '\r\n\r\nChan Stop Cuts=-1\r\n\r\n\r\n'
  t += 'Use User Specified Reach Order=0\r\n'
  t += 'GIS Ratio Cuts To Invert=-1\r\n'
  t += 'GIS Limit At Bridges=0\r\n'
  t += 'Composite Channel Slope=5\r\n'
  geoFile = open(filename, 'wb')
  geoFile.write(t)
  geoFile.close()
  