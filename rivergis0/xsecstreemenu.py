# -*- coding: utf-8 -*-

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from rivergisdef import *
from qgis.core import *
from qgis.gui import *
from logging_rivergis import *

def isNumber(s):
    try:
        float(s)
        return True
    except ValueError:
        return False


class xsecsTreeMenuXs(QMenu):
  """Menu for Cross-section items"""
  def __init__(self, parent, selXsIds):
    QMenu.__init__(self)
    self.selXsIds = selXsIds
    self.parent = parent
    self.rdb = parent.rdb
    self.iface = self.parent.iface

    #refresh tree
    self.refreshAction=QAction("Refresh Tree",self)
    QObject.connect(self.refreshAction, SIGNAL('triggered()'), self.parent.drawXsecsTree)

    self.zoomMapToSelectedAction=QAction("Zoom to Selected Cross-sections",self)
    QObject.connect(self.zoomMapToSelectedAction, SIGNAL('triggered()'), self.zoomMapToSelected)
    #Simplify selected
    self.simplifySelectedAction=QAction("Simplify Selected Cross-sections",self)
    QObject.connect(self.simplifySelectedAction, SIGNAL('triggered()'), self.simplifySelected)
    #Revert Simplification for Selected Xsections
    self.unSimplifySelectedAction=QAction("Revert Simplification for Selected Cross-sections",self)
    QObject.connect(self.unSimplifySelectedAction, SIGNAL('triggered()'), self.unSimplifySelected)
    #Delete Points filtered out by simplification for Selected Xsections
    self.delSimplifiedSelectedAction=QAction("Delete Points Filtered out by Simplification for Selected Cross-sections",self)
    QObject.connect(self.delSimplifiedSelectedAction, SIGNAL('triggered()'), self.delSimplifiedSelected)
    
    self.createTopologyAction = QAction("Create Topology",self)
    QObject.connect(self.createTopologyAction, SIGNAL('triggered()'), self.parent.createTopology)
    
    self.updateXSectsProfileAction = QAction("Update Cross-section Points from DEM",self)
    QObject.connect(self.updateXSectsProfileAction, SIGNAL('triggered()'), self.parent.updateSelectedXsProfile)
    
    self.addBedPointsAction = QAction("Add Measured Bed Points to Selected Cross-sections",self)
    QObject.connect(self.addBedPointsAction, SIGNAL('triggered()'), self.parent.addBedPoints)
    
    self.deletePtsOfSelectedXssAction = QAction("Delete Points of Selected Cross-sections",self)
    QObject.connect(self.deletePtsOfSelectedXssAction, SIGNAL('triggered()'), self.deletePtsOfSelectedXss)
    
    
    self.createMenu()
        
  def createMenu(self):
    #Refresh Tree
    self.addAction(self.refreshAction)
    self.addSeparator()
    #LoadToQgis
    #self.addAction(self.toQGISAction)
    self.addAction(self.zoomMapToSelectedAction)
    self.addSeparator()
    #Simplify Selected
    self.addAction(self.simplifySelectedAction)
    self.addAction(self.unSimplifySelectedAction)
    self.addAction(self.delSimplifiedSelectedAction)
    self.addSeparator()
    # Create points along selected xsections
    self.addAction(self.createTopologyAction)
    self.addAction(self.updateXSectsProfileAction)
    self.addAction(self.addBedPointsAction)
    self.addAction(self.deletePtsOfSelectedXssAction)
    self.addSeparator()
    #Draw menu
    self.exec_(QCursor.pos())
    
      
  def zoomMapToSelected(self):
    for ident in self.selXsIds:
      self.parent.xsLayer.select(ident)
    self.parent.canvas.zoomToSelected(self.parent.xsLayer)
    

  def simplifySelected(self):
    dist, ok = QInputDialog.getText(self, 'Set RDP Parameter', 
      '''<html><head/><body><p>Set Ramer-Douglas-Peucker Parameter<br/>
      (see <a href="https://en.wikipedia.org/wiki/Ramer%E2%80%93Douglas%E2%80%93Peucker_algorithm">
      <span style=" text-decoration: underline; color:#0000ff;">Wikipedia explanation</span>
      </a>)</p></body></html>''')

    if ok and isNumber(dist):
      self.parent.ui.progressBar.setValue(0)
      self.parent.ui.progressBar.setMaximum(len(self.selXsIds))
      for i, id in enumerate(self.selXsIds):
        xs = Xsection(self.rdb, "", "", id)
        xs.simplify(float(dist))
        self.parent.ui.progressBar.setValue(i+1)
      self.iface.messageBar().clearWidgets()
      self.parent.updateXsPlot(self.selXsIds[0], False)
      self.parent.updatePointsTable(self.selXsIds[0])
    else:
      return 
  
  def unSimplifySelected(self):
    self.parent.unSimplifySelected(self.selXsIds)
    self.parent.updateXsPlot(self.selXsIds[0], False)
    self.parent.updatePointsTable(self.selXsIds[0])
    
  def delSimplifiedSelected(self):
    quit_msg = "Are you sure you want delete points filtered out by Simplification?"
    reply = QMessageBox.question(self, 'Message', 
                     quit_msg, QMessageBox.Yes, QMessageBox.No)

    if reply == QMessageBox.Yes:
      self.parent.deletePointsSimplified(self.selXsIds)
      self.parent.updateXsPlot(self.selXsIds[0], False)
      self.parent.updatePointsTable(self.selXsIds[0])
    else:
      return

  
  def deletePtsOfSelectedXss(self):
    msg = 'Deleteing points of xss: %s' % self.selXsIds
    self.parent.addInfo(msg)
    self.parent.deletePoints(self.selXsIds)
  
    
