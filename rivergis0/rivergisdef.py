# -*- coding: utf-8 -*-

from pyspatialite import dbapi2
import unicodedata
from os.path import isfile, join
from os import remove
from shutil import copyfile
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *
from rdp import *
from PyQt4.Qwt5 import *
from math import pow
try:
  from logging_rivergis import *
except:
  print "Can't load logging module"

try:
  import MySQLdb
except:
  pass
#   info = "No MySQLdb Python module found. \nYou won't be able to import data from MySQL database."
#   QMessageBox.warning(None, "Python module info", info)

  
def mikeName(text):
  """Removes diacritics from the string, replaceses spaces with underscore"""
  a = text.decode('utf-8').replace(u'\u0141', "L").replace(u'\u0142', "l")
  b = a.replace(" ", "_")
  textAscii = unicodedata.normalize("NFKD", b).encode('ascii', 'ignore')
  return textAscii 



class RiverDb:
  def __init__(self, filename, srid=2180):
    self.filename = filename
    self.rivIds = []
    if isfile(filename):
      logging.debug("\n\nFile `%s` exists. Opening and reading srid...." % (filename))
      self.conn = dbapi2.connect(self.filename)
      cur = self.conn.cursor()
      sql = "SELECT srid FROM db_srid;" 
      logging.debug(sql)
      cur.execute(sql)
      self.srid = cur.fetchone()[0]
      del cur
    else:
      logging.debug("\n\nCreating new database `%s` with srid %i...." % (filename, srid))
      self.createEmptyDb(filename, srid)
      self.conn = dbapi2.connect(self.filename)
    self.getRivers()
    
    
  def getRivers(self):
    cur = self.conn.cursor()
    qry = "SELECT * FROM rivers ORDER BY name"
    cur.execute(qry)
    self.rivIds = []
    rivs = []
    for riv in cur.fetchall():
      self.rivIds.append(riv[0])
      rivs.append(riv)
    del cur
    return rivs


  def createEmptyDb(self, filename, srid):
    # tables' names
    xsecTable = "xsecs"
    ptsTable = "points"
    filteredPtsTable = "filtered_points"
    riversTable = "rivers"
    modelsTable = "models"
    modelPartsTable = "model_parts"
    conn = dbapi2.connect(self.filename)
    cur = conn.cursor()
    try:
      sql = 'SELECT InitSpatialMetadata(1)'
      cur.execute(sql)
      logging.debug("%s\n\nSpatial metadata OK." % sql)
    except:
      logging.debug("InitSpatialMetadata() failed.", "Rivergis", QgsMessageLog.ERROR)
      
    # create srid table     
    sql = """CREATE TABLE db_srid (
    srid INTEGER NOT NULL PRIMARY KEY);"""
    logging.debug("\n" + sql)
    cur.execute(sql)
    conn.commit()
    sql = "INSERT INTO db_srid (srid) VALUES (%i);" % srid
    logging.debug(sql)
    cur.execute(sql)
    conn.commit()
    
    # create xsections table     
    sql = """CREATE TABLE %s (
    xs_id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    riv_id INTEGER,
    chainage INTEGER,
    desc TEXT);""" % (xsecTable)
    logging.debug("\n" + sql)
    cur.execute(sql)
    conn.commit()
    sql = """SELECT AddGeometryColumn(\'%s\', \'the_geom\', %i, 'LINESTRING', 'XY')""" % (xsecTable, srid)
    logging.debug(sql)
    cur.execute(sql)
    conn.commit()

    # create points table
    sql = """CREATE TABLE %s (
    pt_id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    xs_id INTEGER,
    x DOUBLE,
    y DOUBLE,
    abscissa DOUBLE,
    ordinate DOUBLE,
    cover TEXT,
    n DOUBLE,
    marker INTEGER,
    is_node INTEGER,
    filtered DOUBLE,
    desc text);""" % (ptsTable)
    logging.debug("\n" + sql)
    cur.execute(sql)
    conn.commit()
    sql = """SELECT AddGeometryColumn(\'%s\', \'the_geom\', %i, 'POINT', 'XY')""" % (ptsTable, srid)
    logging.debug(sql)
    cur.execute(sql)
    conn.commit()
    
    # create rivers table     
    sql = """CREATE TABLE %s (
    riv_id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    topo_id INTEGER,
    reach TEXT,
    name TEXT,
    short_name TEXT,
    ch_upstr INTEGER,
    ch_downstr INTEGER,
    desc TEXT);""" % (riversTable)
    logging.debug("\n" + sql)
    cur.execute(sql)
    conn.commit()
    sql = """SELECT AddGeometryColumn(\'%s\', \'the_geom\', %i, 'LINESTRING', 'XY')""" % (riversTable, srid)
    logging.debug(sql)
    cur.execute(sql)
    conn.commit()

    # create models table     
    sql = """CREATE TABLE %s (
    model_id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    model_name TEXT,
    desc TEXT);""" % (modelsTable)
    logging.debug("\n" + sql)
    cur.execute(sql)
    conn.commit()
    
    # create land covers table
    sql = """CREATE TABLE land_covers (
    cover_id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    cover_code TEXT,
    n DOUBLE,
    desc TEXT);"""
    logging.debug("\n" + sql)
    cur.execute(sql)
    conn.commit()
    
    # create table of default n values for land covers 
    sql = """CREATE TABLE n_defaults (
    cover_code TEXT NOT NULL PRIMARY KEY,
    n DOUBLE NOT NULL,
    desc TEXT);"""
    logging.debug("\n" + sql)
    cur.execute(sql)
    conn.commit()
      
  def importAllFromMySQL(self,dbM):
        
    dbS = self.conn
    curS = dbS.cursor()

    # wczytaj dane rzek z bazy mySQL
    curM = dbM.cursor()
    qry = "SELECT * FROM river_data"
    curM.execute(qry)
    riverIds = []
    for riv in curM.fetchall():
      riverIds.append(riv[0])
    del curM
    
    for riverId in riverIds:
      river = mySQL.River(dbM,"", riverId)
      print "Working on river %s (riv_id = %i)" % (river.name, river.rivId)
      curS = dbS.cursor()
      sql = river.getInsertSQLite()
      logging.debug(sql)
      curS.execute(sql)
      river.getXsecs()
      
      for xsId in river.xsIds:
        
        xs = mySQL.Xsection(dbM,"", "",xsId)
        # print "Robie przekroj: %i, %s" % (xs.xsId, xs.chainage)
        curS = dbS.cursor()
        sql = xs.getInsertSQLite()
        logging.debug(sql)
        curS.execute(sql)
        
        xs.getPtIds()
        
        for ptId in xs.ptIds:
        
          pt = mySQL.XsPoint(dbM,"", ptId)
          curS = dbS.cursor()
          sql = pt.getInsertSQLite()
          logging.debug(sql)
          curS.execute(sql)
        
        dbS.commit()
  
  def exportRiversSQLite(self, filename, srid, rivIdList):
    """
    Exports rivers with ids in rivIdList to a new SQLite DB along 
    with its xsections and their points 
    """
    if isfile(filename):
      remove(filename)
    emptyDbFilename = join(dirname(__file__), "db/emptyDb.sqlite") 
    QMessageBox.information(None, "", str(emptyDbFilename))
    copyfile(emptyDbFilename, filename)
    newDb = RiverDb(filename, srid)
    for rivId in rivIdList:
      srcRiver = River(self, "", rivId)
      srcRiver.getXsecs()
      newRiver = srcRiver
      newRiver.conn = newDb.conn
      newRiver.insert2Db()
      for xsId in srcRiver.xsIds:
        xs = Xsection(self, "", "", xsId)
        xs.rivId = newRiver.rivId
        cur = newRiver.conn.cursor()
        sql = xs.getExportSQL()
        logging.debug(sql)
        cur.execute(sql)
        newXsId = cur.lastrowid
        self.conn.commit()
        logging.debug("New xs_id for xs %i is : %i" % (xs.xsId, newXsId))
        xs.getPtIds()
        #logging.debug("ptIds to export: %s" % xs.ptIds)
        for ptId in xs.ptIds:
          pt = XsPoint(self,"", ptId)
          pt.xsId = newXsId
          sql = pt.getExportSQL()
          #logging.debug("\n" + sql)
          cur.execute(sql)
        newRiver.conn.commit()

  
  def updateXsGeometriesForRiver(self, rivId):
    river = River(self.conn,"",riverId)
    logging.debug("Updating xsections geometry for river: %i, %s" % (river.rivId, river.name))
    river.getXsecs()
    
    for xsId in river.xsIds:
      xs = Xsection(self.conn,"", "",xsId)   
      xs.updateXsGeometry()
        
        
  def updateAllXsGeometries(self):
    for rivId in self.rivIds:
      self.updateXsGeometriesForRiver(rivId)
      
  def unSimplify(self, xsIds): 
    cur = self.conn.cursor()
    pts2Revert = []
    for xsId in xsIds:
      pts2Revert.append(str(xsId))
    sep = ", "
    pts2RevertIds = sep.join(pts2Revert)
    script = "UPDATE points SET filtered=0 where xs_id IN (%s);\n" % pts2RevertIds
    #logging.debug(script)
    cur.executescript(script)
    self.conn.commit()
  
  def delSimplified(self, xsIds): 
    cur = self.conn.cursor()
    xsIdList = []
    for xsId in xsIds:
      xsIdList.append(str(xsId))
    sep = ", "
    xsIdListStr = sep.join(xsIdList)
    qry = "DELETE FROM points WHERE xs_id IN (%s) and not filtered = 0;\n" % xsIdListStr
    logging.debug(qry)
    cur.execute(qry)
    self.conn.commit()

      


