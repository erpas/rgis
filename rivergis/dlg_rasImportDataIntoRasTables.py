# -*- coding: utf-8 -*-

import psycopg2
import psycopg2.extras

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *
from qgis.gui import *
from qgis.utils import *
from ui.ui_importDataIntoRasTables import *


class DlgImportDataIntoRasTables(QDialog):
    def __init__(self, rgis):
        QDialog.__init__(self)
        self.ui = Ui_importDataIntoRasTables()
        self.ui.setupUi(self)
        self.rgis = rgis
        self.ui.buttonBox.accepted.connect(self.acceptDialog)
        self.ui.buttonBox.rejected.connect(self.rejectDlg)
        self.ui.cboFlowPaths.currentIndexChanged.connect(self.cboFlowpathsLayerChanged)
        self.ui.cboIneffective.currentIndexChanged.connect(self.cboIneffectiveLayerChanged)
        self.ui.cboObstructions.currentIndexChanged.connect(self.cboObstructionsLayerChanged)
        self.ui.cboLanduse.currentIndexChanged.connect(self.cboLanduseLayerChanged)
        self.populateCbos()
        self.flowpathsLayer = None
        self.ineffectiveLayer = None
        self.obstructionsLayer = None
        self.landuseLayer = None
        self.importInfo = []
        self.layers = {
            'Stream Centerlines': {
                'cbo': self.ui.cboStreamCenterlines,
                'className': 'StreamCenterlines',
                'attrs': {}
            },
            'Cross-sections': {
                'cbo': self.ui.cboXsecs,
                'className': 'XSCutLines',
                'attrs': {}
            },
            'Banks': {
                'cbo': self.ui.cboBanks,
                'className': 'BankLines',
                'attrs': {}
            },
            'Flow Paths': {
                'cbo': self.ui.cboFlowPaths,
                'className': 'Flowpaths',
                'attrs': {
                    'LineType': {
                        'cbo': self.ui.cboFlowpathType,
                        'check': ['type', 'linetype']
                    }
                }
            },
            'Levee Alignment': {
                'cbo': self.ui.cboLevees,
                'className': 'LeveeAlignment',
                'attrs': {}
            },
            'Ineffective Flow Areas': {
                'cbo': self.ui.cboIneffective,
                'className': 'IneffAreas',
                'attrs': {
                    'Elevation': {
                        'cbo': self.ui.cboIneffElev,
                        'check': ['elevation', 'elev']
                    }
                }
            },
            'Blocked Obstructions': {
                'cbo': self.ui.cboObstructions,
                'className': 'BlockedObs',
                'attrs': {
                    'Elevation': {
                        'cbo': self.ui.cboObstructionsElev,
                        'check': ['elevation', 'elev']
                    }
                }
            },
            'Landuse Areas': {
                'cbo': self.ui.cboLanduse,
                'className': 'LanduseAreas',
                'attrs': {
                    'LUCode': {
                        'cbo': self.ui.cboLandCodeAttr,
                        'check': ['lucode', 'code']
                    },
                    'N_Value': {
                        'cbo': self.ui.cboManningAttr,
                        'check': ['manning', 'n', 'n_value']
                    }
                }
            }
        }

    def processLayers(self, name, data):
        if not data['cbo'].currentText() == '':
            curInd = data['cbo'].currentIndex()
            lid = data['cbo'].itemData(curInd)
            layer = self.rgis.mapRegistry.mapLayer(lid)
            attrMap = {}
            for attr, attrData in data['attrs'].iteritems():
                attrMap[attr] = attrData['cbo'].currentText()
            self.rgis.rdb.insert_layer(layer, \
                self.rgis.rdb.register[data['className']], \
                attr_map=attrMap)
            self.importInfo.append(name)
            if self.rgis.iface.mapCanvas().isCachingEnabled():
                layer.setCacheImage(None)

    def acceptDialog(self):
        QApplication.setOverrideCursor(Qt.WaitCursor)

        for key, data in self.layers.iteritems():
            self.processLayers(key, data)

        self.rgis.addInfo("  Imported layers:\n    {0}".format('\n    '.join(self.importInfo)))
        self.rgis.iface.mapCanvas().refresh()
        QApplication.setOverrideCursor(Qt.ArrowCursor)
        QDialog.accept(self)

    def displayHelp(self):
        pass

    def populateCbos(self):
        self.ui.cboStreamCenterlines.clear()
        self.ui.cboXsecs.clear()
        self.ui.cboBanks.clear()
        self.ui.cboFlowPaths.clear()
        self.ui.cboFlowpathType.clear()
        self.ui.cboLevees.clear()
        self.ui.cboIneffective.clear()
        self.ui.cboIneffElev.clear()
        self.ui.cboObstructions.clear()
        self.ui.cboObstructionsElev.clear()
        self.ui.cboLanduse.clear()
        self.ui.cboLandCodeAttr.clear()
        self.ui.cboManningAttr.clear()

        self.ui.cboStreamCenterlines.addItem('')
        self.ui.cboXsecs.addItem('')
        self.ui.cboBanks.addItem('')
        self.ui.cboFlowPaths.addItem('')
        self.ui.cboFlowpathType.addItem('')
        self.ui.cboLevees.addItem('')
        self.ui.cboIneffective.addItem('')
        self.ui.cboIneffElev.addItem('')
        self.ui.cboObstructions.addItem('')
        self.ui.cboObstructionsElev.addItem('')
        self.ui.cboLanduse.addItem('')
        self.ui.cboLandCodeAttr.addItem('')
        self.ui.cboManningAttr.addItem('')

        for layerId, layer in sorted(self.rgis.mapRegistry.mapLayers().iteritems()):
            if layer.type() == 0 and layer.geometryType() == 0: # vector and points
                pass
            if layer.type() == 0 and layer.geometryType() == 1: # vector and polylines
                self.ui.cboStreamCenterlines.addItem(layer.name(), layerId)
                self.ui.cboXsecs.addItem(layer.name(), layerId)
                self.ui.cboLevees.addItem(layer.name(), layerId)
                self.ui.cboBanks.addItem(layer.name(), layerId)
                self.ui.cboFlowPaths.addItem(layer.name(), layerId)
            if layer.type() == 0 and layer.geometryType() == 2: # vector and polygons
                self.ui.cboIneffective.addItem(layer.name(), layerId)
                self.ui.cboObstructions.addItem(layer.name(), layerId)
                self.ui.cboLanduse.addItem(layer.name(), layerId)
            if layer.type() == 1: # it's a raster
                pass


    def cboFlowpathsLayerChanged(self):
        curInd = self.ui.cboFlowPaths.currentIndex()
        lid = self.ui.cboFlowPaths.itemData(curInd)
        self.flowpathsLayer = self.rgis.mapRegistry.mapLayer(lid)
        if self.flowpathsLayer:
            if self.flowpathsLayer.featureCount():
                self.ui.cboFlowpathType.clear()
                self.ui.cboFlowpathType.addItem("")
                attrs = self.flowpathsLayer.pendingFields()
                typeIdx = 0
                for i, attr in enumerate(attrs):
                    self.ui.cboFlowpathType.addItem(attr.name())
                    if attr.name().lower() == 'linetype' or attr.name().lower() == 'type':
                        typeIdx = i + 1
                self.ui.cboFlowpathType.setCurrentIndex(typeIdx)


    def cboIneffectiveLayerChanged(self):
        curInd = self.ui.cboIneffective.currentIndex()
        lid = self.ui.cboIneffective.itemData(curInd)
        self.ineffectiveLayer = self.rgis.mapRegistry.mapLayer(lid)
        if self.ineffectiveLayer:
            if self.ineffectiveLayer.featureCount():
                self.ui.cboIneffElev.clear()
                self.ui.cboIneffElev.addItem("")
                attrs = self.ineffectiveLayer.pendingFields()
                typeIdx = 0
                for i, attr in enumerate(attrs):
                    self.ui.cboIneffElev.addItem(attr.name())
                    if attr.name().lower() == 'elevation' or attr.name().lower() == 'elev':
                        typeIdx = i + 1
                self.ui.cboIneffElev.setCurrentIndex(typeIdx)


    def cboObstructionsLayerChanged(self):
        curInd = self.ui.cboObstructions.currentIndex()
        lid = self.ui.cboObstructions.itemData(curInd)
        self.obstructionsLayer = self.rgis.mapRegistry.mapLayer(lid)
        if self.obstructionsLayer:
            if self.obstructionsLayer.featureCount():
                self.ui.cboObstructionsElev.clear()
                self.ui.cboObstructionsElev.addItem("")
                attrs = self.obstructionsLayer.pendingFields()
                typeIdx = 0
                for i, attr in enumerate(attrs):
                    self.ui.cboObstructionsElev.addItem(attr.name())
                    if attr.name().lower() == 'elevation' or attr.name().lower() == 'elev':
                        typeIdx = i + 1
                self.ui.cboObstructionsElev.setCurrentIndex(typeIdx)

    def layerCboChanged(self):
        layerCbo = self.sender()

        curInd = layerCbo.currentIndex()
        lid = layerCbo.itemData(curInd)
        cboLayer = self.rgis.mapRegistry.mapLayer(lid)
        if cboLayer:
            if cboLayer.featureCount():
                for layer, data in self.layers.iteritems():
                    # TODO
                    pass


                self.ui.cboLandCodeAttr.clear()
                self.ui.cboLandCodeAttr.addItem("")
                self.ui.cboManningAttr.clear()
                self.ui.cboManningAttr.addItem("")
                attrs = self.landuseLayer.pendingFields()
                codeIdx = mannIdx = 0
                for i, attr in enumerate(attrs):
                    self.ui.cboLandCodeAttr.addItem(attr.name())
                    self.ui.cboManningAttr.addItem(attr.name())
                    if attr.name().lower() == 'lucode' or attr.name().lower == 'code':
                        codeIdx = i + 1
                    if attr.name().lower() == 'n_value' or attr.name().lower() == 'manning':
                        mannIdx = i + 1
                self.ui.cboLandCodeAttr.setCurrentIndex(codeIdx)
                self.ui.cboManningAttr.setCurrentIndex(mannIdx)


    def cboLanduseLayerChanged(self):
        layerCbo = self.sender()
        self.rgis.addInfo(layerCbo.objectName())
        curInd = self.ui.cboLanduse.currentIndex()
        lid = self.ui.cboLanduse.itemData(curInd)
        self.landuseLayer = self.rgis.mapRegistry.mapLayer(lid)
        if self.landuseLayer:
            if self.landuseLayer.featureCount():
                self.ui.cboLandCodeAttr.clear()
                self.ui.cboLandCodeAttr.addItem("")
                self.ui.cboManningAttr.clear()
                self.ui.cboManningAttr.addItem("")
                attrs = self.landuseLayer.pendingFields()
                codeIdx = mannIdx = 0
                for i, attr in enumerate(attrs):
                    self.ui.cboLandCodeAttr.addItem(attr.name())
                    self.ui.cboManningAttr.addItem(attr.name())
                    if attr.name().lower() == 'lucode' or attr.name().lower == 'code':
                        codeIdx = i + 1
                    if attr.name().lower() == 'n_value' or attr.name().lower() == 'manning':
                        mannIdx = i + 1
                self.ui.cboLandCodeAttr.setCurrentIndex(codeIdx)
                self.ui.cboManningAttr.setCurrentIndex(mannIdx)


    def rejectDlg(self):
        self.rgis.addInfo("  Import cancelled.")
        self.reject()




