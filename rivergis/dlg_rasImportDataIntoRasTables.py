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
        # QObject.connect(self.ui.helpButton, SIGNAL("clicked()"), self.displayHelp)
        self.populateCbos()
        self.flowpathsLayer = None
        self.ineffectiveLayer = None
        self.obstructionsLayer = None
        self.landuseLayer = None


    def acceptDialog(self):
        QApplication.setOverrideCursor(Qt.WaitCursor)
        importInfo = []

        if not self.ui.cboStreamCenterlines.currentText() == '':
            curInd = self.ui.cboStreamCenterlines.currentIndex()
            lid = self.ui.cboStreamCenterlines.itemData(curInd)
            streamCenterlinesLayer = self.rgis.mapRegistry.mapLayer(lid)
            self.rgis.rdb.insert_layer(streamCenterlinesLayer, \
                self.rgis.rdb.register['StreamCenterlines'])
            importInfo.append('Stream Centerlines')
            if self.rgis.iface.mapCanvas().isCachingEnabled():
                streamCenterlinesLayer.setCacheImage(None)

        if not self.ui.cboXsecs.currentText() == '':
            curInd = self.ui.cboXsecs.currentIndex()
            lid = self.ui.cboXsecs.itemData(curInd)
            xsLayer = self.rgis.mapRegistry.mapLayer(lid)
            self.rgis.rdb.insert_layer(xsLayer, self.rgis.rdb.register['XSCutLines'])
            importInfo.append('XSCutlines')
            if self.rgis.iface.mapCanvas().isCachingEnabled():
                xsLayer.setCacheImage(None)

        if not self.ui.cboBanks.currentText() == '':
            curInd = self.ui.cboBanks.currentIndex()
            lid = self.ui.cboBanks.itemData(curInd)
            banksLayer = self.rgis.mapRegistry.mapLayer(lid)
            self.rgis.rdb.insert_layer(banksLayer, self.rgis.rdb.register['BankLines'])
            importInfo.append('Banks')
            if self.rgis.iface.mapCanvas().isCachingEnabled():
                banksLayer.setCacheImage(None)

        if not self.ui.cboFlowPaths.currentText() == '':
            attrMapFlowpaths = {}
            curInd = self.ui.cboFlowPaths.currentIndex()
            lid = self.ui.cboFlowPaths.itemData(curInd)
            pathsLayer = self.rgis.mapRegistry.mapLayer(lid)
            if not self.ui.cboFlowpathType.currentText() == '':
                attrMapFlowpaths['LineType'] = self.ui.cboFlowpathType.currentText()
            self.rgis.rdb.insert_layer(pathsLayer, self.rgis.rdb.register['Flowpaths'], attr_map=attrMapFlowpaths)
            importInfo.append('Flowpaths')
            if self.rgis.iface.mapCanvas().isCachingEnabled():
                pathsLayer.setCacheImage(None)

        if not self.ui.cboLevees.currentText() == '':
            curInd = self.ui.cboLevees.currentIndex()
            lid = self.ui.cboLevees.itemData(curInd)
            leveesLayer = self.rgis.mapRegistry.mapLayer(lid)
            self.rgis.rdb.insert_layer(leveesLayer, self.rgis.rdb.register['LeveeAlignment'])
            importInfo.append('Levee Alignment')
            if self.rgis.iface.mapCanvas().isCachingEnabled():
                leveesLayer.setCacheImage(None)

        if not self.ui.cboIneffective.currentText() == '':
            attrMapIneff = {}
            curInd = self.ui.cboIneffective.currentIndex()
            lid = self.ui.cboIneffective.itemData(curInd)
            ineffLayer = self.rgis.mapRegistry.mapLayer(lid)
            if not self.ui.cboIneffElev.currentText() == '':
                attrMapIneff['Elevation'] = self.ui.cboIneffElev.currentText()
            self.rgis.rdb.insert_layer(ineffLayer, self.rgis.rdb.register['IneffAreas'], attr_map=attrMapIneff)
            importInfo.append('Ineffective Areas')
            if self.rgis.iface.mapCanvas().isCachingEnabled():
                ineffLayer.setCacheImage(None)

        if not self.ui.cboObstructions.currentText() == '':
            attrMapObs = {}
            curInd = self.ui.cboObstructions.currentIndex()
            lid = self.ui.cboObstructions.itemData(curInd)
            obsLayer = self.rgis.mapRegistry.mapLayer(lid)
            if not self.ui.cboIneffElev.currentText() == '':
                attrMapObs['Elevation'] = self.ui.cboObstructionsElev.currentText()
            self.rgis.rdb.insert_layer(obsLayer, self.rgis.rdb.register['BlockedObs'], attr_map=attrMapObs)
            importInfo.append('Blocked Obstructions')
            if self.rgis.iface.mapCanvas().isCachingEnabled():
                obsLayer.setCacheImage(None)

        if not self.ui.cboLanduse.currentText() == '':
            attrMapLU = {}
            curInd = self.ui.cboLanduse.currentIndex()
            lid = self.ui.cboLanduse.itemData(curInd)
            landuseLayer = self.rgis.mapRegistry.mapLayer(lid)
            if not self.ui.cboLandCodeAttr.currentText() == '':
                attrMapLU['LUCode'] = self.ui.cboLandCodeAttr.currentText()
                attrMapLU['N_Value'] = self.ui.cboManningAttr.currentText()
            self.rgis.rdb.insert_layer(landuseLayer, self.rgis.rdb.register['LanduseAreas'], attr_map=attrMapLU)
            importInfo.append('Landuse Areas')
            if self.rgis.iface.mapCanvas().isCachingEnabled():
                landuseLayer.setCacheImage(None)

        self.rgis.addInfo("  Imported layers:\n    {0}".format('\n    '.join(importInfo)))
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


    def cboLanduseLayerChanged(self):
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