class XsPoint:
  def __init__(self, rdb, xsId, ptId=None):
    
    self.conn = rdb.conn
    self.conn.row_factory = dbapi2.Row
    self.srid = rdb.srid
    
    if not ptId == None:
      qry = "SELECT * FROM points where pt_id=%i" % ptId
      cur = self.conn.cursor()
      cur.execute(qry)
      dbData = cur.fetchone()
      self.ptId = dbData['pt_id']
      self.xsId = dbData['xs_id']
      self.x = dbData['x']
      self.y = dbData['y']
      self.absc = dbData['abscissa']
      self.ordin = dbData['ordinate']
      self.code = dbData['cover']
      self.rough = dbData['n']
      self.marker = dbData['marker']
      self.desc = dbData['desc']
      self.isNode = dbData['is_node']
      self.filtered = dbData['filtered']
      del cur
    else:
      self.xsId = xsId
      self.ptId = 0
      self.x = 0
      self.y = 0
      self.absc = 0
      self.ordin = 0
      self.code = 0
      self.rough = 0
      self.marker = 0
      self.desc = ""
      self.isNode = 0
      self.geomWKT = ""
      self.filtered = 0
      
  def getInsertSQL(self):
    qry = """INSERT INTO `points` (`pt_id`, `xs_id`, `x`, `y`,
    `abscissa`, `ordinate`, `cover`, `n`, `marker`, 
    `desc`,`the_geom`, `is_node`, `filtered`) VALUES (%i, %i, %.3f, %.3f, %.3f, %.3f, '%s', %.3f, %i, %s, ST_GeomFromText('POINT(%.3f %.3f)', %i), %i, %.3f);""" % \
    (self.ptId, self.xsId, self.x, self.y, self.absc, \
    self.ordin, self.code, self.rough, self.marker, self.desc, \
    self.x, self.y, self.srid, self.isNode, self.filtered)
    return qry
    
  def getUpdateSQL(self):
    qry = """INSERT OR REPLACE INTO `points` (`pt_id`, `xs_id`, `x`, `y`,
    `abscissa`, `ordinate`, `cover`, `n`, `marker`,
    `desc`,`the_geom`, `is_node`, `filtered`) VALUES (%i, %i, %.3f, %.3f, %.3f, %.3f, '%s', %.3f, %i, %s, ST_GeomFromText('POINT(%.3f %.3f)', %i), %i, %.3f);""" % \
    (self.ptId, self.xsId, self.x, self.y, self.absc, \
    self.ordin, self.code, self.rough, self.marker, self.desc, \
    self.x, self.y, self.srid, self.isNode, self.filtered)
    return qry
  
  def getExportSQL(self):
    qry = """INSERT OR REPLACE INTO `points` (`xs_id`, `x`, `y`,
    `abscissa`, `ordinate`, `cover`, `n`, `marker`, 
    `desc`,`the_geom`, `is_node`, `filtered`) VALUES (%i, %.3f, %.3f, %.3f, %.3f, '%s', %.3f, %i, '%s', ST_GeomFromText('POINT(%.3f %.3f)', %i), %i, %.3f);""" % \
    (self.xsId, self.x, self.y, self.absc, \
    self.ordin, self.code, self.rough, self.marker, self.desc, \
    self.x, self.y, self.srid, self.isNode, self.filtered)
    return qry
  
  def readFromDb(self):
    cur = self.conn.cursor()
    qry = "SELECT * FROM points where pt_id=%i" % self.ptId
    cur.execute(qry)
    res = cur.fetchone()
    if res == None:
       info = "There is no point with pt_id=%i in the db." % self.ptId       
       logging.debug(info)
    del cur
    return res
    
  def insert2Db(self):
    res = self.readFromDb()
    if not res == None:
      info = "There is a point with pt_id=%i in the db." % self.ptId
      info += "You cannot insert it - just update it."
    else:
      cur = self.conn.cursor()
      info = "SQL string for point inserting:\n%s" % self.getInsertSQL()
      logging.debug(info)
      cur.execute(self.getInsertSQL())
      self.conn.commit()
      self.ptId = cur.lastrowid
  
  def updateDb(self):
    res = self.readFromDb()
    if not res == None:
      cur = self.conn.cursor()
      info = "SQL string for point updating:\n%s" % self.getUpdateSQL()
      logging.debug(info)
      cur.execute(self.getUpdateSQL())
      self.conn.commit()
    else:
      info = "There is no point with pt_id=%i in the db." % self.ptId
      info += "You cannot update it - insert it first."
      logging.debug(info)
  
  def updatePtGeometry(self):
    cur = self.conn.cursor()
    geom = "ST_GeomFromText(\'Point("
    geom += "%f " % self.x
    geom += "%f " % self.y
    geom += ")\', 2180)"
    self.geomWKT = geom
    #logging.debug(self.getUpdateSQL())
    cur.execute(self.getUpdateSQL())
    self.conn.commit()




