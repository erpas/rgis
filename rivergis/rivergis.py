# -*- coding: utf-8 -*-

"""
/***************************************************************************
Name                 : RiverGIS
Description          : HEC-RAS tools for QGIS
Date                 : December, 2015
copyright            : (C) 2015 by RiverGIS Group
email                : rpasiok@gmail.com, damnback333@gmail.com
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
from __future__ import absolute_import
from builtins import range
import os
import json

from qgis.PyQt import uic
from qgis.PyQt.QtCore import QByteArray, QSettings, Qt, QUrl
from qgis.PyQt.QtWidgets import QMainWindow, QMenu, QToolBar, QAction, QToolButton, QInputDialog, QApplication
from qgis.PyQt.QtGui import QDesktopServices
from qgis.core import QgsAuthMethodConfig, QgsApplication

from . import river_database as rivdb
from . import hecobjects as heco
from . import ras1dFunctions as r1d
from . import ras2dFunctions as r2d


class RiverGIS(QMainWindow):

    OPT_GENERAL, OPT_RDB, OPT_DTM = list(range(3))

    def __init__(self, iface, parent=None):
        QMainWindow.__init__(self, parent)
        if QApplication.overrideCursor():
            QApplication.restoreOverrideCursor()
        self.setAttribute(Qt.WA_DeleteOnClose)
        tdir = os.path.dirname(os.path.realpath(__file__))
        uif = os.path.join(tdir, "ui", "ui_rivergis.ui")
        self.ui = uic.loadUi(uif, self)
        self.conn = None
        self.curConnName = None
        self.schema = None
        self.passwd = None
        self.rdb = None
        self.iface = iface
        # self.mapRegistry = QgsMapLayerRegistry.instance()
        self.rivergisPath = os.path.dirname(__file__)
        self.dtms = []
        # restore settings
        self.readSettings()
        self.menus = self.ui.menubar.findChildren(QMenu)
        self.toolbars = self.findChildren(QToolBar)

        # MENU Actions

        # DB
        self.ui.actionRefreshConnections.triggered.connect(self.connChanged)
        self.ui.actionCreateNewSchema.triggered.connect(self.dbCreateSchema)
        self.ui.actionDeleteSchema.triggered.connect(self.dbDeleteSchema)
        self.ui.actionRASCreateRdbTables.triggered.connect(self.rasCreateRdbTables)
        self.ui.actionRASLoadRdbTablesIntoQGIS.triggered.connect(self.rasLoadRdbTablesIntoQGIS)
        self.ui.actionRASImportLayersIntoRdbTables.triggered.connect(self.rasImportLayersIntoRdbTables)
        # Settings
        self.ui.actionOptions.triggered.connect(self.options)
        self.ui.actionRestoreDefaultOptions.triggered.connect(lambda: self.readSettings(defaults=True))
        # RAS Geometry
        # 1D
        self.ui.actionRASTopology1D.triggered.connect(lambda: r1d.ras1dStreamCenterlineTopology(self))
        self.ui.actionRASLengthsStations.triggered.connect(lambda: r1d.ras1dStreamCenterlineLengthsStations(self))
        self.ui.actionCopyStreamCenterlines2Flowpaths.triggered.connect(lambda: r1d.ras1dStreamCenterlines2Flowpaths(self))
        self.ui.actionRASStreamCenterlineAll.triggered.connect(lambda: r1d.ras1dStreamCenterlineAll(self))
        self.ui.actionRASXSRiverReachNames.triggered.connect(lambda: r1d.ras1dXSRiverReachNames(self))
        self.ui.actionRASXSStationing.triggered.connect(lambda: r1d.ras1dXSStationing(self))
        self.ui.actionRASXSBankStations.triggered.connect(lambda: r1d.ras1dXSBankStations(self))
        self.ui.actionRASXSDownstreamReachLengths.triggered.connect(lambda: r1d.ras1dXSDownstreamLengths(self))
        self.ui.actionRASXSElevations.triggered.connect(lambda: r1d.ras1dXSElevations(self))
        self.ui.actionRASXSAll.triggered.connect(lambda: r1d.ras1dXSAll(self))
        self.ui.actionRASHealLanduseGeometries.triggered.connect(lambda: r1d.ras1dHealLanduseGeoms(self))
        self.ui.actionRASManningsNValues.triggered.connect(lambda: r1d.ras1dXSExtractMannings(self))
        self.ui.actionRASLevees.triggered.connect(lambda: r1d.ras1dLevees(self))
        self.ui.actionRASIneffectiveFlowAreas.triggered.connect(lambda: r1d.ras1dIneffective(self))
        self.ui.actionRASBlockedObstructions.triggered.connect(lambda: r1d.ras1dObstructions(self))
        self.ui.actionRASXSUpdateInsertMeasuredPoints.triggered.connect(lambda: r1d.ras1dXSUpdateInsertMeasuredPts(self))
        self.ui.actionRASBRRiverReachNames.triggered.connect(lambda: r1d.ras1dBRRiverReachNames(self))
        self.ui.actionRASBRStationing.triggered.connect(lambda: r1d.ras1dBRStationing(self))
        self.ui.actionRASBRElevations.triggered.connect(lambda: r1d.ras1dBRElevations(self))
        self.ui.actionRASBRAll.triggered.connect(lambda: r1d.ras1dRASBRAll(self))
        self.ui.actionRASInlRiverReachNames.triggered.connect(lambda: r1d.ras1dISRiverReachNames(self))
        self.ui.actionRASInlStationing.triggered.connect(lambda: r1d.ras1dISStationing(self))
        self.ui.actionRASInlElevations.triggered.connect(lambda: r1d.ras1dISElevations(self))
        self.ui.actionRASInlAll.triggered.connect(lambda: r1d.ras1dISAll(self))
        self.ui.actionRASLatRiverReachNames.triggered.connect(lambda: r1d.ras1dLatRiverReachNames(self))
        self.ui.actionRASLatStationing.triggered.connect(lambda: r1d.ras1dLatStationing(self))
        self.ui.actionRASLatElevations.triggered.connect(lambda: r1d.ras1dLatElevations(self))
        self.ui.actionRASLatAll.triggered.connect(lambda: r1d.ras1dLatAll(self))
        self.ui.actionRASSAElevationVolumeData.triggered.connect(lambda: r1d.ras1dSAVolumeData(self))
        self.ui.actionRASSATerrainPointExtraction.triggered.connect(lambda: r1d.ras1dSAElevations(self))
        self.ui.actionRASSAAll.triggered.connect(lambda: r1d.ras1dSAAll(self))
        self.ui.actionRASSacAssignNearestSA.triggered.connect(lambda: r1d.ras1dSACAssignNearestSA(self))
        self.ui.actionRASSacElevations.triggered.connect(lambda: r1d.ras1dSACElevations(self))
        self.ui.actionRASSacAll.triggered.connect(lambda: r1d.ras1dSACAll(self))
        self.ui.actionRASCreateRASGISImport.triggered.connect(lambda: r1d.ras1dCreateRasGisImportFile(self))
        # 2D
        self.ui.actionRASCreate2dAreaPoints.triggered.connect(lambda: r2d.ras2dCreate2dPoints(self))
        self.ui.actionRASPreview2DMesh.triggered.connect(lambda: r2d.ras2dPreviewMesh(self))
        self.ui.actionRASSave2DPointsToHECRASGeometry.triggered.connect(lambda: r2d.ras2dSaveMeshPtsToGeometry(self))
        # HELP
        self.ui.actionHelpContents.triggered.connect(self.showRGisHelp)
        self.ui.actionWebsite.triggered.connect(self.showWebsite)
        self.ui.actionAbout.triggered.connect(self.about)
        # combos
        self.ui.crsWidget.crsChanged.connect(self.updateDefaultCrs)
        self.ui.connsCbo.activated.connect(self.connChanged)
        self.ui.schemasCbo.activated.connect(self.schemaChanged)

        # Welcome message
        self.ui.textEdit.append('<b>Welcome to RiverGIS!</b><br><br>Start building your model with 3 simple steps:<br>1. <b>Choose a connection</b> to PostGIS database<br>2. choose or create database <b>schema</b> (schema = model container or folder)<br>3. select a <b>projection</b> for the river database objects (projection = Coordinate Reference System, CRS).')
        self.ui.textEdit.append('<br>If you can\'t see any connection, please, create a new one from menu Layer > Add layer > Add PostGIS layers... <br>')
        self.ui.textEdit.append('----------------------------------------------------------------------------')

        # restore the window state
        s = QSettings()
        self.restoreGeometry(s.value("/rivergis/mainWindow/geometry", QByteArray(), type=QByteArray))
        self.restoreState(s.value("/rivergis/mainWindow/windowState", QByteArray(), type=QByteArray))

        # get PostGIS connections details and populate connections' combo
        self.connChanged()

        # restore settings
        self.readSettings()

        # set QGIS projection CRS as a default for RiverGIS
        self.ui.crsWidget.setCrs(self.iface.mapCanvas().mapSettings().destinationCrs())
        self.updateDefaultCrs()

        # check if we should connect to previously used RDB
        if self.open_last_conn:
            try:
                self.connChanged(conn_name=self.opts['rdb']['last_conn'],
                             schema_name=self.opts['rdb']['last_schema'])
            except:
                pass

        # disable some actions until a connection to river database is established
        if not self.rdb:
            self.disableActions()

    def disableActions(self):
        menusAlwaysOn = ['Help']
        for m in self.menus:
            if not m.title() in menusAlwaysOn:
                for a in m.findChildren(QAction):
                    a.setDisabled(True)
        for t in self.toolbars:
            for b in t.findChildren(QToolButton):
                b.setDisabled(True)

    def enableDBActions(self):
        self.toolsNoSchema = ['Refresh Connections List',
                            'Create New Schema',
                            'Delete Schema']
        self.actions2Disable = [self.ui.actionRASCreateRdbTables,
                           self.ui.actionRASImportLayersIntoRdbTables,
                           self.ui.actionRASLoadRdbTablesIntoQGIS]
        self.ui.menuDB.findChildren(QAction)[0].setEnabled(True)
        for a in self.actions2Disable:
            a.setDisabled(True)
        for t in self.ui.dbToolBar.findChildren(QToolButton):
            if t.text() in self.toolsNoSchema:
                t.setEnabled(True)

    def enableAllActions(self):
        for m in self.menus:
            for a in m.findChildren(QAction):
                a.setEnabled(True)
        for t in self.toolbars:
            for b in t.findChildren(QToolButton):
                b.setEnabled(True)
        for a in self.actions2Disable:
            a.setEnabled(True)

    def closeEvent(self, e):
        # save the window state
        settings = QSettings()
        settings.setValue("/rivergis/mainWindow/windowState", self.saveState())
        settings.setValue("/rivergis/mainWindow/geometry", self.saveGeometry())
        settings.setValue("/rivergis/mainWindow/flags", self.windowFlags())
        self.writeSettings()
        QMainWindow.closeEvent(self, e)

    def addInfo(self, text):
        self.ui.textEdit.append(text)

    def updateDefaultCrs(self):
        self.crs = self.ui.crsWidget.crs()
        if self.rdb:
            self.rdb.SRID = int(self.crs.postgisSrid())
        self.addInfo('\nCurrent projection is {0}'.format(self.crs.authid()))

    # Database Functions

    def dbCreateSchema(self):
        schemaName, ok = QInputDialog.getText(self, 'New schema', 'New schema name:')
        if ok:
            self.rdb.create_schema(schemaName)
            self.connChanged(self.curConnName, schema_name=schemaName)
        else:
            self.addInfo('Creating new schema cancelled.')

    def dbDeleteSchema(self):
        schemaName, ok = QInputDialog.getText(self, 'Delete schema', 'Schema name:')
        if ok:
            self.rdb.drop_schema(schemaName, cascade=True)
            if self.rdb.SCHEMA == schemaName:
                self.connChanged()
            else:
                self.ui.schemasCbo.removeItem(self.ui.schemasCbo.findText(schemaName))
        else:
            self.addInfo('Droping schema cancelled.')

    def connChanged(self, conn_name='', schema_name=''):
        # close any existing connection to a river database
        if self.rdb:
            self.addInfo("Closing existing connection to {0}@{1} river database".format(self.rdb.dbname, self.rdb.host))
            self.rdb.disconnect_pg()
            self.rdb = None
        else:
            pass
        s = QSettings()
        s.beginGroup('/PostgreSQL/connections')
        connsNames = s.childGroups()

        if conn_name in connsNames:
            self.curConnName = conn_name
        else:
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
            self.ui.schemasCbo.clear()
            self.ui.schemasCbo.addItem('')
            self.disableActions()
            return
        connName = self.ui.connsCbo.currentText()
        s.endGroup()
        s.beginGroup('/PostgreSQL/connections/{0}'.format(connName))

        # first try to get the credentials from AuthManager, then from the basic settings
        authconf = s.value('authcfg', None)
        if authconf:
            auth_manager = QgsApplication.authManager()
            conf = QgsAuthMethodConfig()
            auth_manager.loadAuthenticationConfig(authconf, conf, True)
            if conf.id():
                self.user = conf.config('username', '')
                self.passwd = conf.config('password', '')
        else:
            self.user = s.value('username')
            self.passwd = s.value('password')

        self.host = s.value('host')
        self.port = s.value('port')
        self.database = s.value('database')

        s.endGroup()

        # create a new connection to river database
        self.rdb = rivdb.RiverDatabase(self, self.database, self.host, self.port, self.user, self.passwd)
        self.rdb.SRID = int(self.crs.postgisSrid())
        if self.rdb.connect_pg():
            self.addInfo('Created connection to river database: {0}@{1}'.format(self.rdb.dbname, self.rdb.host))
            self.rdb.last_conn = connName
        else:
            info = 'Couldn\'t connect to river database: {0}@{1}'.format(self.rdb.dbname, self.rdb.host)
            info += '\nPlease, check you database connection settings!'
            self.addInfo(info)
            self.ui.schemasCbo.clear()
            return

        # refresh schemas combo
        schemaName = self.ui.schemasCbo.currentText()
        qry = "SELECT nspname FROM pg_namespace WHERE nspname !~ '^pg_' AND nspname != 'information_schema' ORDER BY nspname"
        schemas = self.rdb.run_query(qry, fetch=True)
        self.ui.schemasCbo.clear()
        self.ui.schemasCbo.addItem('')
        if not schemas:
            schemas = []
        for schema in schemas:
            self.ui.schemasCbo.addItem(schema[0])
        if schema_name:
            schemaExists = self.ui.schemasCbo.findText(schema_name)
        else:
            schemaExists = self.ui.schemasCbo.findText(schemaName)
        if schemaExists:
            self.ui.schemasCbo.setCurrentIndex(schemaExists)
        self.enableDBActions()
        self.schemaChanged()

    def schemaChanged(self):
        if self.rdb:
            self.rdb.register.clear()
        else:
            return
        if not self.ui.schemasCbo.currentText() == '':
            self.schema = self.ui.schemasCbo.currentText()
            self.addInfo('Current DB schema is: {0}'.format(self.schema))
            # change river database parameters
            self.rdb.SCHEMA = self.schema
            self.rdb.create_spatial_index()
            self.rdb.last_schema = self.schema
            self.rdb.register_existing(heco)
            reg = [self.rdb.register[k].name for k in sorted(self.rdb.register.keys())]
            if self.DEBUG:
                self.addInfo('Objects registered in the database:<br>  {0}'.format('<br>  '.join(reg)))
                self.addInfo('You can load them now using RAS Geometry > Load River Database Tables Into QGIS')
            else:
                if reg:
                    self.addInfo('There are some objects registered in the database.')
                else:
                    self.addInfo('River database is empty.<br>Create or import your river network data.')
            self.enableAllActions()
        else:
            self.disableActions()
            self.enableDBActions()

    # MENU Database

    def rasCreateRdbTables(self):
        from .dlg_rasCreateRasLayers import DlgCreateRasLayers
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
        from .dlg_rasImportDataIntoRasTables import DlgImportDataIntoRasTables
        self.addInfo("<br><b>Import data into RAS PostGIS tables...</b>")
        if not self.curConnName or not self.schema:
            self.addInfo("No PostGIS database or schema selected. Choose a connection and schema.")
            return
        importData = DlgImportDataIntoRasTables(self)
        importData.exec_()

    # MENU Settings

    def options(self, widget):
        from .dlg_settings import DlgSettings
        dlg = DlgSettings(self, widget=widget)
        dlg.exec_()

    def toggleDebugMode(self):
        if self.ui.actionDebugMode.isChecked():
            self.DEBUG = 1
        else:
            self.DEBUG = 0

    def toggleAlwaysOnTop(self):
        if self.always_on_top:
            flags = self.windowFlags()
            self.setWindowFlags(flags | Qt.CustomizeWindowHint | Qt.WindowStaysOnTopHint)
        else:
            flags = self.windowFlags()
            self.setWindowFlags(flags & ~Qt.CustomizeWindowHint & ~Qt.WindowStaysOnTopHint)
        self.show()

    # MENU Help

    def showHelp(self, page='index.html'):
        helpFile = 'file:///{0}/help/{1}'.format(self.rivergisPath, page)
        QDesktopServices.openUrl(QUrl(helpFile))

    def showRGisHelp(self):
        self.showHelp('index.html')

    def showWebsite(self):
        QDesktopServices.openUrl(QUrl('http://rivergis.com'))

    def about(self):
        self.showHelp('index.html')

    def readSettings(self, defaults=False):
        sFile = os.path.join(self.rivergisPath, 'settings.json')
        if not os.path.isfile(sFile) or defaults:
            sFile = os.path.join(self.rivergisPath, 'default_settings.json')
        with open(sFile, 'r') as f:
            self.opts = json.load(f)
        for group, options in self.opts.items():
            for name, defaultValue in options.items():
                if group == 'rgis' and name in list(self.opts['rgis'].keys()):
                    setattr(self, name, self.opts['rgis'][name])
                elif group == 'rdb' and name in list(self.opts['rdb'].keys()):
                    setattr(self, name, self.opts['rdb'][name])
                else:
                    self.addInfo("Options have no key ['{}']['{}']".format(group, name))

    def writeSettings(self):
        for group, options in self.opts.items():
            for name, defaultValue in options.items():
                if group == 'rgis':
                    try:
                        self.opts['rgis'][name] = getattr(self, name)
                    except:
                        pass
                elif group == 'rdb':
                    try:
                        self.opts['rdb'][name] = getattr(self.rdb, name)
                    except:
                        pass

        with open(os.path.join(self.rivergisPath, 'settings.json'), 'w') as f:
            json.dump(self.opts, f)
