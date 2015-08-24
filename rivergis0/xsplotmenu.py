# -*- coding: utf-8 -*-

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from rivergisdef import *

def isNumber(s):
    try:
        float(s)
        return True
    except ValueError:
        return False
        


class xsPlotMenu(QMenu):
  def __init__(self, parent):
    QMenu.__init__(self)
    self.parent = parent
    xsPlot = parent.ui.xsPlot
    if parent.rdbLoaded:
      self.rdb = parent.rdb

    self.zoomExtentsAction=QAction("Zoom Extents",self)
    QObject.connect(self.zoomExtentsAction, SIGNAL('triggered()'), self.parent.clearZoomStack)

    self.createMenu()
        
  def createMenu(self):
    self.addAction(self.zoomExtentsAction)
    self.addSeparator()

    self.exec_(QCursor.pos())
    
      
  def zoomToSelectedQgis(self):
    #vLayer.getFeatures( QgsFeatureRequest().setFilterExpression ( u'"xs_id" = 3' ) )
    #setSelectedFeatures( [ f.id() for f in it ] )
    idsStrs = []
    for id in self.selXsIds:
      idsStrs.append(str(id))
    sep = ", "
    selXsIdsStr = sep.join(idsStrs)
    uri = QgsDataSourceURI()
    uri.setDatabase(self.rdb.filename)
    sql = 'xs_id IN (%s)' %  selXsIdsStr
    uri.setDataSource('', 'xsecs', 'the_geom', "%s" % sql, 'xs_id')
    vLayer=QgsVectorLayer(uri.uri(), 'xs_', 'spatialite')
    if vLayer.isValid():
      #allAttrs = vLayer.pendingAllAttributesList()
      #vLayer.select(allAttrs)
      #self.parent.iface.mapCanvas().zoomToSelected()
      e = vLayer.extent()
      self.parent.canvas.setExtent(vLayer.extent())
      self.parent.canvas.refresh()
      