class xsecsTreeMenuRiv(QMenu):
  """Menu for river items"""
  def __init__(self, parent, selRivIds):
    QMenu.__init__(self)
    self.selRivIds = selRivIds
    self.parent = parent
    self.rdb = parent.rdb
    
    #refresh tree
    self.refreshAction=QAction("Refresh Tree",self)
    QObject.connect(self.refreshAction, SIGNAL('triggered()'), self.parent.drawXsecsTree)
    #Simplify selected
    self.simplifySelectedAction=QAction("Simplify Selected Cross-sections",self)
    QObject.connect(self.simplifySelectedAction, SIGNAL('triggered()'), self.simplifySelected)
    #Revert Simplification for Selected Xsections
    self.unSimplifySelectedAction=QAction("Revert Simplification for Selected Cross-sections",self)
    QObject.connect(self.unSimplifySelectedAction, SIGNAL('triggered()'), self.unSimplifySelected)
    #Delete Points filtered out by simplification for Selected Xsections
    self.delSimplifiedSelectedAction=QAction("Delete Points Filtered out by Simplification for Selected Cross-sections",self)
    QObject.connect(self.delSimplifiedSelectedAction, SIGNAL('triggered()'), self.delSimplifiedSelected)

    self.exportSelectedRivers2NewDBAction=QAction("Export Selected Rivers to New DataBase",self)
    QObject.connect(self.exportSelectedRivers2NewDBAction, SIGNAL('triggered()'), self.exportSelectedRivers2NewDB)

    self.createTopologyAction = QAction("Create Topology",self)
    QObject.connect(self.createTopologyAction, SIGNAL('triggered()'), self.parent.createTopology)
    
    self.updateXSectsProfileAction = QAction("Update Cross-section Points from DEM",self)
    QObject.connect(self.updateXSectsProfileAction, SIGNAL('triggered()'), self.parent.updateSelectedXsProfile)
    
    self.addBedPointsAction = QAction("Add Measured Bed Points to Selected Cross-sections",self)
    QObject.connect(self.addBedPointsAction, SIGNAL('triggered()'), self.parent.addBedPoints)
    
    self.createMenu()
    
  def createMenu(self):
    #Refresh Tree
    self.addAction(self.refreshAction)
    self.addSeparator()
    #Simplify Selected
    self.addAction(self.simplifySelectedAction)
    self.addAction(self.unSimplifySelectedAction)
    self.addAction(self.delSimplifiedSelectedAction)
    self.addSeparator()
    # export
    self.addAction(self.exportSelectedRivers2NewDBAction)
    self.addSeparator()
    self.addAction(self.createTopologyAction)
    self.addAction(self.updateXSectsProfileAction)
    self.addAction(self.addBedPointsAction)
    self.addSeparator()
    
    self.exec_(QCursor.pos())
    
  
  
  def simplifySelected(self):
    dist, ok = QInputDialog.getText(self, 'Set RDP Parameter', 
      '''<html><head/><body><p>Set Ramer-Douglas-Peucker Parameter<br/>
      (see <a href="https://en.wikipedia.org/wiki/Ramer%E2%80%93Douglas%E2%80%93Peucker_algorithm">
      <span style=" text-decoration: underline; color:#0000ff;">Wikipedia explanation</span>
      </a>)</p></body></html>''')

    if ok and isNumber(dist):
      self.parent.ui.progressBar.setValue(0)
