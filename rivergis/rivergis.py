# -*- coding: utf-8 -*-

"""
/***************************************************************************
Name                 : RiverGIS
Description          : HEC-RAS tools for QGIS
Date                 : January, 2015
copyright            : (C) 2015 by RiverGIS Group
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
from qgis.core import *
from qgis.utils import *

import processing # TODO: try to not use the processing
from ui._ui_rivergis import Ui_RiverGIS
import river_database as rivdb
import hecobjects as heco


class RiverGIS(QMainWindow):

    def __init__(self, iface, parent=None):
        QMainWindow.__init__(self, parent) #, Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.ui = Ui_RiverGIS()
        self.ui.setupUi(self)
        self.conn = None
        self.curConnName = None
        self.schema = None
        self.passwd = None
        self.rdb = None
        self.iface = iface
        self.mapRegistry = QgsMapLayerRegistry.instance()
        self.rivergisPath = os.path.dirname(__file__)

        self.DEBUG = 1

        # create status bar
        self.statusBar = QStatusBar(self)
        self.setStatusBar(self.statusBar)

        # MENU Actions

        # DB
        self.ui.actionRefreshConnections.triggered.connect(self.connChanged)
        self.ui.actionImportRiverFromIsokp.triggered.connect(self.importRiverIsokp)
        # RAS Geometry
        # 1D
        self.ui.actionRASCreateRdbTables.triggered.connect(self.rasCreateRdbTables)
        self.ui.actionRASLoadRdbTablesIntoQGIS.triggered.connect(self.rasLoadRdbTablesIntoQGIS)
        self.ui.actionRASImportLayersIntoRdbTables.triggered.connect(self.rasImportLayersIntoRdbTables)
        self.ui.actionRASTopology1D.triggered.connect(self.rasTopology1D)
        self.ui.actionRASLengthsStations.triggered.connect(self.rasLengthsStations)
        self.ui.actionRASCenterlineElevations.triggered.connect(self.rasCenterlineElevations)
        self.ui.actionRASStreamCenterlineAll.triggered.connect(self.rasStreamCenterlineAll)
        self.ui.actionRASXSRiverReachNames.triggered.connect(self.rasXSRiverReachNames)
        self.ui.actionRASXSStationing.triggered.connect(self.rasXSStationing)
        self.ui.actionRASXSBankStations.triggered.connect(self.rasXSBankStations)
        self.ui.actionRASXSDownstreamReachLengths.triggered.connect(self.rasXSDownstreamReachLengths)
        self.ui.actionRASXSElevations.triggered.connect(self.rasXSElevations)
        self.ui.actionRASXSAll.triggered.connect(self.rasXSAll)
        self.ui.actionRASManningsNValues.triggered.connect(self.rasManningsNValues)
        self.ui.actionRASLevees.triggered.connect(self.rasLevees)
        self.ui.actionRASIneffectiveFlowAreas.triggered.connect(self.rasIneffectiveFlowAreas)
        self.ui.actionRASBlockedObstructions.triggered.connect(self.rasBlockedObstructions)
        self.ui.actionRASFlipXSDirection.triggered.connect(self.rasFlipXSDirection)
        self.ui.actionRASExport1DRASData.triggered.connect(self.rasExport1DRasData)
        # 2D
        self.ui.actionRASCreate2dArea.triggered.connect(self.rasCreate2dArea)
        self.ui.actionRASPreview2DMesh.triggered.connect(self.rasPreview2DMesh)
        self.ui.actionRASSaveMeshPointsToHECRASGeometry.triggered.connect(self.rasSaveMeshPtsToHecrasGeo)
        self.ui.actionRASImportRasData.triggered.connect(self.rasImportRasDataStart)
        self.ui.actionRASWaterSurfaceGeneration.triggered.connect(self.rasWaterSurfaceGeneration)
        self.ui.actionRASFloodplainDelineation.triggered.connect(self.rasFloodplainDelineation)
        self.ui.actionAbout.triggered.connect(self.about)
        self.ui.actionHelpContents.triggered.connect(self.showRGisHelp)

        # toolbars

        # River database toolbar
        self.ui.dbToolBar = QToolBar("River Database", self)
        self.ui.dbToolBar.setObjectName("Rdb_ToolBar")
        self.ui.dbToolBar.addAction(self.ui.actionRefreshConnections)

        # 1D HEC-RAS Toolbar
        self.ui.ras1dToolBar = QToolBar("HEC-RAS 1D Geometry", self)
        self.ui.ras1dToolBar.setObjectName("RAS1D_ToolBar")
        self.ui.ras1dToolBar.addAction(self.ui.actionRASCreateRdbTables )
        self.ui.ras1dToolBar.addAction(self.ui.actionRASLoadRdbTablesIntoQGIS)
        self.ui.ras1dToolBar.addAction(self.ui.actionRASImportLayersIntoRdbTables)

        # 2D HEC-RAS Toolbar
        self.ui.ras2dToolBar = QToolBar("HEC-RAS 2D Geometry", self)
        self.ui.ras2dToolBar.setObjectName("RAS2D_ToolBar")
        self.ui.ras2dToolBar.addAction(self.ui.actionRASCreate2dArea )

        # HEC-RAS Mapping Toolbar
        self.ui.rasMappingToolBar = QToolBar("HEC-RAS Flood Mapping", self)
        self.ui.rasMappingToolBar.setObjectName("RASMAP_ToolBar")
        self.ui.rasMappingToolBar.addAction(self.ui.actionRASImportRasData )
        self.ui.rasMappingToolBar.addAction(self.ui.actionRASWaterSurfaceGeneration)
        self.ui.rasMappingToolBar.addAction(self.ui.actionRASFloodplainDelineation)

        self.addToolBar(self.ui.dbToolBar)
        self.addToolBar(self.ui.ras1dToolBar)
        self.addToolBar(self.ui.ras2dToolBar)
        self.addToolBar(self.ui.rasMappingToolBar)

        self.ui.crsWidget.crsChanged.connect(self.updateDefaultCrs)
        self.ui.connsCbo.activated.connect(self.connChanged)
        self.ui.schemasCbo.activated.connect(self.schemaChanged)

        # Some info
        self.ui.textEdit.append('<b>Welcome to RiverGIS!</b><br><br>Please, start with choosing a <b>connection to a PostGIS database and a schema</b> from the above lists.')
        self.ui.textEdit.append('If you can\'t see any connection, create a new one from menu Layer > Add layer > Add PostGIS layers... <br>')
        self.ui.textEdit.append('<b>Loading HEC-RAS 2D results</b> requires a h5py Python package ( http://www.h5py.org ).')
        self.ui.textEdit.append('<br>----------------------------------------------------------------------------')

        # restore the window state
        settings = QSettings()
        self.restoreGeometry( settings.value("/rivergis/mainWindow/geometry", QByteArray(), type=QByteArray ) )
        self.restoreState( settings.value("/rivergis/mainWindow/windowState", QByteArray(), type=QByteArray ) )

        # get PostGIS connections details and populate connections' combo
        self.connChanged()

        # set project CRS as a default projection
        self.ui.crsWidget.setCrs(self.iface.mapCanvas().mapRenderer().destinationCrs())
        self.updateDefaultCrs()

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

    def addInfo(self, text):
        self.ui.textEdit.append(text)

    def updateDefaultCrs(self):
        self.crs = self.ui.crsWidget.crs()
        if self.rdb:
            self.rdb.SRID = int(self.crs.postgisSrid())
        self.addInfo('\nDefault CRS is: %s' % self.crs.authid() )

    # Database Functions

    def connChanged(self):
        s = QSettings()
        s.beginGroup('/PostgreSQL/connections')
        connsNames = s.childGroups()
        self.curConnName = self.ui.connsCbo.currentText()
        self.ui.connsCbo.clear()
        self.ui.connsCbo.addItem('')
        for conn in connsNames:
            self.ui.connsCbo.addItem(conn)
        try:
            i = connsNames.index(self.curConnName) + 1
        except ValueError:
            i = 0
        self.ui.connsCbo.setCurrentIndex(i)
        if self.ui.connsCbo.currentIndex() == 0:
            return
        connName = self.ui.connsCbo.currentText()
        s.endGroup()
        s.beginGroup('/PostgreSQL/connections/%s' % connName)
        self.host = s.value('host')
        self.port = s.value('port')
        self.database = s.value('database')
        self.user = s.value('username')
        self.passwd = s.value('password')
        # self.sslmode = s.value('sslmode')
        # self.connParams = "host='%s' port='%s' dbname='%s' user='%s' password='%s'" % \
        #                          (self.host,self.port,self.database,self.user,self.passwd)
        # sslmodesList = [0,'disable', 'allow', 'prefer', 'require']
        # if self.sslmode:
        #     self.connParams += " sslmode='%s'" % sslmodesList[self.sslmode]
        # self.conn = psycopg2.connect(self.connParams)
        # self.addInfo('Current DB connection is: %s' % self.curConnName)

        # close any existing connection to river database
        if self.rdb:
            self.addInfo("Closing existing connection to {0}@{1} river database".format( \
                self.rdb.dbname, self.rdb.host))
            self.rdb.disconnect_pg()
            self.rdb = None
        # create a new connection to river database
        self.rdb = rivdb.RiverDatabase(self, self.database, self.host, self.port, self.user, self.passwd)
        self.rdb.SCHEMA = 'start'
        self.rdb.SRID = int(self.crs.postgisSrid())
        self.rdb.connect_pg()
        self.rdb.create_spatial_index()
        self.addInfo('Created connection to river database: {0}@{1}'.format( \
            self.rdb.dbname, self.rdb.host))

        # refresh schemas combo
        schemaName = self.ui.schemasCbo.currentText()
        qry = "SELECT nspname FROM pg_namespace WHERE nspname !~ '^pg_' AND nspname != 'information_schema' ORDER BY nspname"
        schemas = self.rdb.run_query(qry,fetch=True)
        self.ui.schemasCbo.clear()
        self.ui.schemasCbo.addItem('')
        for schema in schemas:
            self.ui.schemasCbo.addItem(schema[0])
        schemaExists = self.ui.schemasCbo.findText(schemaName)
        if schemaExists:
            self.ui.schemasCbo.setCurrentIndex(schemaExists)
        self.schemaChanged()

    def schemaChanged(self):
        if not self.ui.schemasCbo.currentText() == '':
            self.schema = self.ui.schemasCbo.currentText()
            self.addInfo('Current DB schema is: %s' % self.schema)
            # change river database parameters
            self.rdb.SCHEMA = self.schema
            self.rdb.register_existing(heco)
            # self.rdb.load_registered()
            reg = [self.rdb.register[k].name for k in sorted(self.rdb.register.keys())]
            self.addInfo('Objects registered in the database:\n  {0}'.format( \
            '\n  '.join(reg)))
            self.addInfo('You can load them now using RAS Geometry > Load River Database Tables Into QGIS')

    def importRiverIsokp(self):
        from dlg_importRiverFromIsokp import DlgImportRiverFromIsokp
        self.addInfo('\n<b>Running Import River Data From ISOKP Database</b>' )
        if self.curConnName is None:
            self.addInfo("No database selected or you are not connected to it.")
            return

        importData = DlgImportRiverFromIsokp(self)
        importData.exec_()

    # 1D HEC-RAS Geometry Functions

    def rasCreateRdbTables(self):
        from dlg_rasCreateRasLayers import DlgCreateRasLayers
        dlg = DlgCreateRasLayers(self)
        dlg.exec_()

    def rasLoadRdbTablesIntoQGIS(self):
        self.rdb.register_existing(heco)
        self.rdb.refresh_uris()
        if self.DEBUG:
            self.addInfo('Layers sources after refresh_uris:\n    {0}'.format('\n    '.join(self.rdb.uris)))
        self.rdb.load_registered()

    def rasImportLayersIntoRdbTables(self):
        '''
        Imports chosen layers into PostGIS database.
        '''
        from dlg_rasImportDataIntoRasTables import DlgImportDataIntoRasTables
        self.addInfo("<br><b>Import data into RAS PostGIS tables...</b>")
        if not self.curConnName or not self.schema:
            self.addInfo("No PostGIS database or schema selected. Choose a connection and schema.")
            return

        importData = DlgImportDataIntoRasTables(self)
        importData.exec_()

    def rasTopology1D(self):
        from ras1dFunctions import ras1dTopology
        ras1dTopology(self)

    def rasLengthsStations(self):
        from ras1dFunctions import ras1dLengthsStations
        ras1dLengthsStations(self)

    def rasCenterlineElevations(self):
        from ras1dFunctions import ras1dCenterlineElevations
        ras1dCenterlineElevations(self)

    def rasStreamCenterlineAll(self):
        from ras1dFunctions import ras1dStreamCenterlineAll
        ras1dStreamCenterlineAll(self)

    def rasXSRiverReachNames(self):
        from ras1dFunctions import ras1dXSRiverReachNames
        ras1dXSRiverReachNames(self)

    def rasXSStationing(self):
        from ras1dFunctions import ras1dXSStationing
        ras1dXSStationing(self)

    def rasXSBankStations(self):
        from ras1dFunctions import ras1dXSBankStations
        ras1dXSBankStations(self)

    def rasXSDownstreamReachLengths(self):
        from ras1dFunctions import ras1dXSDownstreamLengths
        ras1dXSDownstreamLengths(self)

    def rasXSElevations(self):
        from ras1dFunctions import ras1dXSElevations
        ras1dXSElevations(self)

    def rasXSAll(self):
        from ras1dFunctions import ras1dXSAll
        ras1dXSAll(self)

    def rasManningsNValues(self):
        pass

    def rasLevees(self):
        pass

    def rasIneffectiveFlowAreas(self):
        pass

    def rasBlockedObstructions(self):
        pass

    def rasFlipXSDirection(self):
        pass

    def rasExport1DRasData(self):
        pass

    # 2D HEC-RAS Geometry Functions

    def rasCreate2dArea(self):
        if self.curConnName is '' or self.schema is '':
            QMessageBox.warning(None, "2D Area", "Please, choose a connection and schema.")
            return
        else:
            from dlg_ras2dAreaMesh import DlgRasCreate2dFlowAreas
            self.addInfo('<br><b>Running Create 2D Flow Areas</b>' )
            dlg = DlgRasCreate2dFlowAreas(self)
            dlg.exec_()

    def rasPreview2DMesh(self):
        if self.curConnName is '' or self.schema is '':
            QMessageBox.warning(None, "Preview 2D Area", "Please, choose a connection and schema.")
            return
        from ras2dPreviewMesh import ras2dPreviewMesh
        ras2dPreviewMesh(self)

    def rasSaveMeshPtsToHecrasGeo(self):
        from ras2dSaveMeshPtsToGeometry import ras2dSaveMeshPtsToGeometry
        ras2dSaveMeshPtsToGeometry(self)

    # RAS Mapping function

    def rasImportRasDataStart(self):
        from rasImportRasData import WorkerRasImportRasData
        self.workerWselHecRas = WorkerRasImportRasData(self)

        thread = QThread()
        self.workerWselHecRas.moveToThread(thread)
        self.workerWselHecRas.finished.connect(self.rasImportRasDataFinish)
        self.workerWselHecRas.error.connect(self.loadWselError)
        thread.started.connect(self.workerWselHecRas.run)
        thread.start()
        self.threadWselHecRas = thread

    def rasImportRasDataFinish(self, res):
            if not res == None:
                # processing.load(res['OUTPUT_LAYER'], 'WSEL_temp_points')
                # processing.load(res.dataProvider().dataSourceUri(), 'WSEL_temp_points')
                processing.load(res, 'WSEL_temp_points')
            else:
                self.addInfo('Loading max WSEL failed or was cancelled, check the log...')

            self.workerWselHecRas.deleteLater()
            self.threadWselHecRas.quit()
            self.threadWselHecRas.wait()
            self.threadWselHecRas.deleteLater()

    def loadWselError(self, e, exception_string):
        self.addInfo('Thread loading WSEL raised an exception:{}'.format(exception_string))
        QgsMessageLog.logMessage('Thread loading WSEL raised an exception:{}\n'.format(exception_string), level=QgsMessageLog.CRITICAL)

    def rasWaterSurfaceGeneration(self):
        from dlg_rasWaterSurfaceGeneration import DlgRasWaterSurfaceGeneration
        self.addInfo('<br><b>Running Create Water Surface Raster</b>' )
        dlg = DlgRasWaterSurfaceGeneration(self)
        dlg.exec_()

    def rasFloodplainDelineation(self):
        from dlg_rasFloodplainDelineation import DlgRasFloodplainDelineation
        self.addInfo('\n<b>Running floodplain delineation.</b>' )
        dialog = DlgRasFloodplainDelineation(self)
        dialog.exec_()

    def about(self):
        self.showHelp('index.html')

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
            if menu.isEmpty():    # hide the menu
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

