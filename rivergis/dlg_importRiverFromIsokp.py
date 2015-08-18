# -*- coding: utf-8 -*-

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *
from qgis.gui import *
from qgis.utils import *

from ui_importRiverFromIsokp import *
import psycopg2
import psycopg2.extras
from miscFunctions import *


class DlgImportRiverFromIsokp(QDialog):
  def __init__(self, rgis):
    QDialog.__init__(self)
    self.ui = Ui_DlgImportRiverFromIsokp()
    self.ui.setupUi(self)
    self.mydb = None
    self.rgis = rgis

    QObject.connect(self.ui.buttonBox, SIGNAL("accepted()"), self.accept)
    QObject.connect(self.ui.buttonBox, SIGNAL("rejected()"), self.reject)
    QObject.connect(self.ui.helpButton, SIGNAL("clicked()"), self.displayHelp)

    QObject.connect(self.ui.btnConnect,SIGNAL("clicked()"),self.reconnectIsokp)
    QObject.connect(self.ui.cboRivers,SIGNAL("currentIndexChanged(int)"),self.cboRiversChanged)

    # self.ui.cboRivers.addItem("")
    self.ui.lineEdConnection.setText( rgis.ui.lineEdCurDatabase.text() )
    self.ui.lineEdSchema.setText( rgis.ui.lineEdCurSchema.text() )
    self.populateCboRivers()
    self.riv_id = None

  def displayHelp(self):
    pass

  def reconnectIsokp(self):
    try:
      import MySQLdb
    except:
      addInfo(self.rgis, "\n\nQGIS couldn't import mysql-python Python package and cannot connect to ISOKP Database. Download compiled module mysql-python from\nhttp://www.lfd.uci.edu/~gohlke/pythonlibs/#mysql-python\nand install with:\npip install module_name.whl")
      QMessageBox.warning(self.rgis, "Import River From ISOKP", "QGIS couldn't import mysql-python Python package and cannot connect to ISOKP Database. Download compiled module mysql-python from\nhttp://www.lfd.uci.edu/~gohlke/pythonlibs/#mysql-python\nand install with:\npip install module_name.whl")
      return
    self.mydb = None
    if not self.ui.lineEdHostname == "" \
          and not self.ui.lineEdDatabase == "" \
          and not self.ui.lineEdUsername == "" \
          and not self.ui.lineEdPassword == "":
      self.mydb = MySQLdb.connect(host=self.ui.lineEdHostname.text(),
          user=self.ui.lineEdUsername.text(),
          passwd=self.ui.lineEdPassword.text(),
          db=self.ui.lineEdDatabase.text(),
          charset='utf8',
          use_unicode=True)
      # self.mydb.set_character_set('utf8')
      self.populateCboRivers()



  def populateCboRivers(self):
    self.ui.cboRivers.clear()
    rivers = []
    if not self.mydb:
      return
    cur = self.mydb.cursor()
    qry = "SELECT * FROM river_data"
    cur.execute(qry)
    data = cur.fetchall()
    for row in data:
      rivers.append([row[0], row[1], row[2], row[3]] )
    del cur

    for riv in rivers:
      self.ui.cboRivers.addItem(riv[1], riv)


  def cboRiversChanged(self):
    curInd = self.ui.cboRivers.currentIndex()
    self.riv_id, self.riv_name, self.riv_topoid, self.riv_mikeName = self.ui.cboRivers.itemData(curInd)
    self.riverName = self.ui.cboRivers.currentText()
    # print "Current river id=%i, name=%s" % (self.riv_id, self.ui.cboRivers.currentText())


  def accept(self):
    if not self.riv_id: # no river selected
      return
    self.srid = int(self.ui.lineEdSrid.text())
    if not self.srid:
      return
    QApplication.setOverrideCursor(Qt.WaitCursor)
    # PostGIS connection
    # connParams = "host='%s' port='%s' database='%s' user='%s' password='%s' sslmode='%s'" % \
    #              (self.rgis.host,self.rgis.port,self.rgis.dbname,self.rgis.user,self.rgis.passwd,self.rgis.sslmode)
    conn = self.rgis.conn
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    createPgFunctionCreateIndexIfNotExists(self.rgis)
    schema = self.ui.lineEdSchema.text()
    addInfo(self.rgis, "  Creating tables...")
    # create rivers table
    qry = 'create schema if not exists %s;' % schema
    qry += 'create table if not exists %s.rivers (gid serial primary key, topo_id integer, name text, full_name text, geom geometry(Linestring, %i));' % (schema, self.srid)
    qry += "select create_st_index_if_not_exists('%s','rivers');" % (schema)

    # create xsections table
    qry += 'create table if not exists %s.xsecs (gid serial primary key, river_id integer, disabled integer,\
            chainage double precision, interpolated integer, ver_id integer, geom geometry(Linestring, %i));' % (schema, self.srid)
    qry += "select create_st_index_if_not_exists('%s','xsecs');" % (schema)

    # create points table
    qry += 'create table if not exists %s.points (gid serial primary key, xsec_id integer, absc double precision, ordin double precision,\
     code text, marker integer, disabled integer, geom geometry(Point, %i));' % (schema, self.srid)
    qry += "select create_st_index_if_not_exists('%s','points');" % (schema)

    # we need this to complete query execution
    time.sleep(0.05)
    cur.execute(qry)
    conn.commit()


    # insert the river to PostGIS table
    addInfo(self.rgis, "  Adding %s river data to the database..." % self.riv_mikeName)
    # check if the river exists in the database
    qry = '''select * from %s.rivers;''' % schema
    cur.execute(qry)
    self.rivers = cur.fetchall()
    self.riv_gid = None
    for riv in self.rivers:
      if riv['name'] == self.riv_mikeName and riv['full_name'] == self.riv_name:
        self.riv_gid = riv['gid']
        addInfo(self.rgis, "  River %s already exists" % self.riv_mikeName)
        break
    if not self.riv_gid:
      qry = '''insert into %s.rivers (topo_id, name, full_name) select %i, \'%s\', \'%s\'
      where not exists (select gid from %s.rivers r where r.name='%s' and r.full_name='%s')
      returning gid;''' % (\
        schema, self.riv_topoid, self.riv_mikeName, self.riv_name, schema, self.riv_mikeName, self.riv_name)
      cur.execute(qry)
      self.riv_gid = cur.fetchone()[0]
    conn.commit()

    # get xsecs list of the river from ISOKP
    mcur = self.mydb.cursor()
    mqry = "SELECT * FROM cross_data WHERE (River_IDX=%i AND Ver_ID = 2)" % self.riv_id
    # TODO: add cross-section version choice to the dialog
    mcur.execute(mqry)
    mxsecs = mcur.fetchall()
  # check if the xsec exists
    qry = 'select chainage from %s.xsecs;' % (schema)
    cur.execute(qry)
    data = cur.fetchall()
    chainages = []
    for item in data:
      chainages.append(round(item[0],1))
    for mxs in mxsecs:
      if round(mxs[3],1) in chainages:
        addInfo(self.rgis, "  Skipping xsection %.3f on river %s (already exists)" % (mxs[3], self.riv_mikeName))
        continue
      # get points of the xsec from ISOKP
      coordsStr = ''
      mqry = "SELECT * FROM points WHERE Cross_ID=%i ORDER BY `Abscissa`" % mxs[0]
      mcur.execute(mqry)
      mpts = mcur.fetchall()
      for mpt in mpts:
        coordsStr += '%.3f %.3f, ' % (mpt[2], mpt[3])
      # insert current xsec to PostGIS table
      qry = '''insert into %s.xsecs (river_id, disabled, chainage, interpolated, ver_id, geom) VALUES
        (%i, %i, %.3f, %i, %i, ST_GeomFromText('LINESTRING(%s)',%i)) returning gid;''' % (\
        schema, self.riv_gid, mxs[2], mxs[3], mxs[4], 2, coordsStr[:-2], self.srid)
      cur.execute(qry)
      xs_gid = cur.fetchone()[0] # get current xsec gid
      # insert xsec points to PostGIS table
      qry = ''
      for mpt in mpts:
        qry += '''insert into %s.points (xsec_id, absc, ordin, code, marker, disabled, geom) VALUES
        (%i, %.3f, %.3f, '%s', %i, %i, ST_GeomFromText('POINT(%.3f %.3f)',%i));\n''' % (\
        schema, xs_gid, mpt[4], mpt[5], mpt[6], mpt[8], mpt[9], mpt[2], mpt[3], self.srid)
      cur.execute(qry)
    conn.commit()
    addInfo(self.rgis, "  OK")
    QApplication.setOverrideCursor(Qt.ArrowCursor)
    del mcur, cur
    QDialog.accept(self)



