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
from builtins import range

from qgis.PyQt import uic
from qgis.PyQt.QtCore import Qt
from qgis.PyQt.QtWidgets import QDialog, QApplication
from qgis.PyQt.QtGui import QStandardItem, QStandardItemModel
from qgis.core import QgsProject
import os


class DlgSettings(QDialog):

    def __init__(self, parent=None, widget=0):
        QDialog.__init__(self, parent)
        tdir = os.path.dirname(os.path.realpath(__file__))
        uif = os.path.join(tdir, "ui", "ui_settings.ui")
        self.ui = uic.loadUi(uif, self)
        self.ui.optionsList.setCurrentRow(widget)
        self.rgis = parent
        self.rdb = parent.rdb

        if not self.rgis.dtms:
            self.rgis.dtmModel = QStandardItemModel()

        self.ui.buttonBox.accepted.connect(self.acceptDialog)
        self.ui.buttonBox.rejected.connect(self.reject)

        self.ui.dtm_selectAllChbox.toggled.connect(self.dtm_selectAllToggled)

        # layerIds of rasters already in the model
        modelDtmLids = []
        for row in range(self.rgis.dtmModel.rowCount()):
            modelDtmLids.append(self.rgis.dtmModel.item(row).data()[1])

        for layerId, layer in sorted(QgsProject.instance().mapLayers().items()):
            if layer.type() == 1: # it's a raster
                # skip the raster if already in the model
                if layerId in modelDtmLids:
                    continue
                item = QStandardItem('{0}'.format(layer.name()))  #layerId
                check = Qt.Unchecked
                item.setCheckState(check)
                item.setCheckable(True)
                item.setData([layer.name(), layerId])
                self.rgis.dtmModel.appendRow(item)

        self.ui.dtm_listView.setModel(self.rgis.dtmModel)

        # set UI according to current variable values
        # General
        self.ui.open_lastChbox.setChecked(self.rgis.open_last_conn)
        self.ui.debugModeChbox.setChecked(self.rgis.DEBUG)
        self.ui.rgisAlwaysOnTopChbox.setChecked(self.rgis.always_on_top)
        # DB
        self.ui.db_loadAllChbox.setChecked(self.rgis.rdb.LOAD_ALL)

    def acceptDialog(self):
        QApplication.setOverrideCursor(Qt.WaitCursor)

        # General
        self.rgis.open_last_conn = self.ui.open_lastChbox.isChecked()
        self.rgis.DEBUG = self.ui.debugModeChbox.isChecked()
        self.rgis.always_on_top = self.ui.rgisAlwaysOnTopChbox.isChecked()
        self.rgis.toggleAlwaysOnTop()

        # River DB
        self.rgis.rdb.OVERWRITE = True
        self.rgis.rdb.LOAD_ALL = self.ui.db_loadAllChbox.isChecked()

        # DTMs
        self.rgis.dtms = []
        for row in range(self.rgis.dtmModel.rowCount()):
            item = self.rgis.dtmModel.item(row)
            if item.checkState() == Qt.Checked:
                # self.rgis.addInfo('{0}'.format(item.data()[0]))
                self.rgis.dtms.append(item.data()[1]) # append layerId

        self.rgis.dtm_chunksize = self.ui.dtm_chunksize.value()

        # write settings to json
        self.rgis.writeSettings()

        QApplication.restoreOverrideCursor()
        QDialog.accept(self)

    def dtm_selectAllToggled(self):
        allChecked = self.ui.dtm_selectAllChbox.isChecked()
        for row in range(self.rgis.dtmModel.rowCount()):
            item = self.rgis.dtmModel.item(row)
            if allChecked:
                item.setCheckState(Qt.Checked)
            else:
                item.setCheckState(Qt.Unchecked)
