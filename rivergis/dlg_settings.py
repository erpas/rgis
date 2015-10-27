# -*- coding: utf-8 -*-

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *
from qgis.gui import *
from qgis.utils import *

from ui._ui_settings import *

class DlgSettings(QDialog):

    def __init__(self, parent=None, widget=0):
        QDialog.__init__(self, parent)
        self.ui = Ui_Settings()
        self.ui.setupUi(self)
        print "nr widgeta: ", widget
        self.ui.optionsList.setCurrentRow(widget)
        print self.ui.optionsStackedWidget.currentIndex()
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

        for layerId, layer in sorted(self.rgis.mapRegistry.mapLayers().iteritems()):
            if layer.type() == 1: # it's a raster
                # skip the raster if already in the model
                if layerId in modelDtmLids:
                    continue
                item = QStandardItem('{0}'.format(layer.name())) #layerId
                check = Qt.Unchecked
                item.setCheckState(check)
                item.setCheckable(True)
                item.setData([layer.name(), layerId])
                self.rgis.dtmModel.appendRow(item)

        self.ui.dtm_listView.setModel(self.rgis.dtmModel)


    def acceptDialog(self):
        QApplication.setOverrideCursor(Qt.WaitCursor)

        # DTMs

        self.rgis.addInfo('<br><b>New DTM setup: </b>\n')
        self.rgis.dtms = []
        for row in range(self.rgis.dtmModel.rowCount()):
            item = self.rgis.dtmModel.item(row)
            if item.checkState() == Qt.Checked:
                self.rgis.addInfo('{0}'.format(item.data()[0]))
                self.rgis.dtms.append(item.data()[1]) # append layerId

        self.rgis.dtm_chunksize = self.ui.dtm_chunksize.value()

        QApplication.restoreOverrideCursor()
        QDialog.accept(self)

    def displayHelp(self):
        pass

    def dtm_selectAllToggled(self):
        allChecked = self.ui.dtm_selectAllChbox.isChecked()
        for row in range(self.rgis.dtmModel.rowCount()):
            item = self.rgis.dtmModel.item(row)
            if allChecked:
                item.setCheckState(Qt.Checked)
            else:
                item.setCheckState(Qt.Unchecked)
