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
import json
from os.path import join

# TODO: try to not use the processing
import processing
from ui._ui_rivergis import Ui_RiverGIS
import river_database as rivdb
import hecobjects as heco
import ras1dFunctions as r1d
import ras2dFunctions as r2d



class RiverGIS(QMainWindow):

    OPT_GENERAL, OPT_RDB, OPT_DTM = range(3)

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
        # even some objects (rdb, for example) do not exist
        # restore settings
        self.readSettings()

        # MENU Actions

        # DB
        self.ui.actionRefreshConnections.triggered.connect(self.connChanged)
        self.ui.actionRASCreateRdbTables.triggered.connect(self.rasCreateRdbTables)
        self.ui.actionRASLoadRdbTablesIntoQGIS.triggered.connect(self.rasLoadRdbTablesIntoQGIS)
        self.ui.actionRASImportLayersIntoRdbTables.triggered.connect(self.rasImportLayersIntoRdbTables)
        # Settings
        self.ui.actionOptions.triggered.connect(self.options)
        # self.ui.actionRASDTMSetup.triggered.connect(lambda: self.options(self.OPT_DTM))
        # self.ui.actionDebugMode.toggled.connect(self.toggleDebugMode)
        # self.ui.actionAlwaysOnTop.toggled.connect(self.toggleAlwaysOnTop)
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
        self.ui.textEdit.append('<b>Welcome to RiverGIS!</b><br><br>Please start with choosing:<br>1. a <b>connection</b> to a PostGIS database<br>2. a database <b>schema</b> (schema = model container)<br>3. <b>projection</b> for river database objects (projection = Coordinate Reference System, CRS).')
        self.ui.textEdit.append('<br>If you can\'t see any connection, please, create a new one from menu Layer > Add layer > Add PostGIS layers... <br>')
        self.ui.textEdit.append('----------------------------------------------------------------------------')

        # restore the window state
        s = QSettings()
        self.restoreGeometry(s.value("/rivergis/mainWindow/geometry", QByteArray(), type=QByteArray ))
        self.restoreState(s.value("/rivergis/mainWindow/windowState", QByteArray(), type=QByteArray ))

        # get PostGIS connections details and populate connections' combo
        self.connChanged()

        # disable some actions until a connection to river database is established
        self.enableActions(False)

        # set QGIS projection CRS as a default for RiverGIS
        self.ui.crsWidget.setCrs(self.iface.mapCanvas().mapRenderer().destinationCrs())
        self.updateDefaultCrs()


    def enableActions(self, enable):
        menus = self.ui.menubar.findChildren(QMenu)
        toolbars = self.findChildren(QToolBar)
        menusAlwaysOn = ['Help']
        toolsAlwaysOn = []
        if enable:
            for m in menus:
                for a in m.findChildren(QAction):
                    a.setEnabled(True)
            for t in toolbars:
                for b in t.findChildren(QToolButton):
                    b.setEnabled(True)
        else:
            for m in menus:
                if not m.title() in menusAlwaysOn:
                    for a in m.findChildren(QAction):
                        a.setDisabled(True)
            for t in toolbars:
                for b in t.findChildren(QToolButton):
                    if not b.text() in toolsAlwaysOn:
                        b.setDisabled(True)

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
        s.beginGroup('/PostgreSQL/connections/{0}'.format(connName))
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
        schemas = self.rdb.run_query(qry, fetch=True)
        self.ui.schemasCbo.clear()
        self.ui.schemasCbo.addItem('')
        for schema in schemas:
            self.ui.schemasCbo.addItem(schema[0])
        schemaExists = self.ui.schemasCbo.findText(schemaName)
        if schemaExists:
            self.ui.schemasCbo.setCurrentIndex(schemaExists)
        self.schemaChanged()

        self.readSettings()

    def schemaChanged(self):
        self.rdb.register.clear()
        if not self.ui.schemasCbo.currentText() == '':
            self.schema = self.ui.schemasCbo.currentText()
            self.addInfo('Current DB schema is: {0}'.format(self.schema))
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
            self.enableActions(True)

    # MENU Database

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

    # MENU Settings

    def options(self, widget):
        from dlg_settings import DlgSettings
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


    def readQSetting(self, name):
        s = QSettings()
        try:
            value =  s.value("rivergis/{}".format(name))
        except KeyError:
            value = None
        return value

    def writeQSetting(self, name, value):
        s = QSettings()
        s.setValue(name, value)


    def readSettings(self):
        sFile = join(self.rivergisPath, 'settings.json')
        print sFile
        with open(sFile, 'r') as f:
            self.opts = json.load(f)
        for group, options in self.opts.iteritems():
            for name, defaultValue in options.iteritems():
                if group == 'rgis' and name in self.opts['rgis'].keys():
                    setattr(self, name, self.opts['rgis'][name])
                elif group == 'rdb' and name in self.opts['rdb'].keys():
                    setattr(self, name, self.opts['rdb'][name])
                else:
                    print "No key ['{}']['{}']".format(group, name)


    def writeSettings(self):
        for group, options in self.opts.iteritems():
            for name, defaultValue in options.iteritems():
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

        with open(join(self.rivergisPath, 'settings.json'), 'w') as f:
            json.dump(self.opts, f)