class Xsection:
  def __init__(self, rdb, rivId, chainage, xsId=None):
    
    self.rdb = rdb
    self.conn = rdb.conn
    self.srid = rdb.srid
    self.conn.row_factory = dbapi2.Row
    cur = self.conn.cursor()
    if not xsId == None:
      qry = "SELECT xs_id, riv_id, chainage, desc, AsText(the_geom) as the_geom FROM xsecs where xs_id=%i" % xsId
      cur.execute(qry)
      data = cur.fetchone()
      self.xsId = data['xs_id']
      self.rivId = data['riv_id']
      self.chainage = data['chainage']
      self.desc = data['desc']
      self.getPtIds()
      self.pts = []
      self.nodeIds = [] # pt_ids of points with crucial information (markers or land cover change...)
      qry = "SELECT name FROM rivers where riv_id=%i" % data[1]
      cur.execute(qry)
      self.riverName = cur.fetchone()[0]
      self.name = "%s_%i" % (self.riverName, self.chainage)

    else:
      self.xsId = 0
      self.rivId = rivId
      self.chainage = chainage
      self.desc = ""
      self.geom = ""
      self.geomWKT = ""
      self.ptIds = []
      self.pts = []
      self.nodeIds = []
      
  def getRiver(self):
    return River(self.rdb, "", self.rivId)
  
  def getPtIds(self):
    self.ptIds = []
    cur = self.conn.cursor()
    qry = "SELECT * FROM points where (xs_id=%i and filtered=0) ORDER BY abscissa" % (self.xsId)
    cur.execute(qry)
    for pt in cur.fetchall():
      self.ptIds.append(pt[0])
      
  def fetchPointsFromDb(self):
    self.pts = []
    cur = self.conn.cursor()
    qry = "SELECT * FROM points where (xs_id=%i and filtered=0) ORDER BY abscissa" % self.xsId
    logging.debug("fetchPointsFromDb query=\n%s" % qry)
    cur.execute(qry)
    for p in cur.fetchall():
      self.pts.append(XsPoint(self.rdb, "", p[0]))
    logging.debug("Fetched %i points for xsId=%i" % (len(self.ptIds), self.xsId))
  
  def fetchFiltered(self):
    self.filtered = []
    cur = self.conn.cursor()
    qry = "SELECT * FROM points where (xs_id=%i and not filtered=0) ORDER BY abscissa" % self.xsId
    logging.debug("fetchFiltered query=\n%s" % qry)
    cur.execute(qry)
    x, y = [[], []]
    for p in cur.fetchall():
      x.append(p[4])
      y.append(p[5])
    self.filtered = (x, y)
    logging.debug("Fetched %i filtered points for xsId=%i" % (len(self.filtered[0]), self.xsId))
    
  
  def findNodes(self):
    self.nodeIds = []
    nodesStr=[]
    cur = self.conn.cursor()
    logging.debug("Finding nodes for xsId=%i" % (self.xsId))
    if self.pts == []:
      self.fetchPointsFromDb()
    self.pts[0].isNode = 1 # add the first point
    self.nodeIds = [self.pts[0].ptId]
    for pt in self.pts[1:]:
      if not pt.marker == 0 or not pt.code == code:
        pt.isNode = 1
        code = pt.code
        self.nodeIds.append(pt.ptId)
        nodesStr.append(str(pt.ptId))
      else:
        pt.isNode = 0
    sep = ", "
    nodes = sep.join(nodesStr)  
    script = "UPDATE points SET is_node = 0 \
        WHERE xs_id =%i;\n" % self.xsId
    script += "UPDATE points SET is_node = 1 \
        WHERE pt_id in (%s);\n" % nodes
    info = "SQL string for resetting nodes:\n%s" % script
    logging.debug(info)
    cur.executescript(script)
    self.conn.commit()


  def fetchNodesFromDb(self):
    self.nodeIds = []
    cur = self.conn.cursor()
    qry = "SELECT pt_id FROM points where xs_id=%i and is_node" % self.xsId
    cur.execute(qry)
    for p in cur.fetchall():
      self.nodeIds.append(p[0])
  
  
  def fetchMarkersFromDb(self):
    self.markers = {}
    cur = self.conn.cursor()
    qry = "SELECT * FROM points where xs_id=%i and not marker = 0" % self.xsId
    cur.execute(qry)
    self.markers = {}
    for p in cur.fetchall():
      if p[8] == 1:
        self.markers[1] = p[4]
      elif p[8] == 2:
        self.markers[2] = p[4]
      elif p[8] == 3:
        self.markers[3] = p[4]
      elif p[8] == 4:
        self.markers[4] = p[4]
      elif p[8] == 5:
        self.markers[5] = p[4]
      else:
        pass
  
  def moveMarker(self, marker, newPtId):
    cur = self.conn.cursor()
    script = "UPDATE points SET marker=0 WHERE pt_id=(SELECT pt_id FROM points where xs_id=%i and marker=%i);\n" % (self.xsId, marker)
    script += "UPDATE points SET marker=%i WHERE pt_id=%i;" % (marker, newPtId)
    cur.executescript(script)
    self.conn.commit()
    logging.debug(script)
    qry = "SELECT abscissa FROM points WHERE pt_id=%i;" % (newPtId)
    cur.execute(qry)
    self.markers[marker] = cur.fetchone()[0]
    
  def fetchAbscOrdinFromDb(self):
    self.abscissas = []
    self.ordinates = []
    self.covers = []
    cur = self.conn.cursor()
    qry = "SELECT abscissa, ordinate, cover FROM points where (xs_id=%i and filtered=0) ORDER BY abscissa" % self.xsId
    cur.execute(qry)
    for p in cur.fetchall():
      self.abscissas.append(p[0])
      self.ordinates.append(p[1])
      self.covers.append(p[2])
      
  def updateXsGeometry(self):
    cur = self.conn.cursor()
    self.fetchPointsFromDb()
    geomWKT = "ST_GeomFromText(\'LINESTRING("
    for pt in self.pts:
      geomWKT += "%f " % pt.x
      geomWKT += "%f, " % pt.y
    geomWKT = geomWKT[:-2] + ")\', %i)" % self.srid
    self.geomWKT = geomWKT
    logging.debug(self.getUpdateSQL())
    cur.execute(self.getUpdateSQL())
    self.conn.commit()
  
  def getInsertSQL(self):
    qry = """INSERT OR IGNORE INTO 'xsecs' ('riv_id', 
    'chainage', 'desc', `the_geom`) VALUES (
    %i, %i, \'%s\', ST_GeomFromText('%s', %i));""" % \
    (self.rivId, self.chainage, \
    self.desc, self.geomWKT, self.srid)
    logging.debug("Insert XS qry:\n%s" % qry)
    return qry
    
  def getUpdateSQL(self):
    qry = """INSERT OR REPLACE INTO 'xsecs' ('xs_id', 'riv_id', 
    'chainage', 'desc', 'the_geom') VALUES (
    %i, %i, %i, \'%s\', ST_GeomFromText('%s', %i));""" % \
    (self.xsId, self.rivId, self.chainage, \
    self.desc, self.geomWKT, self.srid)
    logging.debug(qry)
    return qry
  
  def getExportSQL(self):
    qry = """select ST_AsText(the_geom) from xsecs where xs_id=%i""" \
          % self.xsId
    cur = self.conn.cursor()
    cur.execute(qry)
    geom = cur.fetchone()[0]
    
    qry = """INSERT OR REPLACE INTO 'xsecs' ('riv_id', 
    'chainage', 'desc', 'the_geom') VALUES (
    %i, %i, \'%s\', ST_GeomFromText('%s', %i));""" % \
    (self.rivId, self.chainage, \
    self.desc, geom, self.srid)
    logging.debug(qry)
    return qry
  
  def readFromDb(self):
    cur = self.conn.cursor()
    qry = "SELECT * FROM xsecs where xs_id=%i" % self.xsId
    cur.execute(qry)
    res = cur.fetchone()
    if res == None:
      info = "There is no cross-setion with xs_id=%i in the db." % self.xsId
      logging.debug(info)
    return res
    
  def insert2Db(self):
    res = self.readFromDb()
    if not res == None:
      print "There is a cross-section with xs_id=%i in the db. \
        Check your data" % res[0]
    else:
      info = "SQL string for inserting cross-section:\n%s" % self.getInsertSQL()
      logging.debug(info)
      cur = self.conn.cursor()
      cur.execute(self.getInsertSQL())
      self.conn.commit()
      self.xsId = cur.lastrowid
        
  def updateDb(self):
    res = self.readFromDb()
    if not res == None:
      info = "SQL string for river data updating :\n%s" % self.getInsertSQL()
      logging.debug(info)
      cur.execute(self.getUpdateSQL())
      self.conn.commit()
    else:
      info = "There is no river with River_IDX=%i in the db." % (self.rivId)
      info += "You cannot update it - please, insert it instead." 
      logging.debug(info)
  
  def deleteFromDb(self, xsId):
    cur = self.conn.cursor()
    qry = "DELETE FROM points where xs_id=%i;" % xsId
    qry += "DELETE FROM xsecs WHERE xs_id=%i;" % xsId
    cur.execute(qry)
    self.conn.commit()
    del cur

  def changeChainage(self, newChain):
    cur = self.conn.cursor()
    qry = "UPDATE xsecs SET chainage = %i WHERE xs_id = %i;" % (newChain, xsId)
    cur.execute(qry)
    self.conn.commit()
    del cur
     
  def simplify(self, dist):
    if self.nodeIds == []:
      self.fetchNodesFromDb()
    self.fetchPointsFromDb()
    cur = self.conn.cursor()
    ptsRemainingIds = []
    line = []
    for pt in self.pts:
      line.append((pt.absc, pt.ordin, pt.ptId))
    logging.debug("Filtering xsId=%i, points before: %i" % (self.xsId, len(line)))
    ptsRemaining = ramerdouglas(line, dist)
    logging.debug("points after: %i" % (len(ptsRemaining)))
    for pt in ptsRemaining:
      ptsRemainingIds.append(pt[2])
    logging.debug("Filtered xsId=%i,  %i/%i (new/old)" % (self.xsId, len(ptsRemainingIds), len(self.pts)))
    pts2Filter = []
    for ptId in self.ptIds:
      #logging.debug("Checking ptId = %i " % ptId)
      if not ptId in self.nodeIds:
        if not ptId in ptsRemainingIds:
          pts2Filter.append(str(ptId))
    sep = ", "
    pts2FilterStr = sep.join(pts2Filter)
    script = "UPDATE points SET filtered = %.3f \
              WHERE pt_id IN (%s);\n" % (dist, pts2FilterStr)
    #logging.debug(script)
    cur.executescript(script)
    self.conn.commit()

    
