# -*- coding: utf-8 -*-

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *
from qgis.gui import *
from qgis.utils import *

from os.path import dirname, isfile
#
# import psycopg2
# import psycopg2.extras

def ras2dSaveMeshPtsToGeometry(rgis,geoFileName=None):
  """Saves mesh points from current schema and table 'mesh_pts' to HEC-RAS geometry file"""
  if not geoFileName:
    s = QSettings()
    lastGeoFileDir = s.value("rivergis/lastGeoDir", "")
    geoFileName = QFileDialog.getSaveFileName(None, 'Target HEC-RAS geometry file', directory=lastGeoFileDir, filter='HEC-RAS geometry (*.g**)')
    if not geoFileName:
      return
    s.setValue("rivergis/lastGeoDir", dirname(geoFileName))

  # cur = rgis.conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
  rgis.addInfo("Saving mesh to HEC-RAS geometry file...")

  # get mesh points extent
  qry = 'select ST_XMin(ST_collect(geom)) as xmin, ST_XMax(ST_collect(geom)) as xmax,ST_YMin(ST_collect(geom)) as ymin, ST_YMax(ST_collect(geom)) as ymax from %s.mesh_pts;' % rgis.schema
  pExt = rgis.rdb.run_query(qry, True)[0]
  xmin, xmax, ymin, ymax = [pExt['xmin'], pExt['xmax'], pExt['ymin'], pExt['ymax']]
  buf = 300
  pExtStr = '%.2f, %.2f, %.2f, %.2f' % (xmin-buf, xmax+buf, ymax+buf, ymin-buf)

  # get list of mesh areas
  qry = 'select gid, name, ST_X(ST_Centroid(geom)) as x, ST_Y(ST_Centroid(geom)) as y, ST_NPoints(geom) as ptsnr from %s.areas2d;' % rgis.schema
  t = ''

  for area in rgis.rdb.run_query(qry, True):
    t += '\r\n\r\nStorage Area={:14}             ,{:14},{:14}\r\n'.format(area['name'], area['x'], area['y'])
    t += 'Storage Area Surface Line= {:d}\r\n'.format(area['ptsnr'])

    qry = 'select ST_AsText(geom) as geom from %s.areas2d where gid=%i;' % (rgis.schema, area['gid'])
    res = rgis.rdb.run_query(qry, True)[0]['geom']
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

    qry = 'select ST_X(geom) as x, ST_Y(geom) as y from %s.mesh_pts WHERE aid = %i;' % (rgis.schema, area['gid'])
    pkty = rgis.rdb.run_query(qry, True)

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

  rgis.addInfo('Mesh points saved to HEC-RAS geometry file.\n')


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