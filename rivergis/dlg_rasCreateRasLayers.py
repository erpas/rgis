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
import os
from qgis.PyQt.QtCore import Qt
from qgis.PyQt.QtWidgets import QDialog, QApplication
from . import hecobjects as heco
# from .ui.ui_rasCreateRASLayers import *
from qgis.PyQt import uic


class DlgCreateRasLayers(QDialog):
    def __init__(self, parent=None):
        QDialog.__init__(self, parent)
        tdir = os.path.dirname(os.path.realpath(__file__))
        uif = os.path.join(tdir, "ui", "ui_rasCreateRasLayers.ui")
        self.ui = uic.loadUi(uif, self)
        self.rgis = parent
        self.rdb = parent.rdb

        self.ui.buttonBox.accepted.connect(self.acceptDialog)
        self.ui.buttonBox.rejected.connect(self.reject)
        self.ui.helpButton.clicked.connect(self.displayHelp)
        self.ui.allChbox.toggled.connect(self.allChboxToggled)

        self.tables = [
            (self.ui.bankLinesChbox, heco.BankLines),
            (self.ui.blockedChbox, heco.BlockedObs),
            (self.ui.breaklines2DChbox, heco.BreakLines2d),
            (self.ui.breakpoints2DChbox, heco.BreakPoints2d),
            (self.ui.bridgesChbox, heco.Bridges),
            (self.ui.flowPathChbox, heco.Flowpaths),
            (self.ui.flowAreas2DChbox, heco.FlowAreas2d),
            (self.ui.flowAreas2DChbox, heco.MeshPoints2d),
            (self.ui.ineffectiveChbox, heco.IneffAreas),
            (self.ui.inlineStructChbox, heco.InlineStructures),
            (self.ui.streamChbox, heco.StreamCenterlines),
            (self.ui.landuseChbox, heco.LanduseAreas),
            (self.ui.lateralStructChbox, heco.LateralStructures),
            (self.ui.leveeChbox, heco.LeveeAlignment),
            (self.ui.leveeChbox, heco.LeveePoints),
            (self.ui.storageAreasChbox, heco.StorageAreas),
            (self.ui.saConnectionsChbox, heco.SAConnections),
            (self.ui.xsCutLinesChbox, heco.XSCutLines)]

        self.tables.sort(key=lambda x: x[1]().order)

    def acceptDialog(self):
        QApplication.setOverrideCursor(Qt.WaitCursor)
        self.rgis.addInfo('<br><b>Running Create RAS Layers and Tables...</b>')
        for chbox, hecobj_class in self.tables:
            if chbox.isChecked():
                obj = self.rdb.process_hecobject(hecobj_class, 'pg_create_table')
                try:
                    self.rgis.addInfo('  {0} OK'.format(obj.name))
                    self.rdb.add_to_view(obj)
                except:
                    self.rgis.addInfo('  {0} - failure!<br>{1}'.format(chbox.text(), obj))
        QApplication.restoreOverrideCursor()
        QDialog.accept(self)

    def displayHelp(self):
        pass

    def allChboxToggled(self):
        checked = self.ui.allChbox.isChecked()
        for chbox, hecobj_class in self.tables:
            chbox.setChecked(checked)