#   def updateXsProfile(self, dist,  dem=None, cover=None):
#     cur = self.conn.cursor()
#     qry = "SELECT AsText(ST_Line_Interpolate_Equidistant_Points((select the_geom from xsecs where xs_id=%i), %.3f))" % (self.xsId, dist)
#     cur.execute(qry)
#     res = cur.fetchone()[0]
#     ptsStrList = res[13:-1].split(",")
#     newPtsScript = ""
#     for pt in ptsStrList:
#       floats = [float(x) for x in pt.strip().split(" ")]
#       x, y, absc = floats
#       if not dem == None:
#         ident = dem.dataProvider().identify(QgsPoint(x, y), QgsRaster.IdentifyFormatValue)
#         if ident.isValid():
#           ordin = float(ident.results()[1])
#       else:
#         ordin = -9999
#       if not cover == None:
#         polys = cover.getFeatures()
#         index = QgsSpatialIndex()
#         for f in polys:
#           index.insertFeature(f)
#         polyId = index.nearestNeighbor(QgsPoint(x, y), 1)[0]
#         # TODO: atrybut land_cover ustawiony na sztywno - znajdz sposob jego okreslania za pomoca GUI
#         coverCode = cover.getFeatures(QgsFeatureRequest().setFilterFid(polyId)).next()['land_cover']
#       else:
#         coverCode = -9999
#       # SQL for inserting new point into db
#       qry = "INSERT INTO `points` (`xs_id`, `x`, `y`, `abscissa`, `ordinate`, `cover`, `the_geom`, `filtered`) VALUES (%i, %.3f, %.3f, %.3f, %.3f, %i, ST_GeomFromText('POINT(%.3f %.3f)', %i), 0);\n" % \
#         (self.xsId, x, y, absc, ordin, coverCode, x, y, self.srid)
#       newPtsScript += qry
#     
#     # insert points to the points table
#     cur.executescript(newPtsScript)
#     self.conn.commit()   
    


