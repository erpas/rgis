# -*- coding: utf-8 -*-

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *
from qgis.gui import *
from qgis.utils import *

from ui_createWaterSurfRaster import *

class DlgCreateWaterSurfRaster(QDialog):
  def __init__(self, parent=None):
    QDialog.__init__(self, parent)
    self.ui = Ui_DlgCreateWaterSurfRaster()
    self.ui.setupUi(self)
    self.qras = parent
    
    QObject.connect(self.ui.buttonBox, SIGNAL("accepted()"), self.accept)
    QObject.connect(self.ui.buttonBox, SIGNAL("rejected()"), self.reject)
    QObject.connect(self.ui.helpButton, SIGNAL("clicked()"), self.displayHelp)
    
    QObject.connect(self.ui.cboPoints,SIGNAL("currentIndexChanged(int)"),self.cboPointsChanged)
    
    self.ui.cboPoints.addItem("")
    
    self.populatePointsCombo()
    self.ptsLayer = None

  def accept(self ):
    # check input
    if not self.ptsLayer: # no src layer
      return
    QDialog.accept(self)
  
  def displayHelp(self):
    pass
    
  def addInfo(self, text):
    self.qras.ui.textEdit.append(text)
    
  def populatePointsCombo(self):
    for layerId, layer in self.qras.mapRegistry.mapLayers().iteritems():
      if layer.type() == 0 and layer.geometryType() == 0: # vector and points
        self.ui.cboPoints.addItem(layer.name(), layerId)
      if layer.type() == 0 and layer.geometryType() == 1: # vector and polylines
        pass
      if layer.type() == 0 and layer.geometryType() == 2: # vector and polygons
        pass
      if layer.type() == 1: # it's a raster
        pass
    self.updatePointsAttrs()

      
  def cboPointsChanged(self):
    curInd = self.ui.cboPoints.currentIndex()
    lid = self.ui.cboPoints.itemData(curInd)
    self.ptsLayer = self.qras.mapRegistry.mapLayer(lid)
    self.updatePointsAttrs()
      
  def updatePointsAttrs(self):
    if self.ptsLayer:
      if self.ptsLayer.featureCount():
        self.ui.cboWselAttr.clear()
        self.ui.cboWselAttr.addItem("")
        attrs = self.ptsLayer.pendingFields()
        for attr in attrs:
          self.ui.cboWselAttr.addItem(attr.name())