#       self.parent.ui.progressBar.setMaximum(len(self.selXsIds))
      for i, id in enumerate(self.selXsIds):
        xs = Xsection(self.rdb, "", "", id)
        xs.simplify(float(dist))
        self.parent.ui.progressBar.setValue(int((i+1)/len(self.selXsIds)*100))
      self.iface.messageBar().clearWidgets()
      self.parent.updateXsPlot(self.selXsIds[0], False)
      self.parent.updatePointsTable(self.selXsIds[0])
    else:
      return 
  
  def unSimplifySelected(self):
    self.rdb.unSimplify(self.selXsIds)
    self.parent.updateXsPlot(self.selXsIds[0], False)
    self.parent.updatePointsTable(self.selXsIds[0])
    
  def delSimplifiedSelected(self):
    quit_msg = "Are you sure you want delete points filtered out by Simplification?"
    reply = QMessageBox.question(self, 'Message', 
                     quit_msg, QMessageBox.Yes, QMessageBox.No)

    if reply == QMessageBox.Yes:
      self.rdb.delSimplified(self.selXsIds)
      self.parent.updateXsPlot(self.selXsIds[0], False)
      self.parent.updatePointsTable(self.selXsIds[0])
    else:
      return
    

#   def updateXSectsProfile(self):
#     if self.parent.openedDEM:
#       cellSize = self.parent.DEM.rasterUnitsPerPixelX()
#       dist, ok = QInputDialog.getText(self, 'Set Distance Between Points', 
#         '''<html><head/><body><p>Distance between points<br>Raster cell size is: %.2f</p></body></html>''' % cellSize)
#       # usun stare punkty, ktore nie sa istotne (markery)
#       # tylko co wtedy, gdy zmienia sie przebieg przekroju? wtedy markery pozostaja w zlych miejscach
#       # TODO: zrobic warstwe liniowa markerow (linia brzegow i walów. Nurt powinien byc najniższym punktem
#       # miedzy markerami 4 i 5). I markery będą określane za pomocą przecięć i profilu wysokościowego tych linii 
#       self.parent.deletePoints(self.selXsIds)
#       
#       if ok and isNumber(dist):
#         self.parent.updateXsProfile(self.selXsIds, float(dist))
#       self.parent.updateXsPlot(self.selXsIds[0], False)
#       self.parent.updatePointsTable(self.selXsIds[0])
#     else:
#       msg = 'Updating cross-section(s) failed. Check if a DEM is loaded'
#       QMessageBox.information(self, 'Update Cross-section from DEM', msg)
#       return 
    
    
  def exportSelectedRivers2NewDB(self):
    s = QSettings()
    lastDir = s.value("rivergis/lastRdbDir", "")
    try:
      dbFilename = QFileDialog.getSaveFileName(self, 'New SQLite database file', directory=lastDir)
    except:
      logging.debug("Create new DB cancelled")
      self.parent.msg("Create new DB cancelled", 0)
      logging.debug("Create new DB cancelled")
      return
    
    if not dbFilename.endswith(".sqlite"):
      dbFilename += ".sqlite"
    if not dbFilename == ".sqlite":
      try:
        s.setValue("rivergis/lastRdb", dbFilename)
        s.setValue("rivergis/lastRdbDir", dirname(dbFilename))
      except:
        logging.debug("Could not create a new river DB")
        self.parent.ui.infoTextBrowser.setHtml("Could not create a new river DB - check the log file.")
    t = ""
    for id in self.selRivIds:
        t += str(id) + " "  
    self.rdb.exportRiversSQLite(dbFilename, self.rdb.srid, self.selRivIds)
    logging.debug("Rivers %s copied" % t)
  
  def addBedPoints(self):
    self.parent.addBedPoints()



