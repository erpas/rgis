# -*- coding: utf-8 -*-
"""
/***************************************************************************
 RiverGisDialog
                                 A QGIS plugin
 Helps you build and manage hydraulic models in Mike 11 by DHI
                             -------------------
        begin                : 2013-11-06
        copyright            : (C) 2013 by Radoslaw Pasiok
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
from PyQt4.QtSql import *
from qgis.core import *
from qgis.gui import *
from ui_rivergis import Ui_RiverGis0
from importDialogs import *
from rivergisdef import *
from xsecstreemenu import *
from xsplotmenu import *
from export_rivergis import *
import numpy as np
import pyqtgraph as pgr
from pyqtgraph.Qt import QtCore, QtGui
from os.path import dirname
from logging_rivergis import *
import sys
from random import choice
import time

try:
    sys.path.append(r"C:\Users\admin\apps\eclipse\plugins\org.python.pydev_3.2.0.201312292215\pysrc")
    debug = True
except:
    debug = False
    logging.debug("No debug", level=logging.INFO)
    pass
try:
  from pydevd import *
except:
  pass

debug = False              


class myXsItem(QStandardItem):
  def __lt__(self, other):
    try:
      return (float(self.data(Qt.UserRole)['chainage']) <
            float(other.data(Qt.UserRole)['chainage']))
    except:
      return (self.data(Qt.UserRole)['chainage'] <
            other.data(Qt.UserRole)['chainage'])

class RiverGisDialog(QMainWindow):
  def __init__(self, parent):
    QMainWindow.__init__(self)
    self.ui = Ui_RiverGis0()
    self.ui.setupUi(self)
    self.rdbLoaded = False
    self.rdbMinimum = False
    self.iface = parent.iface
    self.canvas = self.iface.mapCanvas()
    
    self.statusBar = QStatusBar()
    self.setStatusBar(self.statusBar)
    self.statusBar.showMessage('...')
    
    self.messageBar = QgsMessageBar()

    self.mapRegistry = QgsMapLayerRegistry.instance() # .mapLayers()
    self.legend = self.iface.legendInterface()
    self.riversLayer = QgsVectorLayer()
    self.xsLayer = QgsVectorLayer()
    self.pointsLayer = QgsVectorLayer()
    self.bedPtsLayer = QgsVectorLayer()
    self.leveesLayer = QgsVectorLayer()
    self.banksLayer = QgsVectorLayer()
    self.coverLayer = QgsVectorLayer()
    self.DEM = QgsRasterLayer()
    
    self.mapPanToSelectedXs = True
    self.showFiltered = True
    self.curPtIdx = False
    self.curXsId = False
    self.lastXsId = True
    self.openedDEM = False
    self.pointsTableCreated = False

    self.openedLandCover = False
    self.rivers = []
    self.selXsecIds = []
    
    if debug:
        settrace()
    
    self.createPlot()
    self.curPt = pgr.ScatterPlotItem()
    
    self.canvas.setCanvasColor(Qt.white)
    self.canvas.enableAntiAliasing(True)
    self.canvas.mapRenderer().rendererContext().setSelectionColor(Qt.red)

    self.ui.actionOpen_SQLite_db.triggered.connect(self.openRiverDatabase)
    self.ui.actionCreate_new_SQLite_db.triggered.connect(self.createNewDatabase)
    self.ui.actionImport_River_Centerlines.triggered.connect(self.importRivers2RDb)
    
    self.ui.actionDB_Statistics.triggered.connect(self.showDbInfo)
    self.ui.actionCreate_Indexes.triggered.connect(self.createRDbIndexes)
    self.ui.actionCreateTopology.triggered.connect(self.createTopology)
    
    self.ui.actionUpdate_Selected_Cross_sections_Points_from_DEM.triggered.connect(self.updateSelectedXsProfile)
    self.ui.actionAdd_measured_Points_to_Cross_sections.triggered.connect(self.addBedPoints)
    
    self.ui.actionExport_Points_to_ISOKP.triggered.connect(self.exportPointsISOKP)
    self.ui.actionCreate_Indexes.triggered.connect(self.createRDbIndexes)

    self.ui.actionShow_Cross_section_Points_Filtered_Out_by_Simplification.triggered.connect(self.toggleShowFiltered)
    self.ui.showFilteredTool.clicked.connect(self.toggleShowFiltered)
    
    self.ui.actionPan_Map_to_Selected_Cross_sections.triggered.connect(self.toggleMapPanToSelectedXs)
    self.ui.mapPanToSelectedXsTool.clicked.connect(self.toggleMapPanToSelectedXs)
    
    self.ui.xsecsTree.setContextMenuPolicy(Qt.CustomContextMenu)
    QObject.connect(self.ui.xsecsTree,SIGNAL("customContextMenuRequested(const QPoint &)"),self.xsecsTreeRightClick)
    
    self.ui.saveMainWindowStateAction.triggered.connect(self.saveMainWindowState)
    self.ui.restoreMainWindowStateAction.triggered.connect(self.restoreMainWindowState)
    self.ui.resetMainWindowStateAction.triggered.connect(self.resetMainWindowState)
    
    self.ui.actionMap_Zoom_Extents.triggered.connect(self.zoomExtents)
    self.ui.mapZoomExtentsTool.clicked.connect(self.zoomExtents)

    self.ui.populateCombosButton.clicked.connect(self.populateCombos)
    self.ui.loadOgrRiversButton.clicked.connect(self.loadOgrRivers)
    self.ui.loadOgrXsButton.clicked.connect(self.loadOgrXs)
    self.ui.loadOgrLeveesButton.clicked.connect(self.loadOgrLevees)
    self.ui.loadOgrLandCoverButton.clicked.connect(self.loadOgrLandCover)
    self.ui.loadRasterDemButton.clicked.connect(self.loadRasterDem)
    
    QObject.connect(self.ui.comboBedPoints,SIGNAL("currentIndexChanged(int)"),self.setCurrentBedPoints)
    QObject.connect(self.ui.comboLevees,SIGNAL("currentIndexChanged(int)"),self.setCurrentLevees)
    QObject.connect(self.ui.comboBanks,SIGNAL("currentIndexChanged(int)"),self.setCurrentBanks)
    QObject.connect(self.ui.comboLandCover,SIGNAL("currentIndexChanged(int)"),self.setCurrentLandCover)
    QObject.connect(self.ui.comboLandCoverAttr,SIGNAL("currentIndexChanged(int)"),self.setCurrentLandCoverAttr)
    QObject.connect(self.ui.comboDEM,SIGNAL("currentIndexChanged(int)"),self.setCurrentDEM)
    
    self.ui.infoRiversButton.clicked.connect(self.displayInfoRivers)
    self.ui.infoXsectionsButton.clicked.connect(self.displayInfoXsections)
    self.ui.infoBedPointsButton.clicked.connect(self.displayInfoBedPoints)
    self.ui.infoLeveesButton.clicked.connect(self.displayInfoLevees)
    self.ui.infoLandCoverButton.clicked.connect(self.displayInfoLandCover)
    self.ui.infoDEMButton.clicked.connect(self.displayInfoDEM)
    
    self.ui.toggleEditingRiversButton.clicked.connect(self.toggleEditingRivers)
    self.ui.saveRiversEditsButton.clicked.connect(self.saveRiversEdits)
    
    self.ui.toggleEditingPtsButton.clicked.connect(self.toggleEditingPts)
    self.ui.savePtsEditsButton.clicked.connect(self.savePtsEdits)
    
    self.ui.importRivers2RDbButton.clicked.connect(self.importRivers2RDb)
    self.ui.importXs2RDbButton.clicked.connect(self.importXs2RDb)
    
    #self.ui.xsPlot.setContextMenuPolicy(Qt.CustomContextMenu)
    #QObject.connect(self.ui.xsPlot,SIGNAL("customContextMenuRequested(const QPoint &)"),self.xsPlotRightClick)
   
    self.restoreMainWindowState()
    self.addInfo("Welcome to Rivergis! \nPlease, load or create a new river database (DM menu).")
    
  
  
  def displayInfoRivers(self):
    if self.ui.comboRivers.count() > 0:
      curInd = self.ui.comboRivers.currentIndex()
      lid = self.ui.comboRivers.itemData(curInd)
      vl = self.mapRegistry.mapLayer(lid)
      self.addInfo(vl.metadata())
      
  def displayInfoXsections(self):
    if self.ui.comboXsections.count() > 0:
      curInd = self.ui.comboXsections.currentIndex()
      lid = self.ui.comboXsections.itemData(curInd)
      vl = self.mapRegistry.mapLayer(lid)
      self.addInfo(vl.metadata())
      
  def displayInfoBedPoints(self):
    if self.ui.comboBedPoints.count() > 0:
      curInd = self.ui.comboBedPoints.currentIndex()
      lid = self.ui.comboBedPoints.itemData(curInd)
      vl = self.mapRegistry.mapLayer(lid)
      self.addInfo(vl.metadata())
    
  def displayInfoLandCover(self):
    if self.ui.comboLandCover.count() > 0:
      curInd = self.ui.comboLandCover.currentIndex()
      lid = self.ui.comboLandCover.itemData(curInd)
      vl = self.mapRegistry.mapLayer(lid)
      self.addInfo(vl.metadata())
  
  def displayInfoLevees(self):
    if self.ui.comboLevees.count() > 0:
      curInd = self.ui.comboLevees.currentIndex()
      lid = self.ui.comboLevees.itemData(curInd)
      vl = self.mapRegistry.mapLayer(lid)
      self.addInfo(vl.metadata())
  
  def displayInfoDEM(self):
    if self.ui.comboDEM.count() > 0:
      curInd = self.ui.comboDEM.currentIndex()
      lid = self.ui.comboDEM.itemData(curInd)
      rl = self.mapRegistry.mapLayer(lid)
      self.addInfo(rl.metadata())
  
  def loadRasterDem(self):
    s = QSettings()
    lastSrcLayersDir = s.value("rivergis/lastSrcLayersDir", "")
    if lastSrcLayersDir == "":
        lastSrcLayersDir = s.value("rivergis/lastRdb", "")
    demFilename = QFileDialog.getOpenFileName(self, 'Open DEM file', directory=lastSrcLayersDir)
    if demFilename == "":
      return
    fileInfo = QFileInfo(demFilename)
    baseName = fileInfo.baseName()
    rlayer = QgsRasterLayer(demFilename, baseName)
    if rlayer.isValid():
      s.setValue("rivergis/lastDemDir", dirname(demFilename))
      self.openedDEM = demFilename
      self.DEM = rlayer
      logging.debug("Opened DEM file: %s" % str(self.openedDEM))
      self.mapRegistry.addMapLayer(rlayer, False)
      self.ui.comboDEM.addItem(rlayer.name(), userData=rlayer.id())
      self.ui.comboDEM.setCurrentIndex(self.ui.comboDEM.count()-1)
  
  def loadOgrRivers(self):
    s = QSettings()
    lastSrcLayersDir = s.value("rivergis/lastSrcLayersDir", "")
    if lastSrcLayersDir == "":
        lastSrcLayersDir = s.value("rivergis/lastRdb", "")
    filename = QFileDialog.getOpenFileName(self, 'Load Rivers Source Layer', directory=lastSrcLayersDir)
    if filename == "":
      return
    fileInfo = QFileInfo(filename)
    baseName = fileInfo.baseName() 
    vlayer = QgsVectorLayer(filename, baseName, "ogr")
    if vlayer.isValid():
      s.setValue("rivergis/lastSrcLayersDir", dirname(filename))
      logging.debug("Rivers file loaded: %s" % filename)
      self.mapRegistry.addMapLayer(vlayer, False)
      self.ui.comboRivers.addItem(vlayer.name(), userData=vlayer.id())
      self.ui.comboRivers.setCurrentIndex(self.ui.comboRivers.count()-1)
  
  def loadOgrXs(self):
    s = QSettings()
    lastSrcLayersDir = s.value("rivergis/lastSrcLayersDir", "")
    if lastSrcLayersDir == "":
        lastSrcLayersDir = s.value("rivergis/lastRdb", "")
    filename = QFileDialog.getOpenFileName(self, 'Load Cross-sections Source Layer', directory=lastSrcLayersDir)
    if filename == "":
      return
    fileInfo = QFileInfo(filename)
    baseName = fileInfo.baseName() 
    vlayer = QgsVectorLayer(filename, baseName, "ogr")
    if vlayer.isValid():
      s.setValue("rivergis/lastSrcLayersDir", dirname(filename))
      logging.debug("Xs file loaded: %s" % filename)
      self.mapRegistry.addMapLayer(vlayer, False)
      self.ui.comboXsections.addItem(vlayer.name(), userData=vlayer.id())
      self.ui.comboXsections.setCurrentIndex(self.ui.comboXsections.count()-1)

  def loadOgrBedPoints(self):
    s = QSettings()
    lastSrcLayersDir = s.value("rivergis/lastSrcLayersDir", "")
    if lastSrcLayersDir == "":
        lastSrcLayersDir = s.value("rivergis/lastRdb", "")
    filename = QFileDialog.getOpenFileName(self, 'Load Bed Points Source Layer', directory=lastSrcLayersDir)
    if filename == "":
      return
    fileInfo = QFileInfo(filename)
    baseName = fileInfo.baseName() 
    vlayer = QgsVectorLayer(filename, baseName, "ogr")
    if vlayer.isValid():
      self.bedPtsLayer = vlayer
      s.setValue("rivergis/lastSrcLayersDir", dirname(filename))
      logging.debug("Bed Points file loaded: %s" % filename)
      self.mapRegistry.addMapLayer(vlayer, False)
      self.ui.comboBedPoints.addItem(vlayer.name(), userData=vlayer.id())
      self.ui.comboBedPoints.setCurrentIndex(self.ui.comboBedPoints.count()-1)
      
  def loadOgrLevees(self):
    s = QSettings()
    lastSrcLayersDir = s.value("rivergis/lastSrcLayersDir", "")
    if lastSrcLayersDir == "":
        lastSrcLayersDir = s.value("rivergis/lastRdb", "")
    filename = QFileDialog.getOpenFileName(self, 'Load Levees Source Layer', directory=lastSrcLayersDir)
    if filename == "":
      return
    fileInfo = QFileInfo(filename)
    baseName = fileInfo.baseName() 
    vlayer = QgsVectorLayer(filename, baseName, "ogr")
    if vlayer.isValid():
      s.setValue("rivergis/lastSrcLayersDir", dirname(filename))
      logging.debug("Levees file loaded: %s" % filename)
      self.mapRegistry.addMapLayer(vlayer, False)
      self.ui.comboLevees.addItem(vlayer.name(), userData=vlayer.id())
      self.ui.comboLevees.setCurrentIndex(self.ui.comboLevees.count()-1)
       
  def loadOgrLandCover(self):
    s = QSettings()
    lastSrcLayersDir = s.value("rivergis/lastSrcLayersDir", "")
    if lastSrcLayersDir == "":
        lastSrcLayersDir = s.value("rivergis/lastRdb", "")
    filename = QFileDialog.getOpenFileName(self, 'Load Land Cover Source Layer', directory=lastSrcLayersDir)
    if filename == "":
      return
    fileInfo = QFileInfo(filename)
    baseName = fileInfo.baseName() 
    vlayer = QgsVectorLayer(filename, baseName, "ogr")
    if vlayer.isValid():
      self.coverLayer = vlayer
      s.setValue("rivergis/lastSrcLayersDir", dirname(filename))
      logging.debug("Land Cover file loaded: %s" % filename)
      self.mapRegistry.addMapLayer(vlayer, False)
      self.ui.comboLandCover.addItem(vlayer.name(), userData=vlayer.id())
      self.ui.comboLandCover.setCurrentIndex(self.ui.comboLandCover.count()-1)
      
  def setCurrentBedPoints(self):
    curInd = self.ui.comboBedPoints.currentIndex()
    lid = self.ui.comboBedPoints.itemData(curInd)
    self.bedPointsLayer = self.mapRegistry.mapLayer(lid)
    self.addInfo("Current bed points layer is: %s" % self.ui.comboBedPoints.currentText())
  
  def setCurrentLevees(self):
    curInd = self.ui.comboLevees.currentIndex()
    lid = self.ui.comboLevees.itemData(curInd)
    self.leveesLayer = self.mapRegistry.mapLayer(lid)
    self.addInfo("Current bed points layer is: %s" % self.ui.comboBedPoints.currentText())
    
  def setCurrentBanks(self):
    curInd = self.ui.comboBanks.currentIndex()
    lid = self.ui.comboBanks.itemData(curInd)
    self.banksLayer = self.mapRegistry.mapLayer(lid)
    self.addInfo("Current bed points layer is: %s" % self.ui.comboBedPoints.currentText())
    
  def setCurrentLandCover(self):
    curInd = self.ui.comboLandCover.currentIndex()
    lid = self.ui.comboLandCover.itemData(curInd)
    self.coverLayer = self.mapRegistry.mapLayer(lid)
    self.addInfo("Current land cover is: %s" % self.ui.comboLandCover.currentText())
  
  def setCurrentLandCoverAttr(self):
    curInd = self.ui.comboLandCoverAttr.currentIndex()
    self.currentLandCoverAttr = self.ui.comboLandCoverAttr.currentText()
    if not self.currentLandCoverAttr == "":
      self.addInfo("Current land cover attribute is: %s" % self.currentLandCoverAttr)
  
  def setCurrentDEM(self):
    curInd = self.ui.comboDEM.currentIndex()
    lid = self.ui.comboDEM.itemData(curInd)
    self.DEM = self.mapRegistry.mapLayer(lid)
    self.addInfo("Current DEM is: %s" % self.ui.comboDEM.currentText())
    
  def msg(self, text, lev=0):
    if lev == 0:
      begin = "Info: "
    elif lev == 1:
      begin = "Warning: "
    elif lev == 2:
      begin = "Error: "
    else:
      begin = "Info: "
    self.messageBar.pushMessage(begin, text, level=lev)
    
  
  def toggleShowFiltered(self):
    self.showFiltered = not self.showFiltered
    self.ui.showFilteredTool.setChecked(self.showFiltered)
    self.ui.actionShow_Cross_section_Points_Filtered_Out_by_Simplification.setChecked(self.showFiltered)
    self.updateXsPlot(self.curXsId, resetRange=False)
    self.statusBar.showMessage('Show Filtered = %s' % self.showFiltered, 3000)
    
  def toggleMapPanToSelectedXs(self):
    self.mapPanToSelectedXs = not self.mapPanToSelectedXs
    self.ui.mapPanToSelectedXsTool.setChecked(self.mapPanToSelectedXs)
    self.ui.actionPan_Map_to_Selected_Cross_sections.setChecked(self.mapPanToSelectedXs)
    self.statusBar.showMessage('Map Pan To Selected = %s' % self.mapPanToSelectedXs, 3000)
      
  def zoomExtents(self):
    self.canvas.zoomToFullExtent()
    self.canvas.refresh()

  def showEvent(self, event):
    #t = "event.type()=%s,  event.key()=%s" % (event.type(), event.key()))
    t = "event.type()=%s" % (event)
    self.statusBar.showMessage(t)

#     for layer in self.mapRegistry.mapLayers().values():
#       self.canvasLayerSet.append(QgsMapCanvasLayer(layer))

  def loadLayersToMap(self):
    if self.riversLayer.isValid():
      self.riversColor = QColor('#000099')
      self.riversSymbol = QgsSymbolV2.defaultSymbol(self.riversLayer.geometryType())
      self.riversSymbol.setColor(self.riversColor)
      self.riversRenderer = QgsSingleSymbolRendererV2(self.riversSymbol)
      self.riversLayer.setRendererV2(self.riversRenderer)
      self.mapRegistry.addMapLayer(self.riversLayer)
    else:
      logging.debug("RDb Rivers is not valid. Cannot load it into canvas")
      
    if self.xsLayer.isValid():
      self.xsColor = QColor('#00aa00')
      self.xsSymbol = QgsSymbolV2.defaultSymbol(self.xsLayer.geometryType())
      self.xsSymbol.setColor(self.xsColor)
      self.xsRenderer = QgsSingleSymbolRendererV2(self.xsSymbol)
      self.xsLayer.setRendererV2(self.xsRenderer)
      self.mapRegistry.addMapLayer(self.xsLayer)
    else:
      logging.debug("Impossible to Load xsections into canvas")
        
    self.canvas.setExtent(self.xsLayer.extent())
    self.canvas.refresh()
    

  def openRiverDatabase(self, rdbFilename=None):
    s = QSettings()
    lastDir = s.value("rivergis/lastRdbDir", "")
    if rdbFilename:
      dbFilename = rdbFilename
    else:
      dbFilename = QFileDialog.getOpenFileName(self, 'Open SQLite database file', directory=lastDir)
    if dbFilename == "":
      return
    s.setValue("rivergis/lastRdb", dbFilename)
    s.setValue("rivergis/lastRdbDir", dirname(dbFilename))
    self.rdb = RiverDb(dbFilename)
    self.rivers = self.rdb.getRivers()
    self.rdbLoaded = True
    self.ui.actionOpen_SQLite_db.setEnabled(False)
    self.ui.actionCreate_new_SQLite_db.setEnabled(False)
    logging.debug(str(self.rivers))
    
    self.UriRivers = QgsDataSourceURI()
    self.UriRivers.setDatabase(self.rdb.filename)
    self.UriRivers.setDataSource('', 'rivers', 'the_geom')
    self.riversDBLayer = QgsVectorLayer(self.UriRivers.uri(), 'RDb Rivers', 'spatialite')
    self.riversColor = QColor('#000099')
    self.riversSymbol = QgsSymbolV2.defaultSymbol(self.riversDBLayer.geometryType())
    self.riversSymbol.setColor(self.riversColor)
    self.riversRenderer = QgsSingleSymbolRendererV2(self.riversSymbol)
    self.riversDBLayer.setRendererV2(self.riversRenderer)
    self.mapRegistry.addMapLayer(self.riversDBLayer, True)
    self.riversLayer = self.mapRegistry.mapLayersByName('RDb Rivers')[0]
    
    self.UriXsecs = QgsDataSourceURI()
    self.UriXsecs.setDatabase(self.rdb.filename)
    self.UriXsecs.setDataSource('', 'xsecs', 'the_geom')
    self.xsDBLayer = QgsVectorLayer(self.UriXsecs.uri(), 'RDb Cross-sections', 'spatialite')
    self.xsColor = QColor('#00aa00')
    self.xsSymbol = QgsSymbolV2.defaultSymbol(self.xsDBLayer.geometryType())
    self.xsSymbol.setColor(self.xsColor)
    self.xsRenderer = QgsSingleSymbolRendererV2(self.xsSymbol)
    self.xsDBLayer.setRendererV2(self.xsRenderer)
    self.mapRegistry.addMapLayer(self.xsDBLayer, True)
    self.xsLayer = self.mapRegistry.mapLayersByName('RDb Cross-sections')[0]
    
    self.UriPoints = QgsDataSourceURI()
    self.UriPoints.setDatabase(self.rdb.filename)
    self.UriPoints.setDataSource('', 'points', 'the_geom')
    self.pointsDBLayer = QgsVectorLayer(self.UriPoints.uri(), 'RDb Points', 'spatialite')
    self.mapRegistry.addMapLayer(self.pointsDBLayer, True)
    self.pointsLayer = self.mapRegistry.mapLayersByName('RDb Points')[0]
    self.legend.setLayerVisible(self.pointsLayer, False)
    
    if self.riversLayer.isValid() and self.xsLayer.isValid():
      self.rdbMinimum = True
      self.drawXsecsTree()

    self.createRiversTable()
    
    if self.xsLayer.featureCount():
      self.canvas.setExtent(self.xsLayer.extent())
      self.canvas.refresh()
      self.curXsId = self.xsLayer.getFeatures().next()['xs_id']
      if self.curXsId and self.pointsTableCreated:
        self.updateXsPlot(self.curXsId)
    
    if self.pointsLayer.featureCount():
      self.createPointsTable()
      self.updatePointsTable(self.curXsId)
    self.addInfo("River database %s opened." % dbFilename)
    self.showDbInfo()
    
    
  def showDbInfo(self):
    riversCount = self.riversLayer.featureCount()
    xsCount = self.xsLayer.featureCount()
    pointsCount = self.pointsLayer.featureCount()
    
    self.addInfo("Currently database contains:")
    stats = " - %i rivers \n - %i cross-sections\n - %i points" % (riversCount, xsCount, pointsCount)
    self.addInfo(stats)
        

  def createNewDatabase(self):
    s = QSettings()
    lastDir = s.value("rivergis/lastRdbDir", "")
    try:
      dbFilename = QFileDialog.getSaveFileName(self, 'New SQLite database file', directory=lastDir)
    except:
      logging.debug("Create new DB cancelled")
      self.msg("Create new DB cancelled", 0)
      logging.debug("Create new DB cancelled")
      return
    
    if not dbFilename.endswith(".sqlite"):
      dbFilename += ".sqlite"
    if not dbFilename == ".sqlite":
      try:
        s.setValue("rivergis/lastRdb", dbFilename)
        s.setValue("rivergis/lastRdbDir", dirname(dbFilename))
        srid, ok = QInputDialog.getText(self, 'Set a SRID for River Database', 
        '''<html><head/><body><p>River Database SRID: </p></body></html>''')
        db = RiverDb(dbFilename, int(srid))
        self.addInfo("New river DB created. Insert a river, cross-sections and points.\nGo to Source layers Tab, set a source layer and import it.")
        self.openRiverDatabase(dbFilename)
      except:
        logging.debug("Could not create a new river DB")
        self.ui.infoTextBrowser.setHtml("Could not create a new river DB - check the log file.")
        
  
  def importRivers2RDb(self):
    if not self.rdbLoaded:
      QMessageBox.warning(self, "Import river centerlines", "Load an existing river database or create a new one.")
      return
    if self.ui.comboRivers.count() > 0:
      curInd = self.ui.comboRivers.currentIndex()
      lid = self.ui.comboRivers.itemData(curInd)
      self.rivers2Import = self.mapRegistry.mapLayer(lid)
    else:
      QMessageBox.warning(self, "Import river centerlines", "Load a river layer from QGIS or any OGR layer (i.e. Shapefile)")
      return
    if self.rivers2Import.isValid():
      d = ImportRiver2RDbDialog(self)
      if d.exec_():
        nameAttr = d.ui.comboRivernameAttr.currentText()
        topoIDAttr = d.ui.comboTopoIDAttr.currentText()
        chainUpstreamAttr = d.ui.comboChainUpstreamAttr.currentText()
        chainDownstreamAttr = d.ui.comboChainDownstreamAttr.currentText()
      self.riversLayer.startEditing()
      feats = self.rivers2Import.getFeatures()
      for feat in feats:
        geom = feat.geometry()
        name = "A River"
        topoID = "A TopoID"
        chainUpstream = geom.length()
        chainDownstream = 0
        if not nameAttr == "" and not feat[nameAttr] == None: name = str(feat[nameAttr])
        if not topoIDAttr == "" and not feat[topoIDAttr] == None: topoID = str(feat[topoIDAttr])
        if not chainUpstreamAttr == "" and not feat[chainUpstreamAttr] == None: chainUpstream = float(feat[chainUpstreamAttr])
        if not chainDownstreamAttr == "" and not feat[chainDownstreamAttr] == None: chainDownstream = float(feat[chainDownstreamAttr])
        newRiv = QgsFeature()
        newRiv.setGeometry( geom )
        newRiv.setAttributes([NULL, topoID, "", name, "", chainUpstream, chainDownstream, ""])
        res = self.riversLayer.addFeature( newRiv, alsoUpdateExtent = True )
        if not res:
          QMessageBox.warning(self, "Import Rivers failed ", "Something went wrong")
          return
      self.riversLayer.commitChanges()
      self.addInfo("Rivers added.")
    self.drawXsecsTree()


  def importXs2RDb(self):
    if not self.rdbLoaded:
      QMessageBox.warning(self, "Import xsections", "Load or create a new river database")
      return
    if self.ui.comboXsections.count() > 0:
      curInd = self.ui.comboXsections.currentIndex()
      lid = self.ui.comboXsections.itemData(curInd)
      self.xs2Import = self.mapRegistry.mapLayer(lid)
    else:
      QMessageBox.warning(self, "Import cross-sections centerlines", "Load a cross-section layer from QGIS or any OGR layer (i.e. Shapefile)")
      return
    if self.xs2Import.isValid():
      feats = self.xs2Import.getFeatures()
      self.xsLayer.startEditing()
      for feat in feats:
        geom = feat.geometry()
        newXs = QgsFeature()
        newXs.setGeometry(geom)
        newXs.setAttributes([NULL,NULL,NULL,NULL])
        res = self.xsLayer.addFeature( newXs, alsoUpdateExtent = True )
        if not res:
          QMessageBox.warning(self, "Import Cross-sections failed ", "Something went wrong")
          return
      self.xsLayer.commitChanges()
      self.addInfo("Cross-sections added.")
    self.drawXsecsTree()


  def checkRdbMinimum(self):
    if len(self.rivers) > 0:
      cur = self.rdb.conn.cursor()
      qry = "SELECT xs_id FROM xsecs WHERE riv_id=%i" % self.rdb.rivIds[0]
      cur.execute(qry)
      if cur.fetchone()[0]:
        self.rdbMinimum = True
      del cur
      
    
  def populateCombos(self):
    '''Populates source layers combos with layers from QgsMapLayerRegistry.
    '''
    self.ui.comboRivers.clear()
    self.ui.comboXsections.clear()
    self.ui.comboBedPoints.clear()
    self.ui.comboLevees.clear()
    self.ui.comboLandCover.clear()
    self.ui.comboLandCoverAttr.clear()
    self.ui.comboDEM.clear()
    for layerId, layer in self.mapRegistry.mapLayers().iteritems():
      if layer.type() == 0 and layer.geometryType() == 1: # vector and plines
        if not layer.name() in ['RDb Cross-sections', 'RDb Rivers', 'RDb Levees']:
          self.ui.comboRivers.addItem(layer.name(), layerId)
          self.ui.comboXsections.addItem(layer.name(), layerId)
          self.ui.comboLevees.addItem(layer.name(), layerId)
      if layer.type() == 0 and layer.geometryType() == 0: # vector and points
        if not layer.name() in ['RDb Points']:
          self.ui.comboBedPoints.addItem(layer.name(), layerId)
          self.bedPointsLayer = layer
      if layer.type() == 0 and layer.geometryType() == 2: # vector and polygons
        self.ui.comboLandCover.addItem(layer.name(), layerId)
        self.coverLayer = layer
        self.updateComboLandCoverAttr()
      if layer.type() == 1: # it's a raster
        self.ui.comboDEM.addItem(layer.name(), layerId)
        self.openedDEM = True
        self.DEM = layer
      self.updatePointsTable(self.curXsId)
      
  def updateComboLandCoverAttr(self):
    self.setCurrentLandCover()
    if self.coverLayer.featureCount():
      self.ui.comboLandCoverAttr.clear()
      self.ui.comboLandCoverAttr.addItem("")
      coverAttrs = self.coverLayer.pendingFields()
      for attr in coverAttrs:
        self.ui.comboLandCoverAttr.addItem(attr.name())
        
  def createXsecsTree(self):
    if not self.rdbMinimum:
      return
    tree = QStandardItemModel(0,1)
    tree.setHorizontalHeaderItem(0,QStandardItem('Rivers and x-sections'))
    rivs = self.riversLayer.getFeatures()
    for riv in rivs:
      rivItem=QStandardItem(riv['name'])
      rivItem.setData(riv,32)
      req = QgsFeatureRequest()
      req.setFilterExpression(( u'"riv_id" = %i' % riv['riv_id'] ))
      xss = self.xsLayer.getFeatures(req)
      for xs in xss:
        xsItem=myXsItem(str(xs['chainage']))
        xsItem.setData(xs,32)
        rivItem.appendRow(xsItem)
      rivItem.sortChildren(0)
      tree.appendRow(rivItem)
    return tree
  
  def drawXsecsTree(self):
    self.xsTreeModel = self.createXsecsTree()
    self.ui.xsecsTree.setModel(self.xsTreeModel)
    self.xsTreeSelModel = self.ui.xsecsTree.selectionModel()
    self.xsTreeSelModel.selectionChanged.connect(self.treeSelectionChange)
    self.ui.xsecsTree.collapseAll()
#     self.ui.xsecsTree.expand(0)
    return True
  
  def treeSelectionChange(self, selected, deselected):
    if not self.rdbMinimum:
      return
    self.curPtIdx = False # reset xs points selection
    self.treeSelmodel = self.ui.xsecsTree.selectionModel()
    self.treeSelIndexes = self.treeSelmodel.selectedIndexes()
    self.selXsecIds = []
    self.selRiverIds = []
    
    for idx in self.treeSelIndexes:
      if idx.parent() == QModelIndex(): # it's a River
        rivFeat = idx.data(32)
        self.selRiverIds.append(rivFeat['riv_id'])
      else: # it's a cross-section
        xsFeat = idx.data(32)
        self.selXsecIds.append(xsFeat['xs_id'])
    
    # change last and currently selected Xs
#     self.lastXsId = self.curXsId
    if self.selXsecIds == []: # keep at least current Xs if selection is empty
      self.selXsecIds = [self.curXsId]

    
    if self.selXsecIds:
      self.curXsId = self.selXsecIds[0] # first element from selection is the current Xs 
      self.updateXsPlot(self.selXsecIds[0])
      self.updatePointsTable(self.selXsecIds[0])
      if self.xsLayer.selectedFeatureCount() > 0:  self.xsLayer.removeSelection()
      for xsId in self.selXsecIds:
        self.xsLayer.select(xsId)
      if self.mapPanToSelectedXs:
        self.canvas.panToSelected(self.xsLayer)
      
#       self.addInfo("Selected cross-sections: %s" % str(self.selXsecIds))
    
  
  def addInfo(self, text):
    self.ui.infoTextBrowser.append(text)
      
  def saveMainWindowState(self):
    s = QSettings()
    s.setValue("rivergis/geometry", self.saveGeometry())
    s.setValue("rivergis/windowState", self.saveState())
    
    
  def restoreMainWindowState(self):
    s = QSettings()
    if not s.value("rivergis/geometry") == None:
      self.restoreGeometry(s.value("rivergis/geometry"))
      self.restoreState(s.value("rivergis/windowState"))
    
  
  # TODO - find a way to reset windows state
  def resetMainWindowState(self):
    s = QSettings()
    s.setValue("rivergis/geometry", QByteArray())
    s.setValue("rivergis/windowState", QByteArray())
    self.restoreMainWindowState()
    
    
  def xsecsTreeRightClick(self, pos):
    if not self.rdbMinimum:
      return
    selmodel = self.ui.xsecsTree.selectionModel()
    selIdxs = selmodel.selectedIndexes()
    
    if selIdxs:
      logging.debug('selected xsecs ids: %s' % (str(self.selXsecIds)))
      logging.debug('selected rivers ids: %s' % (str(self.selRiverIds)))
      itemClicked = self.ui.xsecsTree.indexAt(pos)
      parentItemClicked = itemClicked.parent()
      logging.debug('clicked item is %s' % (itemClicked))
      logging.debug('parent of the clicked item is %s' % (parentItemClicked))
      if parentItemClicked == QModelIndex(): # we need a River MENU
        self.xsecsTreeMenu = xsecsTreeMenuRiv(self, self.selRiverIds)
      else: # we need a xsec MENU
        self.xsecsTreeMenu = xsecsTreeMenuXs(self, self.selXsecIds)
        

  def createPlot(self):
    self.xsPlot = self.ui.xsPlot
    self.xsPlot.rdbLoaded = False
    xData = np.array([0, 0.5, 1])
    yData = np.array([1, 0, 1])
      
    self.xsPlot.showGrid(1, 1, 1)
    self.xsPlot.setBackground('w')
    #self.xsPlot.setAntialiasing(True)
    self.xsVB = self.ui.xsPlot.getViewBox()
    self.xsVB.keyPressEvent = self.keyPressEvent

    self.xsGround = pgr.PlotDataItem(x=xData, y=yData, pen='k', symbol='s', symbolSize=3, symbolPen='k')
    self.xsPlot.addItem(self.xsGround)
    self.xsFiltered = pgr.PlotDataItem(pen=None, symbol='d', symbolSize=3, symbolPen=0.7)
    self.xsPlot.addItem(self.xsFiltered)
    
    
  def keyPressEvent(self, ev):
    if self.rdbLoaded and not self.curPtIdx == False:
      xs = self.ui.xsPlot.xs
      if type(ev) == QKeyEvent and ev.key() == Qt.Key_1 :
        xs.moveMarker(1, self.curPtIdx)
      elif type(ev) == QKeyEvent and ev.key() == Qt.Key_2 :
        xs.moveMarker(2, self.curPtIdx)
      elif type(ev) == QKeyEvent and ev.key() == Qt.Key_3 :
        xs.moveMarker(3, self.curPtIdx)
      elif type(ev) == QKeyEvent and ev.key() == Qt.Key_4 :
        xs.moveMarker(4, self.curPtIdx)
      elif type(ev) == QKeyEvent and ev.key() == Qt.Key_5 :
        xs.moveMarker(5, self.curPtIdx)
      elif type(ev) == QKeyEvent and ev.key() == Qt.Key_Delete :
        self.deleteSinglePoint(self.curPtIdx)
        
      else:
          #ev.ignore()
          pass
      self.updateXsPlot(self.curXsId, resetRange=False)
            
  def updateXsPlot(self, xsId, resetRange=True):
    self.xsVB.disableAutoRange()
    xsPlot = self.xsPlot
    xsPlot.clear()
    self.curPt = pgr.ScatterPlotItem()
    # TODO: get xs points via QGIS API
    xsPlot.xs = Xsection(self.rdb, "", "", xsId)
    xsPlot.xs.fetchAbscOrdinFromDb()
    xsPlot.xs.fetchMarkersFromDb()
   
    if self.showFiltered:
      xsPlot.xs.fetchFiltered()
      logging.debug('There is %i active and %i filtered points in xsId=%i' % (len(xsPlot.xs.ptIds), len(xsPlot.xs.filtered[0]), xsPlot.xs.xsId))
      fX = np.array(xsPlot.xs.filtered[0])
      fY = np.array(xsPlot.xs.filtered[1])
      self.xsFiltered = pgr.PlotDataItem(x=fX, y=fY, pen=None, symbol='d', symbolSize=3, symbolPen=0.7, symbolBrush=0.7)
      self.xsPlot.addItem(self.xsFiltered)
    
    xsPlot.groundX = np.array(xsPlot.xs.abscissas)
    xsPlot.groundY = np.array(xsPlot.xs.ordinates)
    xsPlot.ptIds = np.array(xsPlot.xs.ptIds)
    self.xsGround = pgr.PlotDataItem(x=xsPlot.groundX, y=xsPlot.groundY, data=xsPlot.ptIds, pen='k', symbol='o', symbolSize=4, symbolPen='k', symbolBrush='k', pxMode=True)
    self.xsPlot.addItem(self.xsGround)
    
#     ptIds = np.array(xsPlot.xs.ptIds)
#     abscissas = np.array(xsPlot.xs.abscissas)
#     ordinates = np.array(xsPlot.xs.ordinates)
#     covers = np.array(xsPlot.xs.covers)
#     colors = ('b', 'g', 'r', 'c', 'm', 'y', 'k', 'w')
#     groundItems = []
#     start = 0
#     for i, pt in enumerate(xsPlot.xs.abscissas[1:]):
#       if xsPlot.xs.covers[i-1] == xsPlot.xs.covers[i]:
#         continue
#       else: # change in cover
#         ptIds = np.array(xsPlot.xs.ptIds)[start:i]
#         groundX = np.array(xsPlot.xs.abscissas)[start:i]
#         groundY = np.array(xsPlot.xs.ordinates)[start:i]
#         cov = np.array(xsPlot.xs.ptIds)[start:i]
#         item = pgr.PlotDataItem(x=groundX, y=groundY, data=ptIds, pen=choice(colors), symbol='o', symbolSize=4, symbolPen='k', symbolBrush='k', pxMode=True)
#         self.xsPlot.addItem(item)
#         start = i
        
    self.markerLine = {}
    for m in xsPlot.xs.markers.keys():
      self.markerLine[m] = pgr.InfiniteLine(pos=None, angle=90, pen=None, movable=False, bounds=None)
      if m == 1 or m == 3:
        self.markerLine[m].setPen(pgr.mkPen('r', width=2))
      elif m == 2:
        self.markerLine[m].setPen(pgr.mkPen('r', width=1))
      elif m == 4 or m == 5:
        self.markerLine[m].setPen(pgr.mkPen('b', width=1))
      self.markerLine[m].setValue(xsPlot.xs.markers[m])
      xsPlot.addItem(self.markerLine[m])
      logging.debug("Marker %i w punkcie x=%.2f" % (m,xsPlot.xs.markers[m]))
    self.xsGround.sigPointsClicked.connect(self.ptsClicked)
    
    if resetRange:
      self.xsVB.autoRange()

      
  def ptsClicked(self, plot, points):
    # reset visible selection from previously selected pt
    self.curPt.setPen('k')
    self.curPt.setSize(4)
    self.curPt.setBrush('k')

    p = points[0] # take first point from selection
    p.setPen('r')
    p.setSize(9)
    p.setBrush(pgr.mkBrush(255,255,255,0))
    self.curPt = p
    logging.debug("clicked points data: %s" % p.data())
    logging.debug("clicked points pos: %s" % p.pos())
    self.curPtIdx = p.data()
    
    
  def createRiversTable(self):
    self.rivCache = QgsVectorLayerCache(self.riversLayer, 1000)
    self.riversTableModel = QgsAttributeTableModel(self.rivCache)
    self.riversTableModel.loadLayer()
    self.riversTableFilterModel = QgsAttributeTableFilterModel(self.canvas, self.riversTableModel)
    self.ui.tableViewRivers.setModel(self.riversTableFilterModel)
    self.ui.tableViewRivers.resizeColumnsToContents()
    
    
  def createPointsTable(self):
    self.ptsCache = QgsVectorLayerCache(self.pointsLayer, 1000000)
#     self.ptsCache.setFullCache(True)
    self.ptsTableModel = QgsAttributeTableModel(self.ptsCache)
    self.ptsTableModel.loadLayer()
    self.ptsTableFilterModel = QgsAttributeTableFilterModel(self.canvas, self.ptsTableModel)
    self.ptsTableFilterModel.setFilterMode(QgsAttributeTableFilterModel.ShowFilteredList)
    self.ui.tableViewPoints.setModel(self.ptsTableFilterModel)
    self.ui.tableViewPoints.resizeColumnsToContents()
    self.pointsTableCreated = True
    
    
  def updatePointsTable(self, xsId):
    if self.pointsTableCreated:
      self.ptsTableModel.loadLayer()
      # find IDs of points of the current xs
      if self.pointsLayer.featureCount():
        ptIds = []
        req = QgsFeatureRequest()
        req.setFilterExpression( u'"xs_id"=%i' % xsId)
        pts = self.pointsLayer.getFeatures(req)
        for pt in pts:
          ptIds.append(pt['pt_id'])
        self.ptsTableFilterModel.setFilteredFeatures(ptIds)
    else:
      self.createPointsTable()
      self.updatePointsTable(xsId)
      

  def toggleEditingRivers(self):
    if not self.riversLayer.isEditable():
      self.riversLayer.startEditing()
    else:
      # TODO - ask for commitChanges or rollBack()
      self.riversLayer.commitChanges()
      self.drawXsecsTree()

  def saveRiversEdits(self):
    self.riversLayer.commitChanges()
    self.riversLayer.startEditing()
    
  def toggleEditingPts(self):
    if not self.pointsLayer.isEditable():
      self.pointsLayer.startEditing()
    else:
      # TODO - ask for commitChanges or rollBack()
      self.pointsLayer.commitChanges()
      self.updatePointsTable(self.curXsId)

  def savePtsEdits(self):
    self.pointsLayer.commitChanges()
    self.updatePointsTable(self.curXsId)
    self.pointsLayer.startEditing()
    
                
  def createTopology(self):
    if 1:
      # calculate rivers chainages if empty 
      self.riversLayer.startEditing()
      rivIter = self.riversLayer.getFeatures()
      for riv in rivIter:
        if riv['ch_upstr'] and riv['ch_downstr']:
          pass
        else:
          rivGeom = riv.geometry()
          rivLen = rivGeom.length()
          riv['ch_upstr'] = rivLen
          riv['ch_downstr'] = 0
          self.riversLayer.updateFeature(riv)
      self.riversLayer.commitChanges()
      
      cur = self.rdb.conn.cursor()
      xsIter = self.xsLayer.getFeatures()
      self.xsLayer.startEditing()
      
      for xs in xsIter:
        xsGeom = xs.geometry()
        xsId = xs['xs_id']
        rivIter = self.riversLayer.getFeatures()
        for riv in rivIter:
          rivId = riv['riv_id']
          rivGeom = riv.geometry()
          rivLen = abs(riv['ch_upstr']-riv['ch_downstr'])
          fet = QgsFeature()
          fet.setGeometry( xsGeom.intersection(rivGeom) )
          wkt = fet.geometry().exportToWkt()
          qry = 'SELECT ST_Line_Locate_Point( (select the_geom from rivers where riv_id = %i), ST_GeomFromText(\'%s\', %i) )' % (rivId, wkt, self.rdb.srid)
          cur.execute(qry)
          m = cur.fetchone()[0]
          if m:
            chainage = int(riv['ch_downstr']+(1-m) * rivLen)
            xs['riv_id'] =  rivId
            xs['chainage'] = chainage
            self.xsLayer.updateFeature(xs)
        del rivIter
      del xsIter
      self.xsLayer.commitChanges()
#       self.curXsId = -1 # do autoRange of xs plot
      self.curXsId = self.xsLayer.getFeatures().next()['xs_id']
      self.updateXsPlot(self.curXsId)
#       self.updateXsPlot(self.selXsecIds[0], False)
      self.drawXsecsTree()
      self.addInfo("Topology created.")

      
    else:
      msg = 'Creating topology failed. Check....'
      QMessageBox.information(self, 'Update Cross-section from DEM', msg)
      return

  def deleteSinglePoint(self, ptId):
    '''Deletes a cross-section point.
    '''
    self.pointsLayer.startEditing()
    self.pointsLayer.setSelectedFeatures([ptId])
    self.pointsLayer.deleteSelectedFeatures()
    self.pointsLayer.commitChanges()
    self.updateXsPlot(self.curXsId, False)
    self.updatePointsTable(self.curXsId)
    
    
  def deletePoints(self, xsIds):
    '''Deletes existing xsecs points, except markers.
    '''
    self.pointsLayer.startEditing()
    xss = []
    for xsId in xsIds:
      xss.append(str(xsId))
    sep = ", "
    xsIdsStr = sep.join(xss)
    req = QgsFeatureRequest()
    qry = u'xs_id IN (%s) AND marker = 0' % xsIdsStr
    req.setFilterExpression(qry)
    pts = self.pointsLayer.getFeatures(req)
    ptIds = []
    for pt in pts:
      ptIds.append(pt.id())
#     self.addInfo("Points to delete: %s" % str(ptIds))
    self.pointsLayer.setSelectedFeatures(ptIds)
    self.pointsLayer.deleteSelectedFeatures()
    self.pointsLayer.commitChanges()
    self.updateXsPlot(self.curXsId, False)
    self.updatePointsTable(self.curXsId)

  def deletePointsSimplified(self, xsIds):
    '''Deletes xsecs points filtered out by simplification.
    '''
    self.pointsLayer.startEditing()
    xss = []
    for xsId in xsIds:
      xss.append(str(xsId))
    sep = ", "
    xsIdsStr = sep.join(xss)
    req = QgsFeatureRequest()
    qry = u'xs_id IN (%s) AND filtered <> 0' % xsIdsStr
    req.setFilterExpression(qry)
    pts = self.pointsLayer.getFeatures(req)
    ptIds = []
    for pt in pts:
      ptIds.append(pt.id())
    self.pointsLayer.setSelectedFeatures(ptIds)
    self.pointsLayer.deleteSelectedFeatures()
    self.pointsLayer.commitChanges()
    self.updateXsPlot(self.curXsId, False)
    self.updatePointsTable(self.curXsId)
  
  def unSimplifySelected(self, xsIds):
    '''Sets 'filtered' attr to 0 for selected xss points
    '''
    self.pointsLayer.startEditing()
    xss = []
    for xsId in xsIds:
      xss.append(str(xsId))
    sep = ", "
    xsIdsStr = sep.join(xss)
    req = QgsFeatureRequest()
    qry = u'xs_id IN (%s) AND filtered <> 0' % xsIdsStr
    req.setFilterExpression(qry)
    pts = self.pointsLayer.getFeatures(req)
    for pt in pts:
      pt['filtered'] = 0
      self.pointsLayer.updateFeature(pt)
    self.pointsLayer.commitChanges()
    self.updateXsPlot(self.curXsId, False)
    self.updatePointsTable(self.curXsId)
  
  
  def checkXsSelection(self):
    if self.selXsecIds == []:
      q = "There is no selected cross-section. \nClick 'Proceed for all' if you would you like to proceed for all cross-sections or 'Cancel' to manually select some cross-sections"
      choice = QMessageBox.question(None, "No Selected Cross-sections", q, "Proceed for all", "Cancel", "", 0, -1)
      if choice == 0:
        self.selXsecIds = self.xsLayer.allFeatureIds()
        return True
      else:
        return False
    else:
        return True
  
  
  def updateSelectedXsProfile(self): # was updateXsProfile
    '''Creates / updates cross-section points.    
    '''
    if not self.checkXsSelection():
      self.addInfo("")
      return
#     self.addInfo("Selected xss: %s" % str(self.selXsecIds))
    if self.openedDEM:
      cellSize = self.DEM.rasterUnitsPerPixelX()
      dist, ok = QInputDialog.getText(self, 'Set Distance Between Points', 
        '''<html><head/><body><p>Distance between points<br>Raster cell size is: %.2f</p></body></html>''' % cellSize)
      # usun stare punkty, ktore nie sa istotne (markery)
      # tylko co wtedy, gdy zmienia sie przebieg przekroju? wtedy markery pozostaja w zlych miejscach
      # TODO: zrobic warstwe liniowa markerow (linia brzegow i walów. Nurt powinien byc najniższym punktem
      # miedzy markerami 4 i 5). I markery będą określane za pomocą przecięć i profilu wysokościowego tych linii 
      self.deletePoints(self.selXsecIds)
      self.ui.progressBar.setValue(0)
      self.ui.progressBar.setMaximum(len(self.selXsecIds))
      if ok and isNumber(dist):
        self.createXsPointsFromDEM(float(dist))
      self.updateXsPlot(self.selXsecIds[0], False)
      self.updatePointsTable(self.selXsecIds[0])
      self.addInfo("Cross-sections' profiles updated.")
    else:
      msg = 'Updating cross-section(s) failed. Check if a DEM is loaded'
      QMessageBox.warning(self, 'Update Cross-section from DEM', msg)
      return 
    
    
  def createXsPointsFromDEM(self, dist):
    self.pointsLayer.startEditing()
    startTime = time.time()
    for i, id in enumerate(self.selXsecIds):
      
      cur = self.rdb.conn.cursor()
      qry = "SELECT AsText(ST_Line_Interpolate_Equidistant_Points((select the_geom from xsecs where xs_id=%i), %.3f))" % (id, dist)
      cur.execute(qry)
      res = cur.fetchone()[0]
      ptsStrList = res[13:-1].split(",")
      newPtsScript = ""
      curTime =  time.time()-startTime
#       self.addInfo("%.3f\tpoints interpolated " % curTime)
      startTime = time.time()
      # add first and last point of the xs
      req = QgsFeatureRequest()
      req.setFilterExpression( u'"xs_id" = %i' % id )
      xs =self.xsLayer.getFeatures(req).next()
      xsGeom = xs.geometry()
      nrOfVertices = xsGeom.exportToWkt().count(',')
      firstPt = xsGeom.vertexAt(0)
      lastPt = xsGeom.vertexAt(nrOfVertices)
      ptsList = []
      for pt in ptsStrList:
        ptsList.append([float(x) for x in pt.strip().split(" ")])
      ptsList.insert(0, [firstPt.x(), firstPt.y(), 0])
      ptsList.append([lastPt.x(), lastPt.y(), xsGeom.length()])
      curTime =  time.time()-startTime
#       self.addInfo("%.3f\tList of xs's points created" % curTime)
      startTime = time.time()
      
      if self.coverLayer.featureCount():
        allfeatures = {feature.id(): feature for (feature) in self.coverLayer.getFeatures()}
        index = QgsSpatialIndex()
        map(index.insertFeature, allfeatures.values())
        curTime =  time.time()-startTime
#         self.addInfo("%.3f\tSpatial index created" % curTime)
        startTime = time.time()
      
      feats = []
      for floats in ptsList:
        x, y, absc = floats
#         self.addInfo(str(floats))
        if self.openedDEM:
          ident = self.DEM.dataProvider().identify(QgsPoint(x, y), QgsRaster.IdentifyFormatValue)
          if ident.isValid():
            ordin = float(ident.results()[1])
            curTime =  time.time()-startTime
#             self.addInfo("%.3f\tRaster identified" % curTime)
            startTime = time.time()
          else:
            ordin = -9999
        else: # DEM not loaded
          msg = 'Load a DEM before interpolating cross-section\'s points'
          QMessageBox.warning(self, 'Warning!', msg)
          return
        
        if self.coverLayer.featureCount():
          coverCode = -9999
          allAttrs = self.coverLayer.pendingAllAttributesList()
          self.coverLayer.select(allAttrs)
          
          ids = index.intersects(QgsRectangle(x, y, x+0.01, y+0.01)) # just to have a rectangle
          for idPoly in ids:
            f = allfeatures[idPoly]
            if f.geometry().intersects( QgsGeometry.fromPoint(QgsPoint(x, y))):
              coverCode = f[self.currentLandCoverAttr]
              curTime =  time.time()-startTime
#               self.addInfo("%.3f\tLand cover found" % curTime)
              startTime = time.time()
           
        feat = QgsFeature()
#         self.addInfo("id=%i\tx=%.2f\ty=%.2f\tabsc=%.2f\tordin=%.2f\tcover=%s " % (id, x, y, absc, ordin, coverCode))
        feat.setAttributes([NULL, id, x, y, absc, ordin, coverCode, 0, 0, 0, 0, "" ])
        feat.setGeometry(QgsGeometry.fromPoint(QgsPoint(x,y)))
        feats.append(feat)
        
      (res, outFeats) = self.pointsLayer.dataProvider().addFeatures(feats)
      curTime =  time.time()-startTime
#       self.addInfo("%.3f\tFeatures added." % curTime)
      self.ui.progressBar.setValue(i+1)
      qApp.processEvents()

    self.pointsLayer.commitChanges()
    self.updatePointsTable(self.curXsId)


  def addBedPoints(self):
    if not self.rdbLoaded:
      QMessageBox.warning(self, "Import Bed Point", "Load or create a new river database")
      return
    if self.ui.comboBedPoints.count() > 0:
      curInd = self.ui.comboBedPoints.currentIndex()
      lid = self.ui.comboBedPoints.itemData(curInd)
      self.bedPts2Import = self.mapRegistry.mapLayer(lid)
    else:
      QMessageBox.warning(self, "Import Bed Points", "Load a Bed Points layer from QGIS or any OGR layer (i.e. Shapefile)")
      return
    
    # build xs spatial index
    if self.xsLayer.featureCount():
      xss = self.xsLayer.getFeatures()
      xsIndex = QgsSpatialIndex()
      for xs in xss:
        xsIndex.insertFeature(xs)
        
    bedPts = self.bedPts2Import.getFeatures()
    bedPtsCount = self.bedPts2Import.featureCount()
    self.pointsLayer.startEditing()
    
    cur = self.rdb.conn.cursor()
    
    # for each bed point find a nearest xs and a nearest point on that xs
    for i, bedPt in enumerate(bedPts):
      self.ui.progressBar.setValue(int(i/bedPtsCount))
      geom = bedPt.geometry()
      ptWKT = geom.exportToWkt()
      newPt = QgsFeature()
      newPt.setGeometry(geom)
      xsId = xsIndex.nearestNeighbor(geom.asPoint(), 1)[0]
      xs = self.xsLayer.getFeatures(QgsFeatureRequest().setFilterFid(xsId)).next()
      xsLength = xs.geometry().length()
#       self.addInfo("xs_id = %i, l = %.2f" % (xsId, xsLength))
      qry = 'SELECT ST_Line_Locate_Point( (select the_geom from xsecs where xs_id = %i), ST_GeomFromText(\'%s\', %i) )' % (xsId, ptWKT, self.rdb.srid)
      cur.execute(qry)
      m = cur.fetchone()[0] * xsLength
      if m:
        newPt.setAttributes([NULL, xsId, geom.asPoint().x(), geom.asPoint().y(), m, bedPt['elevation'], bedPt['cover_code'], 0, 0, 2, 0, "" ])
#         self.addInfo("Bed Point inserted to DB: absc=%.2f, ordin=%.2f, cover=%s" % (m * xsLength, bedPt['elevation'], bedPt['cover_code']))
      else:
        newPt.setAttributes([NULL, xsId, geom.asPoint().x(), geom.asPoint().y(), -9999, bedPt['elevation'], bedPt['cover_code'], 0, 0, 2, 0, "" ])
#         self.addInfo("Bed Point inserted to DB: %s, absc=%.2f, ordin=%.2f, cover=%s" % (ptWKT, -9999, bedPt['elevation'], bedPt['cover_code']))
      res = self.pointsLayer.addFeature( newPt, alsoUpdateExtent = False )

    del cur
    self.pointsLayer.commitChanges()
    self.pointsLayer.startEditing()

    for xs in self.xsLayer.getFeatures():
      xsId = xs.id()
      req = QgsFeatureRequest()
      req.setFilterExpression( u'"xs_id" = %i and is_node=2' % xsId )
      minBedAbsc, maxBedAbsc = [99999, -99999]
      for pt in self.pointsLayer.getFeatures(req):
        minBedAbsc = min(pt['abscissa'], minBedAbsc)
        maxBedAbsc = max(pt['abscissa'], maxBedAbsc)
      if not minBedAbsc == 99999 and not maxBedAbsc == -99999:
        filter = u'"xs_id"=%i AND "abscissa">=%.4f AND "abscissa"<=%.4f AND NOT "is_node"=2' % (xsId, minBedAbsc, maxBedAbsc)
        self.addInfo("Xs:%i, filter:%s" % (xsId, filter))
        req.setFilterExpression(filter)
        it = self.pointsLayer.getFeatures(req)
        self.pointsLayer.setSelectedFeatures([ f.id() for f in it ])
        self.pointsLayer.deleteSelectedFeatures()
    
    self.pointsLayer.commitChanges()
    self.addInfo("Bed points added.")
    
    
  def exportPointsISOKP(self):
    exportISOKP(self)
  
    
  def cleanMapLayerRegistry(self):
    '''OBSOLETE. Removes RDb layers from QgsMapLayerRegistry.
    '''
    for layerId, layer in self.mapRegistry.mapLayers().iteritems():
      if layer.name() in ['RDb Cross-sections', 'RDb Rivers', 'RDb Levees']:
        self.mapRegistry.removeMapLayer(layerId)

  def createRDbIndexes(self):
    '''Creates indexes for xsecs and points tables
    '''
    cur = self.rdb.conn.cursor()
    qry = 'DROP index "main"."pointsIndex"'
    cur.execute(qry)
    qry = 'CREATE UNIQUE INDEX "main"."pointsIndex" ON "points" ("pt_id" ASC, "xs_id" ASC)'
    cur.execute(qry)
    self.addInfo('Indexes created.')


  def warningMapRegistryCleaned(self):
    msg = 'You just cleaned your map registry! \nYou have to reload Rivergis plugin.'
    QMessageBox.warning(self, 'Warning!', msg)
