# -*- coding: utf-8 -*-

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *
from qgis.gui import *


def exportISOKP(dlg):
  
  dlg.addInfo("i am in")
  s = QSettings()
  lastDir = s.value("rivergis/lastRdbDir", "")
  isokpFilename = QFileDialog.getSaveFileName(None, 'ISOK Przekroje filename', directory=lastDir)

  
  for river in dlg.riversLayer.getFeatures():
    
    nazwaPlikuWynikow = "%s_%s_ISOKP.txt" % (isokpFilename, river['name'])
    
    ISOKPFile = open(nazwaPlikuWynikow, 'w')
    
    header = "chainage\tx\ty\todl\tz\tkod\tmarker\n"
    ISOKPFile.write( header )
    
    req = QgsFeatureRequest()
    qry = u'"riv_id" = %i' % (river['riv_id'])
    req.setFilterExpression(qry)
    
    for xs in dlg.xsLayer.getFeatures(req):
      req2 = QgsFeatureRequest()
      qry2 = u'"xs_id" = %i AND "filtered"=0' % (xs['xs_id'])
      req2.setFilterExpression(qry2)
    
      for pt in dlg.pointsLayer.getFeatures(req2):
        
        t =  '%i\t' % xs['chainage']
        t += '%.2f\t' % pt['x']
        t += '%.2f\t' % pt['y']
        t += '%.2f\t' % pt['abscissa']
        t += '%.2f\t' % pt['ordinate']
        t += '%s\t' % pt['cover']
        if not pt['marker'] == 0:
          t += pt['marker']
        t += '\n'
        
        ISOKPFile.write( t )
      
    ISOKPFile.close()
    
    dlg.addInfo("\nZapisalem plik wsadowy ISOKP dla rzeki %s" % (river['name']))