class River:
  def __init__(self, rdb, name, rivId=None):
    self.rdb = rdb
    self.conn = rdb.conn
    self.conn.row_factory = dbapi2.Row
    if not rivId == None:
      qry = "SELECT * FROM rivers where riv_id=%i" % rivId
      cur = self.conn.cursor()
      cur.execute(qry)
      dbData = cur.fetchone()
      self.rivId = dbData['riv_id']
      self.topoId = dbData['topo_id']
      self.name = dbData['name']
      self.shortName = dbData['short_name']
      self.reach = dbData['reach']
      self.desc = dbData['desc']
      self.chUpstream = dbData['ch_upstr']
      self.chDownstream = dbData['ch_downstr']
      self.geomWKT = self.getGeomWKT()
      self.srid = rdb.srid
      del cur
      self.getXsecs()
    else:
      self.rivId = 0
      self.topoId = 0
      self.name = name
      self.shortName = ""
      self.reach = ""
      self.desc = ""
      self.chUpstream = 0
      self.chDownstream = 1
      self.geom = "''"
      self.srid = self.rdb.srid
      self.xsIds = []
      
  
  def getInsertSQL(self):
    if self.topoId == 0:
      txt = "River %s has no topo_id, a first available value will be assumed" % self.name
      logging.debug(txt)
      cur = self.conn.cursor()
      qry = "SELECT max(topo_id) FROM rivers"
      cur.execute(qry)
      try:
        self.topoId = cur.fetchone()[0] + 1
      except TypeError:
        self.topoId = 1
    if self.shortName == "":
      self.shortName = mikeName(self.name)

    if self.geomWKT == '':
      qry = """select ST_AsText(the_geom) from rivers where riv_id=%i""" \
            % self.rivId
      cur = self.conn.cursor()
      cur.execute(qry)
      try:
        self.geomWKT = cur.fetchone()[0]
      except TypeError:
        geomWKT = ""
    logging.debug("River geometry WKT: %s" % self.geomWKT)
       
    qry = """INSERT OR REPLACE INTO rivers (topo_id, name, 
    short_name, reach, desc, ch_upstr, ch_downstr, the_geom) VALUES (
    %i, \'%s\', \'%s\', \'%s\', \'%s\', %i, %i, ST_GeomFromText('%s', 2180));""" % \
    (self.topoId, self.name.decode('utf-8'), self.shortName, \
    self.reach, self.desc, self.chUpstream, self.chDownstream, self.geomWKT)
    logging.debug(qry)
    return qry
    
  def getUpdateSQL(self):
    qry = """REPLACE INTO 'rivers' ('riv_id', 'topo_id', 'name', 
    short_name, reach, desc, , ch_downstr, ch_upstr, the_geom) VALUES (
    %i, '%i', '%s', '%s', '%s', '%s', %i, %i, ST_GeomFromText('%s', %i));""" % \
    (self.rivId, self.topoId, self.name.decode('utf-8'), self.shortName, self.reach,\
      self.desc, self.chDownstream, self.chUpstream, self.geomWKT, self.srid)
    return qry
    
  def getExportSQL(self):
    qry = """select ST_AsText(the_geom) from rivers where riv_id=%i""" \
          % self.rivId
    cur = self.conn.cursor()
    cur.execute(qry)
    geom = cur.fetchone()[0]
    #logging.debug("River geometry WKT: %s" % geom)
    
    qry = """INSERT OR REPLACE INTO rivers (topo_id, name, 
    short_name, reach, desc, ch_downstr, ch_upstr, the_geom) VALUES (
    %i, \'%s\', \'%s\', \'%s\', \'%s\', %i, %i, ST_GeomFromText('%s', %i));""" % \
    (self.topoId, self.name.decode('utf-8'), self.shortName, \
    self.reach.decode('utf-8'), self.desc, self.chDownstream, self.chUpstream, geom, self.srid)
    logging.debug(qry)
    return qry
  
  def getGeomWKT(self):
    qry = """select ST_AsText(the_geom) from rivers where riv_id=%i""" \
          % self.rivId
    cur = self.conn.cursor()
    cur.execute(qry)
    self.geomWKT = cur.fetchone()[0]
    
  def readFromDb(self):
    cur = self.conn.cursor()
    qry = "SELECT * FROM rivers where riv_id=%i" % self.rivId
    cur.execute(qry)
    res = cur.fetchone()
    if res == None:
      info = "There is no river with riv_id=%i in the db." % self.rivId
      logging.debug(info)
    del cur
    return res
  
  def insert2Db(self):
    res = self.readFromDb()
    if not res == None:
      info = "There is a river %s with riv_id=%i in the db." % (res[1], self.rivId)
      info += "You cannot update it - just insert it."
    else:
      cur = self.conn.cursor()
      info = "SQL string for river inserting:\n%s" % self.getInsertSQL()
      logging.debug(info)
      cur.execute(self.getInsertSQL())
      self.conn.commit()
      self.rivId = cur.lastrowid

  def updateDb(self):
    res = self.readFromDb()
    if not res == None:
      info = "SQL string for river data updating :\n%s" % self.getInsertSQL()
      logging.debug(info)
      cur = self.conn.cursor()
      cur.execute(self.getUpdateSQL())
      self.conn.commit()
    else:
      info = "There is no river with riv_id=%i in the db." % (self.rivId)
      info += "You cannot update it - please, insert it instead." 
      logging.debug(info)
  
  def getXsecs(self):
    """gets a list of cross-section ids and complete xs models for the river"""
    self.xsIds = []
    self.xss = []
    cur = self.conn.cursor()
    qry = "SELECT * FROM xsecs where riv_id=%i  ORDER BY chainage" % (self.rivId)
    cur.execute(qry)
    for xs in cur.fetchall():
      self.xsIds.append(xs[0])
      self.xss.append(xs)
            


