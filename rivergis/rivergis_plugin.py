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
from __future__ import print_function
from __future__ import absolute_import
from builtins import object

from qgis.PyQt.QtCore import QObject, Qt
from qgis.PyQt.QtWidgets import QAction, QApplication
from qgis.PyQt.QtGui import QIcon
from .utils import icon_path


class RiverGISPlugin(object):
    def __init__(self, iface):
        self.iface = iface
        self.dlg = None

    def initGui(self):
        rg_icon = QIcon(icon_path('rivergis.svg'))
        self.action = QAction(rg_icon, 'RiverGIS', self.iface.mainWindow())
        self.action.setObjectName('rivergis')
        self.action.triggered.connect(self.run)
        # Add toolbar button and menu item
        self.iface.addToolBarIcon(self.action)
        self.iface.addPluginToMenu(QApplication.translate('RiverGIS', 'RiverGIS'), self.action)

    def unload(self):
        # Remove the plugin menu item and icon
        self.iface.removeToolBarIcon(self.action)
        self.iface.removePluginMenu(QApplication.translate('RiverGIS', 'RiverGIS'), self.action)

        if self.dlg is not None:
            self.dlg.close()

    def run(self):
        # keep opened only one instance
        if self.dlg is None:
            from .rivergis import RiverGIS
            self.dlg = RiverGIS(self.iface)
            self.dlg.destroyed.connect(self.onDestroyed)
        self.dlg.show()
        self.dlg.raise_()
        self.dlg.setWindowState(self.dlg.windowState() & ~Qt.WindowMinimized)
        self.dlg.activateWindow()

    def onDestroyed(self, obj):
        self.dlg = None
