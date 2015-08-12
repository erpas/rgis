# -*- coding: utf-8 -*-

"""
/***************************************************************************
Name                 : RiverGIS
Description          : HEC-RAS tools for QGIS
Date                 : January, 2015
copyright            : (C) 2015 by RiverGIS Group
email                : rpasiok@gmail.com

The content of this file is based on
- DB Manager by Giuseppe Sucameli (2011)
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

from qgis.gui import QgsMessageBar
from qgis.utils import showPluginHelp

from db_manager.db_tree import DBTree

from db_manager.db_plugins.plugin import BaseError, DbError, DBPlugin, Schema, Table
from db_manager.dlg_db_error import DlgDbError

import processing
from _ui_rivergis import Ui_RiverGIS
from hecras2dFunctions import *
from hecras1dFunctions import *
from isokpFunctions import *
from hecrasLoadWsel import WorkerLoadWselHecRas
from createWaterSurfRaster import WorkerCreateWaterSurfRaster



class RiverGIS(QMainWindow):

  def __init__(self, iface, parent=None):
    QMainWindow.__init__(self, parent) #, Qt.WindowStaysOnTopHint)
    self.setAttribute(Qt.WA_DeleteOnClose)
    self.ui = Ui_RiverGIS()
    self.ui.setupUi(self)
    self.tree = DBTree(self)
    self.ui.dock.setWidget(self.tree)
    self.connect(self.tree, SIGNAL("selectedItemChanged"), self.dbItemChanged)
    self.dbItemChanged(None)

    # create status bar
    self.statusBar = QStatusBar(self)
    self.setStatusBar(self.statusBar)

    # MENU
    self.ui.actionImportRiverFromIsokp.triggered.connect(self.importRiverIsokp)
    self.ui.actionCreate2dArea.triggered.connect(self.create2dArea)
    self.ui.actionPreview_2D_Mesh.triggered.connect(self.preview2DMesh)
    self.ui.actionSave_mesh_points_to_HEC_RAS_geometry_file.triggered.connect(self.saveMeshPtsToHecrasGeo)
    self.ui.actionCreate_1d_PostGIS_Tables.triggered.connect(self.create1dPostGisTables)
    self.ui.actionLoad_WSEL_from_HEC_RAS.triggered.connect(self.loadWselHecRasStart)
    self.ui.actionCreate_Water_Surface_Raster.triggered.connect(self.createWaterSurfRaster)
    self.ui.actionCreate_Depths_and_Flood_Range.triggered.connect(self.createDepthAndRange)
    self.ui.actionAbout.triggered.connect(self.about)
    self.ui.actionHelpContents.triggered.connect(self.showRGisHelp)
    self.ui.actionRefresh.triggered.connect(self.refreshItem)

    # toolbar
    self.ui.toolBar = QToolBar("Default", self)
    self.ui.toolBar.setObjectName("DB_ToolBar")
    self.ui.toolBar.addAction( self.ui.actionRefresh )
    self.ui.toolBar.addAction( self.ui.actionImportRiverFromIsokp )
    self.ui.toolBar.addAction( self.ui.actionCreate2dArea )
    self.ui.toolBar.addAction( self.ui.actionLoad_WSEL_from_HEC_RAS )
    self.ui.toolBar.addAction( self.ui.actionCreate_Water_Surface_Raster )
    self.ui.toolBar.addAction( self.ui.actionCreate_Depths_and_Flood_Range )
    self.addToolBar(self.ui.toolBar)

    self.ui.crsWidget.crsChanged.connect(self.updateDefaultCrs)

    # Some info
    self.ui.textEdit.append('<b>Welcome to RiverGIS!</b><br><br>For some operations RiverGIS needs a <b>connection to a PostGIS database</b>. Please, choose a connection and schema from the Connections tree on the left.<br>')
    self.ui.textEdit.append('If you can\'t see any connection under the PostGIS tree, create a new one from menu Layer > Add layer > Add PostGIS layers... <br><br>')
    self.ui.textEdit.append('<b>Loading HEC-RAS 2D results</b> requires a h5py Python package ( http://www.h5py.org ).<br><br>')
    self.iface = iface
    self.mapRegistry = QgsMapLayerRegistry.instance()
    self.rivergisPath = os.path.dirname(__file__)

    # restore the window state
    settings = QSettings()
    self.restoreGeometry( settings.value("/rivergis/mainWindow/geometry", QByteArray(), type=QByteArray ) )
    self.restoreState( settings.value("/rivergis/mainWindow/windowState", QByteArray(), type=QByteArray ) )

  def closeEvent(self, e):
    self.unregisterAllActions()

    # save the window state
    settings = QSettings()
    settings.setValue( "/rivergis/mainWindow/windowState", self.saveState() )
    settings.setValue( "/rivergis/mainWindow/geometry", self.saveGeometry() )

    QMainWindow.closeEvent(self, e)

  def finishUi(self):
    pass
    
  def showHelp(self, page='index.html'):
    helpFile = 'file:///%s/help/%s' % (self.rivergisPath, page)
    QDesktopServices.openUrl(QUrl(helpFile))
  
  def showRGisHelp(self):
    self.showHelp('index.html')

  def updateDefaultCrs(self):
    self.crs = self.ui.crsWidget.crs()
    addInfo(self, '\nDefault CRS changed to: %s\n' % self.crs.authid() )

  def importRiverIsokp(self):
    from dlg_importRiverFromIsokp import *
    addInfo(self, '\n<b>Running Import River Data From ISOKP Database</b>' )
    db = self.tree.currentDatabase()
    if db is None:
      addInfo(self, "No database selected or you are not connected to it.")
      return

    importData = DlgImportRiverFromIsokp(self)
    importData.exec_()


  def create2dArea(self):
    db = self.tree.currentDatabase()
    if db is None:
      QMessageBox.warning(None, "2D Area", "Please, choose a connection and schema.")
      return
    else:
      ras2dCreate2dArea(self)

  def preview2DMesh(self):
    ras2dPreviewMesh(self)

  def saveMeshPtsToHecrasGeo(self):
      ras2dSaveMeshPtsToGeometry(self)

  def create1dPostGisTables(self):
    addInfo(self, '\n<b>Creating PostGIS tables for 1D geometry</b>' )

  def loadWselHecRasStart(self):
    messageBar = self.iface.messageBar().createMessage('Loading max water surface elevation...', )
    progressBar = QProgressBar()
    progressBar.setAlignment(Qt.AlignLeft|Qt.AlignVCenter)
    cancelButton = QPushButton()
    cancelButton.setText('Cancel')
    messageBar.layout().addWidget(progressBar)
    messageBar.layout().addWidget(cancelButton)
    self.iface.messageBar().pushWidget(messageBar, self.iface.messageBar().INFO)
    self.messageBar = messageBar
    self.workerWselHecRas = WorkerLoadWselHecRas(self)
    cancelButton.clicked.connect(self.workerWselHecRas.kill)

    thread = QThread()
    self.workerWselHecRas.moveToThread(thread)
    self.workerWselHecRas.finished.connect(self.loadWselHecRasFinish)
    self.workerWselHecRas.error.connect(self.loadWselError)
    self.workerWselHecRas.progress.connect(progressBar.setValue)
    thread.started.connect(self.workerWselHecRas.run)

    thread.start()
    self.threadWselHecRas = thread


  def loadWselHecRasFinish(self, res):
      if not res == None:
        # processing.load(res['OUTPUT_LAYER'], 'WSEL_temp_points')
        # processing.load(res.dataProvider().dataSourceUri(), 'WSEL_temp_points')
        processing.load(res, 'WSEL_temp_points')
      else:
        addInfo(self, 'Loading max WSEL failed or was cancelled, check the log...')
      self.iface.messageBar().popWidget(self.messageBar)
      self.workerWselHecRas.deleteLater()
      self.threadWselHecRas.quit()
      self.threadWselHecRas.wait()
      self.threadWselHecRas.deleteLater()

  def createWaterSurfRaster(self):
    messageBar = self.iface.messageBar().createMessage('Creating water surface elevation raster...', )
    progressBar = QProgressBar()
    progressBar.setAlignment(Qt.AlignLeft|Qt.AlignVCenter)
    cancelButton = QPushButton()
    cancelButton.setText('Cancel')
    messageBar.layout().addWidget(progressBar)
    messageBar.layout().addWidget(cancelButton)
    self.iface.messageBar().pushWidget(messageBar, self.iface.messageBar().INFO)
    self.messageBar = messageBar
    self.workerCreateWaterSurf = WorkerCreateWaterSurfRaster(self)
    cancelButton.clicked.connect(self.workerCreateWaterSurf.kill)

    thread = QThread()
    self.workerCreateWaterSurf.moveToThread(thread)
    self.workerCreateWaterSurf.finished.connect(self.loadWselHecRasFinish)
    self.workerCreateWaterSurf.error.connect(self.loadWselError)
    self.workerCreateWaterSurf.progress.connect(progressBar.setValue)
    thread.started.connect(self.workerCreateWaterSurf.run)

    thread.start()
    self.threadCreateWaterSurf = thread


  def loadWselError(self, e, exception_string):
    addInfo(self, 'Thread loading WSEL raised an exception:{}'.format(exception_string))
    QgsMessageLog.logMessage('Thread loading WSEL raised an exception:{}\n'.format(exception_string), level=QgsMessageLog.CRITICAL)
    
  def createWaterSurfRaster(self):
    ras2dCreateWaterSurfaceRaster(self)

  def createDepthAndRange(self):
    from dlg_createDepthsAndFloodRange import *
    addInfo(self, '\n<b>Running Create Depths and Flood Range</b>' )
    createDialog = DlgCreateDepthsAndFloodRange(self)
    createDialog.exec_()

  def about(self):
    self.showHelp('index.html')
    
  def refreshItem(self, item=None):
    QApplication.setOverrideCursor(Qt.WaitCursor)
    try:
      item = self.tree.currentItem()
      self.tree.refreshItem(item)  # refresh item children in the db tree
    except BaseError, e:
      DlgDbError.showError(e, self)
      return
    finally:
      QApplication.restoreOverrideCursor()

  def dbItemChanged(self, item):
    QApplication.setOverrideCursor(Qt.WaitCursor)
    try:
      self.reloadButtons()
      # self.refreshTabs()
      self.updateLineEdDB()
    except BaseError, e:
      DlgDbError.showError(e, self)
      return
    finally:
      QApplication.restoreOverrideCursor()

  def updateLineEdDB(self):
    db = self.tree.currentDatabase()
    if db is None:
      #self.infoBar.pushMessage(self.tr("No database selected or you are not connected to it."), QgsMessageBar.INFO, self.iface.messageTimeout())
      return
    self.item  = self.tree.currentItem()
    self.db = db
    self.uri = self.db.uri()
    self.user = self.uri.username()
    self.passwd = self.uri.password()
    self.dbname = self.uri.database()
    self.host = self.uri.host()
    self.schema = self.tree.currentSchema()
    if self.schema:
      self.schName = self.schema.name
    self.schemas = self.db.schemas()
    self.hasSchemas = self.schemas != None
    
    if isinstance(self.item, DBPlugin):
      self.ui.lineEdCurDatabase.setText( self.item.connectionName() )
    elif isinstance(self.item, Schema):
      self.ui.lineEdCurDatabase.setText( self.db.connection().connectionName() )
      self.ui.lineEdCurSchema.setText( self.schName )
    elif isinstance(self.item, Table):
      self.ui.lineEdCurDatabase.setText( self.db.connection().connectionName() )
      self.ui.lineEdCurSchema.setText( self.schName )
    else:
      return


  def reloadButtons(self):
    db = self.tree.currentDatabase()
    if not hasattr(self, '_lastDb'):
      self._lastDb = db

    elif db == self._lastDb:
      return

    # remove old actions
    if self._lastDb != None:
      self.unregisterAllActions()

    # add actions of the selected database
    self._lastDb = db
    if self._lastDb != None:
      self._lastDb.registerAllActions(self)


  def registerAction(self, action, menuName, callback=None):
    pass

  def invokeCallback(self, callback, params=None):
    """ Call a method passing the selected item in the database tree,
            the sender (usually a QAction), the plugin mainWindow and
            optionally additional parameters.

            This method takes care to override and restore the cursor,
            but also catches exceptions and displays the error dialog.
    """
    QApplication.setOverrideCursor(Qt.WaitCursor)
    try:
      if params is None:
        callback( self.tree.currentItem(), self.sender(), self )
      else:
        callback( self.tree.currentItem(), self.sender(), self, *params )

    except BaseError, e:
      # catch database errors and display the error dialog
      DlgDbError.showError(e, self)
      return

    finally:
            QApplication.restoreOverrideCursor()

  def unregisterAction(self, action, menuName):
    if not hasattr(self, '_registeredDbActions'):
      return

    if menuName == None or menuName == "":
      self.removeAction( action )

      if self._registeredDbActions.has_key(menuName):
        if self._registeredDbActions[menuName].count( action ) > 0:
          self._registeredDbActions[menuName].remove( action )

      action.deleteLater()
      return True

    for a in self.menuBar.actions():
      if not a.menu() or a.menu().title() != menuName:
        continue

      menu = a.menu()
      menuActions = menu.actions()

      menu.removeAction( action )
      if menu.isEmpty():  # hide the menu
        a.setVisible(False)

      if self._registeredDbActions.has_key(menuName):
        if self._registeredDbActions[menuName].count( action ) > 0:
          self._registeredDbActions[menuName].remove( action )

        # hide the placeholder if there're no other registered actions
        if len(self._registeredDbActions[menuName]) <= 0:
          for i in range(len(menuActions)):
            if menuActions[i].isSeparator() and menuActions[i].objectName().endswith("_placeholder"):
              menuActions[i].setVisible(False)
              break

      action.deleteLater()
      return True

    return False

  def unregisterAllActions(self):
    if not hasattr(self, '_registeredDbActions'):
      return

    for menuName in self._registeredDbActions:
      for action in list(self._registeredDbActions[menuName]):
        self.unregisterAction( action, menuName )
    del self._registeredDbActions

  def createPgFunctionCreateIndexIfNotExists(self):
      connParams = "dbname = '%s' user = '%s' host = '%s' password = '%s'" % (self.dbname,self.user,self.host,self.passwd)
      conn = psycopg2.connect(connParams)
      cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
      qry = '''CREATE OR REPLACE FUNCTION create_st_index_if_not_exists
        (schema text, t_name text) RETURNS void AS $$
      DECLARE
        full_index_name varchar;
      BEGIN
      full_index_name = t_name || '_' || 'geom_idx';
      IF NOT EXISTS (
          SELECT 1
          FROM   pg_class c
          JOIN   pg_namespace n ON n.oid = c.relnamespace
          WHERE  c.relname = full_index_name
          AND    n.nspname = schema
          ) THEN

          execute 'CREATE INDEX ' || full_index_name || ' ON ' || schema || '.' || t_name || ' USING GIST (geom)';
      END IF;
      END
      $$
      LANGUAGE plpgsql VOLATILE;'''
      cur.execute(qry)
      conn.commit()