class ChildModel:
  
  def __init__(self, data):
      
    self.modId = data[0]
    self.parentModId = data[1]
    self.modelName = data[2]
    self.parentUser = data[3]
    self.parentDate = data[4]
    self.chainageStart = data[5]
    self.chainageEnd = data[6]
    self.rivId = data[7]
    
    
    
class Model:
  def __init__(self, conn, modelName, modId=None):
      
    self.conn = conn
    cur = self.conn.cursor()
    
    if not modId == None:
      qry = "SELECT * FROM model_data where (Model_ID=%i AND Parent_model_ID=0)" % modId
      cur.execute(qry)
      data = cur.fetchone()
      self.modId = data[0]
      self.parentModId = data[1]
      self.modelName = data[2]
      self.parentUser = data[3]
      self.parentDate = data[4]
      self.chainageStart = data[5]
      self.chainageEnd = data[6]
      self.rivId = data[7]
      
    else:
      self.modId = 0
      self.parentModId = None
      self.modelName = modelName
      self.parentUser = "aaa"
      self.parentDate = 0
      self.chainageStart = 0
      self.chainageEnd = 0
      self.rivId = 0
    
    self.childModels = []
    self.fetchChildModels()
      

  def fetchChildModels(self):
    cur = self.conn.cursor()
    qry = "SELECT * FROM model_data where Parent_model_ID=%i" % self.modId
    cur.execute(qry)
    for m in cur.fetchall():
      self.childModels.append(ChildModel(m))
    

  def copyXsec(self, srcXsId, targetRivId, targetChainage=None):
    cur = self.conn.cursor()
    qry = "CREATE TEMPORARY TABLE tmpCross SELECT * FROM cross_data where Cross_ID=%i;" % srcXsId
    qry += "CREATE TEMPORARY TABLE tmpPoints SELECT * FROM points where Cross_ID=%i;" % srcXsId
    qry += "UPDATE tmpCross SET River_IDX = %i;" % targetRivId
    qry += "ALTER TABLE tmpCross drop Cross_ID;"
    qry += "INSERT INTO cross_data SELECT 0,tmpCross.* FROM tmpCross;"
    qry += "DROP TABLE tmpCross;"
    qry += "ALTER TABLE tmpPoints drop Point_ID;"
    qry += "UPDATE tmpPoints SET Cross_ID = (SELECT max(Cross_ID) FROM cross_data);"
    qry += "INSERT INTO points SELECT 0,tmpPoints.* FROM tmpPoints;"
    qry += "DROP TABLE tmpPoints;"
    cur.execute(qry)
    self.conn.commit()
    # get 
    del cur







#####    MAIN

if __name__ == "__main__":

  
  db = MySQLdb.connect(host="localhost", 
                     user="", 
                      passwd="",
                      db="cross_section_db", 
                      charset='utf8',
                      use_unicode=True) 
  db.set_character_set('utf8')
                      
  cur = db.cursor()
  qry = "SELECT * FROM model_data where Parent_model_ID=0"
  cur.execute(qry)
  data = cur.fetchall()
  for row in data:
    print row[0], row[2], row[7]
  
  del cur
  
  
  
  print "\n\nA teraz podrzedne z modelu %i:\n" % 56
  modelA = Model(db,"bbb" ,56)
  for ch in modelA.childModels:
    print ch.rivId, ch.modelName, ch.chainageStart, ch.chainageEnd
    
  #kopiowanie przekroju
  #modelA.copyXsec(1480,254)
  #modelA.delXsec(3466)
  #modelA.changeXsecChainage(649,795)
  
