# -*- coding: utf-8 -*-

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *
from qgis.gui import *
from qgis.utils import *
from ui.ui_rasXSUpdate import *


class DlgXSUpdateInsertMeasuredPts(QDialog):
    def __init__(self, rgis):
        QDialog.__init__(self)
        self.ui = Ui_rasXSUpdate()
        self.ui.setupUi(self)
        self.rgis = rgis
        self.ui.buttonBox.accepted.connect(self.acceptDialog)
        self.ui.buttonBox.rejected.connect(self.rejectDlg)
        self.importInfo = []

        self.populateCbos()
        for layer, data in self.layers.iteritems():
            if data['attrs']:
                data['cbo'].currentIndexChanged.connect(self.layerCboChanged)


    def acceptDialog(self):
        QApplication.setOverrideCursor(Qt.WaitCursor)
        for key, data in self.layers.iteritems():
            self.processLayers(key, data)
        self.rgis.addInfo("  Imported layers:\n    {0}".format('\n    '.join(self.importInfo)))
        self.rgis.iface.mapCanvas().refresh()
        QApplication.setOverrideCursor(Qt.ArrowCursor)
        QDialog.accept(self)


    def populateCbos(self):
        allCbosByGeomType = {0:[], 1:[], 2:[]}
        for impLayer, data in self.layers.iteritems():
            data['cbo'].clear()
            data['cbo'].addItem('')
            allCbosByGeomType[data['geomType']].append(data['cbo'])
            for attr, attrData in data['attrs'].iteritems():
                attrData['cbo'].clear()
                attrData['cbo'].addItem('')
        for layerId, layer in sorted(self.rgis.mapRegistry.mapLayers().iteritems()):
            if layer.type() == 0 and layer.geometryType() == 0: # vector and points
                for cbo in allCbosByGeomType[0]:
                    cbo.addItem(layer.name(), layerId)
            if layer.type() == 0 and layer.geometryType() == 1: # vector and polylines
                for cbo in allCbosByGeomType[1]:
                    cbo.addItem(layer.name(), layerId)
            if layer.type() == 0 and layer.geometryType() == 2: # vector and polygons
                for cbo in allCbosByGeomType[2]:
                    cbo.addItem(layer.name(), layerId)
            if layer.type() == 1: # it's a raster
                pass


    def layerCboChanged(self):
        layerCbo = self.sender()
        curInd = layerCbo.currentIndex()
        lid = layerCbo.itemData(curInd)
        cboLayer = self.rgis.mapRegistry.mapLayer(lid)
        if cboLayer:
            if cboLayer.featureCount():
                impLayerAttrs = cboLayer.pendingFields()
                # find data of the current combo
                for layer, data in self.layers.iteritems():
                    # if the combos match
                    if data['cbo'] == layerCbo:
                        # for all attributes combos
                        for attr, attrData in data['attrs'].iteritems():
                            # clear it
                            attrData['cbo'].clear()
                            attrData['cbo'].addItem('')
                            # populate with attributes
                            for a in impLayerAttrs:
                                attrData['cbo'].addItem(a.name())
                            # is there an attribute we search for?
                            for name in attrData['checkName']:
                                attrIndex = attrData['cbo'].findText(name, flags=Qt.MatchFixedString)
                                # self.rgis.addInfo('searching for {0} - found {1}'.format(name, attrIndex))
                                if attrIndex > 0:
                                    attrData['cbo'].setCurrentIndex(attrIndex)


    def rejectDlg(self):
        self.rgis.addInfo("  Import cancelled.")
        self.reject()

    def displayHelp(self):
        pass


