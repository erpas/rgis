# -*- coding: utf-8 -*-
"""
/***************************************************************************
 RiverGis
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
from qgis.core import *
import resources_rc
from rivergisdialog import RiverGisDialog
from os.path import dirname, join, exists


class RiverGis0:
    def __init__(self, iface):
        self.iface = iface
        self.plugin_dir = dirname(__file__)
        locale = QSettings().value("locale/userLocale")[0:2]
        localePath = join(self.plugin_dir, 'i18n', 'rivergis_{}.qm'.format(locale))
        if exists(localePath):
            self.translator = QTranslator()
            self.translator.load(localePath)
            if qVersion() > '4.3.3':
                QCoreApplication.installTranslator(self.translator)
        self.dlg = RiverGisDialog(self)

    def initGui(self):
        self.action = QAction(
            QIcon(":/plugins/rivergis0/icons/rivergis.svg"),
            u"Rivergis0", self.iface.mainWindow())
        self.action.triggered.connect(self.run)
        self.iface.addToolBarIcon(self.action)
        self.iface.addPluginToMenu(u"&Rivergis", self.action)

    def unload(self):
        self.iface.removePluginMenu(u"&Rivergis", self.action)
        self.iface.removeToolBarIcon(self.action)

    def run(self):
        self.dlg.show()

