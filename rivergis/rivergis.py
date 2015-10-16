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
        if QApplication.overrideCursor():
            QApplication.restoreOverrideCursor()
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
        self.dtms = []
        self.DEBUG = 0

        # create status bar
        self.statusBar = QStatusBar(self)
        self.setStatusBar(self.statusBar)

        # MENU Actions

        # DB
        self.ui.actionRefreshConnections.triggered.connect(self.connChanged)
        self.ui.actionImportRiverFromIsokp.triggered.connect(self.importRiverIsokp)
        # Settings
        self.ui.actionRASDTMSetup.triggered.connect(self.rasDTMSetup)
        self.ui.actionDebugMode.toggled.connect(self.toggleDebugMode)
        self.ui.actionAlwaysOnTop.toggled.connect(self.toggleAlwaysOnTop)
        # RAS Geometry
        # 1D
        self.ui.actionRASCreateRdbTables.triggered.connect(self.rasCreateRdbTables)
        self.ui.actionRASLoadRdbTablesIntoQGIS.triggered.connect(self.rasLoadRdbTablesIntoQGIS)
        self.ui.actionRASImportLayersIntoRdbTables.triggered.connect(self.rasImportLayersIntoRdbTables)
        self.ui.actionRASTopology1D.triggered.connect(self.ras1dStreamCenterlinesTopology)
        self.ui.actionRASLengthsStations.triggered.connect(self.ras1dStreamCenterlinesLengthsStations)
        self.ui.actionCopyStreamCenterlines2Flowpaths.triggered.connect(self.ras1dStreamCenterlines2Flowpaths)
        self.ui.actionRASStreamCenterlineAll.triggered.connect(self.ras1dStreamCenterlineAll)
        self.ui.actionRASXSRiverReachNames.triggered.connect(self.ras1dXSRiverReachNames)
        self.ui.actionRASXSStationing.triggered.connect(self.ras1dXSStationing)
        self.ui.actionRASXSBankStations.triggered.connect(self.ras1dXSBankStations)
        self.ui.actionRASXSDownstreamReachLengths.triggered.connect(self.ras1dXSDownstreamReachLengths)
        self.ui.actionRASXSElevations.triggered.connect(self.ras1dXSElevations)
        self.ui.actionRASXSAll.triggered.connect(self.ras1dXSAll)
        self.ui.actionRASManningsNValues.triggered.connect(self.ras1dManningsNValues)
        self.ui.actionRASLevees.triggered.connect(self.ras1dLevees)
        self.ui.actionRASIneffectiveFlowAreas.triggered.connect(self.ras1dIneffectiveFlowAreas)
        self.ui.actionRASBlockedObstructions.triggered.connect(self.ras1dBlockedObstructions)
        self.ui.actionRASXSUpdateInsertMeasuredPoints.triggered.connect(self.ras1dXSUpdateInsertMeasuredPts)
        self.ui.actionRASBRRiverReachNames.triggered.connect(self.ras1dBRRiverReachNames)
        self.ui.actionRASBRStationing.triggered.connect(self.ras1dBRStationing)
        self.ui.actionRASBRElevations.triggered.connect(self.ras1dBRElevations)
        self.ui.actionRASBRAll.triggered.connect(self.ras1dRASBRAll)
        self.ui.actionRASInlRiverReachNames.triggered.connect(self.ras1dInlRiverReachNames)
        self.ui.actionRASInlStationing.triggered.connect(self.ras1dInlStationing)
        self.ui.actionRASInlElevations.triggered.connect(self.ras1dInlElevations)
        self.ui.actionRASInlAll.triggered.connect(self.ras1dInlAll)
        self.ui.actionRASLatRiverReachNames.triggered.connect(self.ras1dLatRiverReachNames)
        self.ui.actionRASLatStationing.triggered.connect(self.ras1dLatStationing)
        self.ui.actionRASLatElevations.triggered.connect(self.ras1dLatElevations)
        self.ui.actionRASLatAll.triggered.connect(self.ras1dLatAll)
        self.ui.actionRASSAElevationRange.triggered.connect(self.ras1dSAElevationRange)
        self.ui.actionRASAElevationVolumeData.triggered.connect(self.ras1dAElevationVolumeData)
        self.ui.actionRASSATerrainPointExtraction.triggered.connect(self.ras1dSATerrainPointExtraction)
        self.ui.actionRASSAAll.triggered.connect(self.actionRASSAAll)
        self.ui.actionRASSacAssignNearestSA.triggered.connect(self.ras1dSacAssignNearestSA)
        self.ui.actionRASSacElevations.triggered.connect(self.ras1dSacElevations)
        self.ui.actionRASSacAll.triggered.connect(self.ras1dSacAll)
        self.ui.actionRASCreateRASGISImport.triggered.connect(self.ras1dCreateRasGisImport)
        # 2D
        self.ui.actionRASCreate2dAreaPoints.triggered.connect(self.ras2dCreate2dAreaPoints)
        self.ui.actionRASPreview2DMesh.triggered.connect(self.ras2dPreview2DMesh)
        self.ui.actionRASSave2DPointsToHECRASGeometry.triggered.connect(self.ras2dSaveMeshPtsToHecrasGeo)

        # RAS Mapping
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

        # Settings Toolbar
        self.ui.settingsToolBar = QToolBar("Settings", self)
        self.ui.settingsToolBar.setObjectName("Settings_ToolBar")
        self.ui.settingsToolBar.addAction(self.ui.actionRASDTMSetup)

        # 1D HEC-RAS Tables Toolbar
        self.ui.ras1dTablesToolBar = QToolBar("HEC-RAS 1D Tables", self)
        self.ui.ras1dTablesToolBar.setObjectName("RAS1D_Tables_Toolbar")
        self.ui.ras1dTablesToolBar.addAction(self.ui.actionRASCreateRdbTables )
        self.ui.ras1dTablesToolBar.addAction(self.ui.actionRASLoadRdbTablesIntoQGIS)
        self.ui.ras1dTablesToolBar.addAction(self.ui.actionRASImportLayersIntoRdbTables)

        # 1D HEC-RAS Geometry Toolbar
        self.ui.ras1dGeometryToolBar = QToolBar("HEC-RAS 1D Geometry", self)
        self.ui.ras1dGeometryToolBar.setObjectName("RAS1D_Geometry_ToolBar")
        self.ui.ras1dGeometryToolBar.addAction(self.ui.actionRASTopology1D)
        self.ui.ras1dGeometryToolBar.addAction(self.ui.actionRASLengthsStations)
        self.ui.ras1dGeometryToolBar.addAction(self.ui.actionRASStreamCenterlineAll)
        self.ui.ras1dGeometryToolBar.addAction(self.ui.actionRASXSRiverReachNames)
        self.ui.ras1dGeometryToolBar.addAction(self.ui.actionRASXSStationing)
        self.ui.ras1dGeometryToolBar.addAction(self.ui.actionRASXSBankStations)
        self.ui.ras1dGeometryToolBar.addAction(self.ui.actionRASXSDownstreamReachLengths)
        self.ui.ras1dGeometryToolBar.addAction(self.ui.actionRASXSElevations)
        self.ui.ras1dGeometryToolBar.addAction(self.ui.actionRASXSAll)
        self.ui.ras1dGeometryToolBar.addAction(self.ui.actionRASManningsNValues)
        self.ui.ras1dGeometryToolBar.addAction(self.ui.actionRASLevees)
        self.ui.ras1dGeometryToolBar.addAction(self.ui.actionRASIneffectiveFlowAreas)
        self.ui.ras1dGeometryToolBar.addAction(self.ui.actionRASBlockedObstructions)
        self.ui.ras1dGeometryToolBar.addAction(self.ui.actionRASXSUpdateInsertMeasuredPoints)
        self.ui.ras1dGeometryToolBar.addAction(self.ui.actionRASCreateRASGISImport)

        # 1D HEC-RAS Structures Toolbar
        # self.ui.ras1dStructuresToolBar = QToolBar("HEC-RAS 1D Structures", self)
        # self.ui.ras1dStructuresToolBar.setObjectName("RAS1D_Structures_ToolBar")
        # self.ui.ras1dStructuresToolBar.addAction(self.ui.actionRASTopology1D)
        # self.ui.ras1dStructuresToolBar.addAction(self.ui.actionRASLengthsStations)

        # 1D HEC-RAS Storage Areas Toolbar
        self.ui.ras1dSAToolBar = QToolBar("HEC-RAS 1D Storage Areas", self)
        self.ui.ras1dSAToolBar.setObjectName("RAS1D_SA_ToolBar")
        self.ui.ras1dSAToolBar.addAction(self.ui.actionRASAElevationVolumeData)
        self.ui.ras1dSAToolBar.addAction(self.ui.actionRASSATerrainPointExtraction)

        # 2D HEC-RAS Toolbar
        self.ui.ras2dToolBar = QToolBar("HEC-RAS 2D Geometry", self)
        self.ui.ras2dToolBar.setObjectName("RAS2D_ToolBar")
        self.ui.ras2dToolBar.addAction(self.ui.actionRASCreate2dAreaPoints )
        self.ui.ras2dToolBar.addAction(self.ui.actionRASPreview2DMesh )
        self.ui.ras2dToolBar.addAction(self.ui.actionRASSave2DPointsToHECRASGeometry )

        # HEC-RAS Mapping Toolbar
        self.ui.rasMappingToolBar = QToolBar("HEC-RAS Flood Mapping", self)
        self.ui.rasMappingToolBar.setObjectName("RASMAP_ToolBar")
        self.ui.rasMappingToolBar.addAction(self.ui.actionRASImportRasData )
        self.ui.rasMappingToolBar.addAction(self.ui.actionRASWaterSurfaceGeneration)
        self.ui.rasMappingToolBar.addAction(self.ui.actionRASFloodplainDelineation)

        self.addToolBar(self.ui.dbToolBar)
        self.addToolBar(self.ui.settingsToolBar)
        self.addToolBar(self.ui.ras1dTablesToolBar)
        self.addToolBar(self.ui.ras1dGeometryToolBar)
        # self.addToolBar(self.ui.ras1dStructuresToolBar)
        self.addToolBar(self.ui.ras1dSAToolBar)
        self.addToolBar(self.ui.ras2dToolBar)
        self.addToolBar(self.ui.rasMappingToolBar)

        self.ui.crsWidget.crsChanged.connect(self.updateDefaultCrs)
        self.ui.connsCbo.activated.connect(self.connChanged)
        self.ui.schemasCbo.activated.connect(self.schemaChanged)

        # Some info
        self.ui.textEdit.append('<b>Welcome to RiverGIS!</b><br><br>Please, start with choosing a <b>connection to a PostGIS database and a schema</b> from the above lists.')
        self.ui.textEdit.append('If you can\'t see any connection, create a new one from menu Layer > Add layer > Add PostGIS layers... <br>')
        self.ui.textEdit.append('Loading HEC-RAS results requires a h5py Python package ( http://www.h5py.org ).')
        self.ui.textEdit.append('<br>----------------------------------------------------------------------------')

        # restore the window state
        settings = QSettings()
        self.restoreGeometry(settings.value("/rivergis/mainWindow/geometry", QByteArray(), type=QByteArray ))
        self.restoreState(settings.value("/rivergis/mainWindow/windowState", QByteArray(), type=QByteArray ))

        # get PostGIS connections details and populate connections' combo
        self.connChanged()

        # set project CRS as a default projection
        self.ui.crsWidget.setCrs(self.iface.mapCanvas().mapRenderer().destinationCrs())
        self.updateDefaultCrs()

    def closeEvent(self, e):
        # save the window state
        settings = QSettings()
        settings.setValue("/rivergis/mainWindow/windowState", self.saveState())
        settings.setValue("/rivergis/mainWindow/geometry", self.saveGeometry())
        settings.setValue("/rivergis/mainWindow/flags", self.windowFlags())

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

        # close any existing connection to a river database
        if self.rdb:
            self.addInfo("Closing existing connection to {0}@{1} river database".format(
                self.rdb.dbname, self.rdb.host))
            self.rdb.disconnect_pg()
            self.rdb = None

        # create a new connection to river database
        self.rdb = rivdb.RiverDatabase(self, self.database, self.host, self.port, self.user, self.passwd)
        self.rdb.SRID = int(self.crs.postgisSrid())
        self.rdb.connect_pg()
        self.rdb.create_spatial_index()
        self.addInfo('Created connection to river database: {0}@{1}'.format(
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
        self.rdb.register.clear()
        if not self.ui.schemasCbo.currentText() == '':
            self.schema = self.ui.schemasCbo.currentText()
            self.addInfo('Current DB schema is: %s' % self.schema)
            # change river database parameters
            self.rdb.SCHEMA = self.schema
            self.rdb.register_existing(heco)
            reg = [self.rdb.register[k].name for k in sorted(self.rdb.register.keys())]
            if self.DEBUG:
                self.addInfo('Objects registered in the database:<br>  {0}'.format(
                    '<br>  '.join(reg)))
                self.addInfo('You can load them now using RAS Geometry > Load River Database Tables Into QGIS')
            else:
                self.addInfo('There are some objects registered in the database.')

    def importRiverIsokp(self):
        from dlg_importRiverFromIsokp import DlgImportRiverFromIsokp
        self.addInfo('\n<b>Running Import River Data From ISOKP Database</b>' )
        if self.curConnName is None:
            self.addInfo("No database selected or you are not connected to it.")
            return

        importData = DlgImportRiverFromIsokp(self)
        importData.exec_()

    # 1D HEC-RAS Geometry Functions

    def rasDTMSetup(self):
        from dlg_dtmSetup import DlgDTMSetup
        dlg = DlgDTMSetup(self)
        dlg.exec_()

    def toggleDebugMode(self):
        if self.ui.actionDebugMode.isChecked():
            self.DEBUG = 1
        else:
            self.DEBUG = 0

    def toggleAlwaysOnTop(self):
        if self.ui.actionAlwaysOnTop.isChecked():
            flags = self.windowFlags()
            self.setWindowFlags(flags | Qt.CustomizeWindowHint | Qt.WindowStaysOnTopHint)
        else:
            flags = self.windowFlags()
            self.setWindowFlags(flags & ~Qt.CustomizeWindowHint & ~Qt.WindowStaysOnTopHint)
        self.show()

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
        """Import chosen layers into PostGIS database."""
        from dlg_rasImportDataIntoRasTables import DlgImportDataIntoRasTables
        self.addInfo("<br><b>Import data into RAS PostGIS tables...</b>")
        if not self.curConnName or not self.schema:
            self.addInfo("No PostGIS database or schema selected. Choose a connection and schema.")
            return

        importData = DlgImportDataIntoRasTables(self)
        importData.exec_()

    def ras1dStreamCenterlinesTopology(self):
        from ras1dFunctions import ras1dStreamCenterlineTopology
        ras1dStreamCenterlineTopology(self)

    def ras1dStreamCenterlines2Flowpaths(self):
        from ras1dFunctions import ras1dStreamCenterlines2Flowpaths
        ras1dStreamCenterlines2Flowpaths(self)

    def ras1dStreamCenterlinesLengthsStations(self):
        from ras1dFunctions import ras1dStreamCenterlineLengthsStations
        ras1dStreamCenterlineLengthsStations(self)

    def ras1dStreamCenterlineAll(self):
        from ras1dFunctions import ras1dStreamCenterlineAll
        ras1dStreamCenterlineAll(self)

    def ras1dXSRiverReachNames(self):
        from ras1dFunctions import ras1dXSRiverReachNames
        ras1dXSRiverReachNames(self)

    def ras1dXSStationing(self):
        from ras1dFunctions import ras1dXSStationing
        ras1dXSStationing(self)

    def ras1dXSBankStations(self):
        from ras1dFunctions import ras1dXSBankStations
        ras1dXSBankStations(self)

    def ras1dXSDownstreamReachLengths(self):
        from ras1dFunctions import ras1dXSDownstreamLengths
        ras1dXSDownstreamLengths(self)

    def ras1dXSElevations(self):
        from ras1dFunctions import ras1dXSElevations
        ras1dXSElevations(self)

    def ras1dXSAll(self):
        from ras1dFunctions import ras1dXSAll
        ras1dXSAll(self)

    def ras1dManningsNValues(self):
        from ras1dFunctions import ras1dXSExtractMannings
        ras1dXSExtractMannings(self)

    def ras1dLevees(self):
        from ras1dFunctions import ras1dLevees
        ras1dLevees(self)

    def ras1dIneffectiveFlowAreas(self):
        from ras1dFunctions import ras1dIneffective
        ras1dIneffective(self)

    def ras1dBlockedObstructions(self):
        from ras1dFunctions import ras1dObstructions
        ras1dObstructions(self)

    def ras1dXSUpdateInsertMeasuredPts(self):
        from ras1dFunctions import ras1dXSUpdateInsertMeasuredPts
        ras1dXSUpdateInsertMeasuredPts(self)

    def ras1dBRRiverReachNames(self):
        pass

    def ras1dBRStationing(self):
        pass

    def ras1dBRElevations(self):
        pass

    def ras1dRASBRAll(self):
        pass

    def ras1dInlRiverReachNames(self):
        pass

    def ras1dInlStationing(self):
        pass

    def ras1dInlElevations(self):
        pass

    def ras1dInlAll(self):
        pass
    
    def ras1dLatRiverReachNames(self):
        pass
    
    def ras1dLatStationing(self):
        pass
    
    def ras1dLatElevations(self):
        pass
    
    def ras1dLatAll(self):
        pass

    def ras1dSAElevationRange(self):
        pass

    def ras1dSATerrainPointExtraction(self):
        from ras1dFunctions import ras1dSAElevations
        ras1dSAElevations(self)

    def ras1dAElevationVolumeData(self):
        from ras1dFunctions import ras1dSAVolumeData
        ras1dSAVolumeData(self)

    def actionRASSAAll(self):
        pass
    
    def ras1dSacAssignNearestSA(self):
        pass
    
    def ras1dSacElevations(self):
        pass
    
    def ras1dSacAll(self):
        pass
    
    def ras1dCreateRasGisImport(self):
        from ras1dFunctions import ras1dCreateRasGisImportFile
        ras1dCreateRasGisImportFile(self)

    # 2D HEC-RAS Geometry Functions

    def ras2dCreate2dAreaPoints(self):
        from ras2dFunctions import ras2dCreate2dPoints
        ras2dCreate2dPoints(self)

    def ras2dPreview2DMesh(self):
        if self.rdb.SCHEMA is '':
            QMessageBox.warning(None, "Preview 2D Area", "Please, choose a connection and schema.")
            return
        from ras2dFunctions import ras2dPreviewMesh
        ras2dPreviewMesh(self)

    def ras2dSaveMeshPtsToHecrasGeo(self):
        from ras2dFunctions import ras2dSaveMeshPtsToGeometry
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
        dialog = DlgRasFloodplainDelineation(self)
        dialog.exec_()

    def about(self):
        self.showHelp('index.html')
