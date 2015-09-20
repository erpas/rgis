# -*- coding: utf-8 -*-

from subprocess import call
from os.path import expanduser, join
import uuid

import psycopg2
import psycopg2.extras

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *
from qgis.gui import *
from qgis.utils import *
from math import floor
from ui.ui_ras2dAreaMesh import *
from ras2dSaveMeshPtsToGeometry import *


class DlgRasCreate2dFlowAreas(QDialog):
  '''
  Dialog for creating 2d Flow Areas.
  '''
  def __init__(self, rgis):
    QDialog.__init__(self)
    self.ui = Ui_AreaMesh()
    self.ui.setupUi(self)
    self.rgis = rgis
    self.schName = rgis.schema
    
    QObject.connect(self.ui.geoFileBtn, SIGNAL("clicked()"), self.chooseGeoFile)
    
    QObject.connect(self.ui.buttonBox, SIGNAL("accepted()"), self.acceptDialog)
    QObject.connect(self.ui.buttonBox, SIGNAL("rejected()"), self.reject)
    QObject.connect(self.ui.helpButton, SIGNAL("clicked()"), self.displayHelp)
    
    QObject.connect(self.ui.cbo2dAreas,SIGNAL("currentIndexChanged(int)"),self.cbo2dAreasChanged)
    QObject.connect(self.ui.cboStructures,SIGNAL("currentIndexChanged(int)"),self.cboStructuresChanged)
    QObject.connect(self.ui.cboBreakPoints,SIGNAL("currentIndexChanged(int)"),self.cboBreakPointsChanged)
    
    self.ui.cbo2dAreas.addItem("")
    self.ui.cboStructures.addItem("")
    self.ui.cboBreakPoints.addItem("")
    
    self.populateLayerCombos()
    self.areasLayer = None
    self.structuresLayer = None
    self.breakPointsLayer = None
  
  def chooseGeoFile(self):
    s = QSettings()
    lastGeoFileDir = s.value("rivergis/lastGeoDir", "")
    geoFilename = QFileDialog.getSaveFileName(None, 'Target HEC-RAS geometry file', directory=lastGeoFileDir, filter='HEC-RAS geometry (*.g**)')
    s.setValue("rivergis/lastGeoDir", dirname(geoFilename))
    self.ui.lineEditGeoFile.setText( geoFilename )

  def acceptDialog(self):
    wrongGeo = False
    if not self.areasLayer: # no areas layer
      return
    self.rgis.addInfo("Creating function makegrid..." )
    areas = self.areasLayer
    nameAttr = self.ui.cbo2dAreasNameAttr.currentText()
    meshSizeAttr = self.ui.cbo2dAreasMeshSizeAttr.currentText()

    structures = self.structuresLayer
    structMeshSizeAlongAttr = self.ui.cboStructureMeshSizeAlongAttr.currentText()
    structMeshSizeAcrossAttr = self.ui.cboStructureMeshSizeAcrossAttr.currentText()
    structMeshRowsAttr = self.ui.cboStructureMeshRowsAttr.currentText()

    breakPoints = self.breakPointsLayer

    srid = areas.dataProvider().crs().postgisSrid()
    geoFileName = self.ui.lineEditGeoFile.text()
    if structures:
      self.rgis.addInfo('\n\n<b>Running 2D Area</b> (%s, %s, %s, %s, %s, %s)\n' % (areas.name(), nameAttr, meshSizeAttr, structures.name(), structMeshSizeAlongAttr, structMeshSizeAcrossAttr) )
    else:
      self.rgis.addInfo('\n\n<b>Running 2D Area</b> (%s, %s, %s)\n' % (areas.name(), nameAttr, meshSizeAttr) )
    QApplication.setOverrideCursor(Qt.WaitCursor)
    uid = str(uuid.uuid4())
    workDirName = join(expanduser("~"), "qgis_processing_temp", uid)
    call(["mkdir", join(expanduser("~"), "qgis_processing_temp")], shell=True)
    call(["mkdir", workDirName], shell=True)

    # cur = self.rgis.conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    self.rgis.addInfo("  Creating tables..." )

    # create 2dareas table
    qry = 'drop table if exists %s.areas2d cascade;' % self.schName
    qry += 'create table %s.areas2d (gid serial primary key, name text, cellsize double precision, geom geometry(Polygon, %i));' % (self.schName, srid)
    qry += "select create_st_index_if_not_exists('%s','areas2d');" % (self.schName)

    # create structures table
    qry += 'drop table if exists %s.struct_lines cascade;' % self.schName
    qry += 'create table %s.struct_lines (gid serial primary key, aid integer, cellsizealong double precision, cellsizeacross double precision, meshrows integer, geom geometry(Linestring, %i));' % (self.schName, srid)
    qry += "select create_st_index_if_not_exists('%s','struct_lines');" % (self.schName)

    # create structure routes table
    qry += 'drop table if exists %s.struct_lines_m cascade;' % self.schName
    qry += 'create table %s.struct_lines_m (gid serial primary key, aid integer, cellsizealong double precision, cellsizeacross double precision, meshrows integer, geom geometry(LinestringM, %i));' % (self.schName, srid)
    qry += "select create_st_index_if_not_exists('%s','struct_lines_m');" % (self.schName)

    # create breakpoints table
    qry += 'drop table if exists %s.breakpoints cascade;' % self.schName
    qry += 'create table %s.breakpoints (gid serial primary key, aid integer, sid integer, m double precision, geom geometry(Point, %i));' % (self.schName, srid)

    # 2d mesh points table
    qry += 'drop table if exists %s.mesh_pts cascade;' % self.schName
    qry += 'create table %s.mesh_pts (gid serial primary key, aid integer, lid integer, cellsize double precision, geom geometry(Point, %i));' % (self.schName, srid)
    qry += "select create_st_index_if_not_exists('%s','mesh_pts');" % (self.schName)

    # structures buffers table
    qry += 'drop table if exists %s.wyciecie_pkt_org;' % self.schName
    qry += 'create table if not exists %s.wyciecie_pkt_org (gid serial primary key,geom geometry(Polygon, %i));' % (self.schName, srid)
    qry += "select create_st_index_if_not_exists('%s','wyciecie_pkt_org');" % (self.schName)

    # time.sleep(0.05)
    self.rgis.rdb.run_query(qry)

    qry = '''CREATE OR REPLACE FUNCTION makegrid(geometry, float, integer)
    RETURNS geometry AS
    'SELECT ST_Collect(st_setsrid(ST_POINT(x/1000000::float,y/1000000::float),$3)) FROM
      generate_series(floor(st_xmin($1)*1000000)::bigint, ceiling(st_xmax($1)*1000000)::bigint,($2*1000000)::bigint) as x,
      generate_series(floor(st_ymin($1)*1000000)::bigint, ceiling(st_ymax($1)*1000000)::bigint,($2*1000000)::bigint) as y
    where st_intersects($1,st_setsrid(ST_POINT(x/1000000::float,y/1000000::float),$3))'
    LANGUAGE sql;'''
    self.rgis.rdb.run_query(qry)

    self.rgis.addInfo("  Inserting polygons into 2D areas PostGIS table..." )

    areaFeats = areas.getFeatures()

    qry = 'INSERT INTO %s.areas2d (name, cellsize, geom) VALUES \n' % self.schName

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

    self.rgis.rdb.run_query(qry)

    self.rgis.addInfo("  Creating preliminary regular mesh points..." )

    qry = '''insert into %s.mesh_pts (aid, lid, geom)
    SELECT gid, -1, (ST_Dump(makegrid(geom, cellsize, %i))).geom as geom from %s.areas2d;''' % (self.schName, srid, self.schName)
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
    ''' % ((self.schName,) * 3)
    self.rgis.rdb.run_query(qry)

    self.rgis.addInfo("  Inserting structures into PostGIS table" )

    if structures:
      structFeats = structures.getFeatures()

      qry = 'INSERT INTO %s.struct_lines (cellsizealong, cellsizeacross, meshrows, geom) VALUES \n' % self.schName

      for feat in structFeats:
        if not feat[structMeshSizeAlongAttr] or not feat[structMeshSizeAcrossAttr]:
          self.rgis.addInfo("\n\n<b>Warning: Some structures have no cell size specified. Crash expected...</b>\n\n" )
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
          self.rgis.addInfo("&nbsp;&nbsp;<b>Structure line id=%i has a wrong (empty) geometry!</b>\n" % feat['Id'])
          wrongGeo = True
        qry = qry[:-2] + ")',%i)),\n" % srid

      qry = qry[:-2] + ';'
      if wrongGeo:
        print qry
        self.rgis.addInfo("\n  Check (or replace) structure lines with wrong geometry and try again.\n\n")
        return
      self.rgis.rdb.run_query(qry)

    # insert breakpoints to database

    if breakPoints:
      breakFeats = breakPoints.getFeatures()

      qry = 'INSERT INTO %s.breakpoints (geom) VALUES \n' % self.schName

      for feat in breakFeats:
        geom = feat.geometry()
        pt = geom.asPoint()
        qry += "(ST_GeomFromText('POINT( %.4f %.4f )',%i)),\n" % (pt.x(), pt.y(), srid)

      qry = qry[:-2] + ';'
      self.rgis.rdb.run_query(qry)

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
    ''' % ((self.schName,) * 3)
    self.rgis.rdb.run_query(qry)

    self.rgis.addInfo("  Creating routes along structure lines..." )

    qry = 'insert into %s.struct_lines_m (aid, cellsizealong, cellsizeacross, meshrows, geom) select aid, cellsizealong, cellsizeacross, meshrows, (ST_Dump(ST_AddMeasure(geom, 0, ST_Length(geom)))).geom from %s.struct_lines;' % ((self.schName,) * 2)

    self.rgis.addInfo("  Deleting orignal mesh points near structures..." )
    qry += 'insert into %s.wyciecie_pkt_org (geom) select ST_Buffer(geom, meshrows*cellsizeacross+cellsizealong*0.6, \'endcap=flat join=round\') from %s.struct_lines_m;' % ((self.schName,) * 2)
    qry += 'delete from %s.mesh_pts as p using %s.wyciecie_pkt_org as w where w.geom && p.geom and ST_Intersects(w.geom, p.geom);' % ((self.schName,) * 2)
    self.rgis.rdb.run_query(qry)

    self.rgis.addInfo("  Creating mesh points along structures..." )

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
      ''' % (self.schName, self.schName, breakPtsLocTol, self.schName)
      self.rgis.rdb.run_query(qry)

      # find measures of breakpoints along structure_lines
      # there was a change in the alg name between PostGIS 2.0 and 2.1
      # ST_Line_Locate_Point -> ST_LineLocatePoint
      qry = "select PostGIS_Full_Version() as ver;"
      postgisVersion = self.rgis.rdb.run_query(qry, True)[0]['ver'].split('\"')[1][:5]
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
      ''' % (self.schName, locate, self.schName)
      self.rgis.rdb.run_query(qry)

    self.rgis.addInfo("  Creating aligned mesh points along structures..." )

    qry = "SELECT gid, aid, cellsizealong, cellsizeacross, ST_Length(geom) as len, meshrows as rows from %s.struct_lines_m;" % self.schName

    for line in self.rgis.rdb.run_query(qry, True):
      odl = float(line['cellsizealong'])
      szer = float(line['cellsizeacross'])
      id = line['gid']
      leng = float(line['len'])
      rows = int(line['rows'])
      imax = int(leng/(odl))

      qry = "SELECT DISTINCT b.m from %s.breakpoints b, %s.struct_lines s where b.sid = %i;" % (self.schName, self.schName, id)
      ms = self.rgis.rdb.run_query(qry, True)

      if not ms: # no breakpoints: create aligned mesh at regular interval = cellsize
        self.rgis.addInfo("  Creating aligned mesh points for structure id=%i" % id )
        for i in range(0, imax+1):
          dist = i * odl
          for j in range(0,rows):
            qry = 'insert into %s.mesh_pts (lid, aid, cellsize, geom) select gid, aid, %.2f, ST_Centroid(ST_LocateAlong(geom, %.2f, %.2f)) from %s.struct_lines_m where gid = %i;' % (self.schName, odl, dist, j*szer+szer/2, self.schName, id)
            qry += 'insert into %s.mesh_pts (lid, aid, cellsize, geom) select gid, aid, %.2f, ST_Centroid(ST_LocateAlong(geom, %.2f, -%.2f)) from %s.struct_lines_m where gid = %i;' % (self.schName, odl, dist, j*szer+szer/2, self.schName, id)
            self.rgis.rdb.run_query(qry)

      else: # create cellfaces at structure breakpoints
        self.rgis.addInfo("  Creating breakpoints for structure id=%i " % id )
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
            qry = 'insert into %s.mesh_pts (lid, aid, cellsize, geom) select gid, aid, %.2f, ST_Centroid(ST_LocateAlong(geom, %.2f, %.2f)) from  %s.struct_lines_m where gid = %i;\n' % (self.schName, cs_min, m*leng, j*odl+odl/2, self.schName, id)
            qry += 'insert into %s.mesh_pts (lid, aid, cellsize, geom) select gid, aid, %.2f, ST_Centroid(ST_LocateAlong(geom, %.2f, -%.2f)) from %s.struct_lines_m where gid = %i;' % (self.schName, cs_min, m*leng, j*odl+odl/2, self.schName, id)
            self.rgis.rdb.run_query(qry)


    self.rgis.addInfo("  Deleting mesh points located too close to each other or outside the 2D area..." )

    qry = '''delete from %s.mesh_pts as p1 using %s.mesh_pts as p2
      where p1.lid <> -1 and p2.lid <> -1 and p1.lid <> p2.lid and p1.gid > p2.gid
      and ST_DWithin(p1.geom, p2.geom, 0.75 * least(p1.cellsize, p2.cellsize))
      ;''' % ((self.schName,) * 2)
    qry += '''delete from %s.mesh_pts as p using %s.areas2d as a
      where
        not ST_Contains( ST_Buffer(a.geom,-0.3*a.cellsize), p.geom )
      ;''' % ((self.schName,) * 2)
    self.rgis.rdb.run_query(qry)

    if geoFileName:
      ras2dSaveMeshPtsToGeometry(self.rgis, geoFileName)

    QApplication.setOverrideCursor(Qt.ArrowCursor)
    QDialog.accept(self)




  
  def displayHelp(self):
    self.rgis.showHelp('create2darea.html') 

  def populateLayerCombos(self):
    for layerId, layer in self.rgis.mapRegistry.mapLayers().iteritems():
      if layer.type() == 0 and layer.geometryType() == 0: # vector and points
        self.ui.cboBreakPoints.addItem(layer.name(), layerId)
      if layer.type() == 0 and layer.geometryType() == 1: # vector and polylines
        self.ui.cboStructures.addItem(layer.name(), layerId)
      if layer.type() == 0 and layer.geometryType() == 2: # vector and polygons
        self.ui.cbo2dAreas.addItem(layer.name(), layerId)
      if layer.type() == 1: # it's a raster
        pass
    self.update2dAreaAttrs()
    self.updateStructureAttrs()

  def cbo2dAreasChanged(self):
    curInd = self.ui.cbo2dAreas.currentIndex()
    lid = self.ui.cbo2dAreas.itemData(curInd)
    self.areasLayer = self.rgis.mapRegistry.mapLayer(lid)
    self.update2dAreaAttrs()
  
  def cboStructuresChanged(self):
    curInd = self.ui.cboStructures.currentIndex()
    lid = self.ui.cboStructures.itemData(curInd)
    self.structuresLayer = self.rgis.mapRegistry.mapLayer(lid)
    self.updateStructureAttrs()
    
  def cboBreakPointsChanged(self):
    curInd = self.ui.cboBreakPoints.currentIndex()
    lid = self.ui.cboBreakPoints.itemData(curInd)
    self.breakPointsLayer = self.rgis.mapRegistry.mapLayer(lid)
    
  def update2dAreaAttrs(self):
    if self.areasLayer:
      if self.areasLayer.featureCount():
        self.ui.cbo2dAreasNameAttr.clear()
        self.ui.cbo2dAreasMeshSizeAttr.clear()
        attrs = self.areasLayer.pendingFields()
        self.ui.cbo2dAreasNameAttr.addItem("")
        self.ui.cbo2dAreasMeshSizeAttr.addItem("")
        areaNameIdx = 0
        areaCellSizeIdx = 0
        for i, attr in enumerate(attrs):
          self.ui.cbo2dAreasNameAttr.addItem(attr.name())
          self.ui.cbo2dAreasMeshSizeAttr.addItem(attr.name())
          # check if there is 'name' attr
          if attr.name() == 'name' or attr.name() == 'nazwa':
            areaNameIdx = i + 1
          # check if there is 'cellsize' attr 
          if attr.name() == 'cellsize':
            areaCellSizeIdx = i + 1
        self.ui.cbo2dAreasNameAttr.setCurrentIndex(areaNameIdx)
        self.ui.cbo2dAreasMeshSizeAttr.setCurrentIndex(areaCellSizeIdx)
            
  def updateStructureAttrs(self):
    if self.structuresLayer:
      if self.structuresLayer.featureCount():
        self.ui.cboStructureMeshSizeAlongAttr.clear()
        self.ui.cboStructureMeshSizeAlongAttr.addItem("")
        self.ui.cboStructureMeshSizeAcrossAttr.clear()
        self.ui.cboStructureMeshSizeAcrossAttr.addItem("")
        self.ui.cboStructureMeshRowsAttr.clear()
        self.ui.cboStructureMeshRowsAttr.addItem("")
        attrs = self.structuresLayer.pendingFields()
        structCellSizeAlongIdx = 0
        structCellSizeAcrossIdx = 0
        structMeshRowsIdx = 0
        for i, attr in enumerate(attrs):
          self.ui.cboStructureMeshSizeAlongAttr.addItem(attr.name())
          self.ui.cboStructureMeshSizeAcrossAttr.addItem(attr.name())
          self.ui.cboStructureMeshRowsAttr.addItem(attr.name())
          # check if there is 'cellsize' attr 
          if attr.name() == 'cellsizesx' or attr.name() == 'cellsizeal':
            structCellSizeAlongIdx = i + 1
          elif attr.name() == 'cellsizesy' or attr.name() == 'cellsizeac':
            structCellSizeAcrossIdx = i + 1
          # check if there is 'meshrows' attr 
          elif attr.name() == 'meshrows':
            structMeshRowsIdx = i + 1
        self.ui.cboStructureMeshSizeAlongAttr.setCurrentIndex(structCellSizeAlongIdx)
        self.ui.cboStructureMeshSizeAcrossAttr.setCurrentIndex(structCellSizeAcrossIdx)
        self.ui.cboStructureMeshRowsAttr.setCurrentIndex(structMeshRowsIdx)


