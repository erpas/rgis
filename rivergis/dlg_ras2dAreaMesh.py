# -*- coding: utf-8 -*-

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *
from qgis.gui import *
from qgis.utils import *

from os.path import dirname

from ui_ras2dAreaMesh import *

class Dlg2dAreaMeshLayers(QDialog):
  def __init__(self, parent=None):
    QDialog.__init__(self, parent)
    self.ui = Ui_AreaMesh()
    self.ui.setupUi(self)
    self.rgis = parent
    
    QObject.connect(self.ui.geoFileBtn, SIGNAL("clicked()"), self.chooseGeoFile)
    
    QObject.connect(self.ui.buttonBox, SIGNAL("accepted()"), self.accept)
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

  def accept(self):
    if not self.areasLayer: # no areas layer
      return
    QDialog.accept(self)
  
  def displayHelp(self):
    self.rgis.showHelp('create2darea.html') 
    
  def addInfo(self, text):
    self.rgis.ui.textEdit.append(text)
    
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
          if attr.name() == 'name':
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
