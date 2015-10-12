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
        self.importInfo = []

        self.layers = {

            # General

            'Stream Centerlines': {
                'cbo': self.ui.cboStreamCenterlines,
                'className': 'StreamCenterlines',
                'attrs': {},
                'geomType': 1 # lines
            },

            'Cross-sections': {
                'cbo': self.ui.cboXsecs,
                'className': 'XSCutLines',
                'attrs': {},
                'geomType': 1 # lines
            },

            'Banks': {
                'cbo': self.ui.cboBanks,
                'className': 'BankLines',
                'attrs': {},
                'geomType': 1 # lines
            },

            'Flow Paths': {
                'cbo': self.ui.cboFlowPaths,
                'className': 'Flowpaths',
                'attrs': {
                    'LineType': {
                        'cbo': self.ui.cboFlowpathType,
                        'checkName': ['type', 'linetype']
                    }
                },
                'geomType': 1 # lines
            },

            'Levee Alignment': {
                'cbo': self.ui.cboLevees,
                'className': 'LeveeAlignment',
                'attrs': {},
                'geomType': 1 # lines
            },

            'Ineffective Flow Areas': {
                'cbo': self.ui.cboIneffective,
                'className': 'IneffAreas',
                'attrs': {
                    'Elevation': {
                        'cbo': self.ui.cboIneffElev,
                        'checkName': ['elevation', 'elev']
                    }
                },
                'geomType': 2 # polygons
            },

            'Blocked Obstructions': {
                'cbo': self.ui.cboObstructions,
                'className': 'BlockedObs',
                'attrs': {
                    'Elevation': {
                        'cbo': self.ui.cboObstructionsElev,
                        'checkName': ['elevation', 'elev']
                    }
                },
                'geomType': 2 # polygons
            },

            'Landuse Areas': {
                'cbo': self.ui.cboLanduse,
                'className': 'LanduseAreas',
                'attrs': {
                    'LUCode': {
                        'cbo': self.ui.cboLandCodeAttr,
                        'checkName': ['lucode', 'code']
                    },
                    'N_Value': {
                        'cbo': self.ui.cboManningAttr,
                        'checkName': ['manning', 'n', 'n_value']
                    }
                },
                'geomType': 2 # polygons
            },

            # 2d

            '2D Flow Areas': {
                'cbo': self.ui.cbo2dFlowAreas,
                'className': 'FlowAreas2d',
                'attrs': {
                    'Name': {
                        'cbo': self.ui.cbo2dAreasNameAttr,
                        'checkName': ['name', 'nazwa']
                    },
                    'CellSize': {
                        'cbo': self.ui.cbo2dAreasMeshSizeAttr,
                        'checkName': ['meshsize', 'cellsize', 'spacing']
                    }
                },
                'geomType': 2 # polygons
            },

            '2D Area Breaklines': {
                'cbo': self.ui.cboBreaklines,
                'className': 'BreakLines2d',
                'attrs': {
                    'CellSizeAlong': {
                        'cbo': self.ui.cboBreaklineCellSizeAlongAttr,
                        'checkName': ['cellsizeal', 'cellsizex', 'cellsizesx', 'dx']
                    },
                    'CellSizeAcross': {
                        'cbo': self.ui.cboBreaklineCellSizeAcrossAttr,
                        'checkName': ['cellsizeac', 'cellsizey', 'cellsizesy', 'dy']
                    },
                    'RowsAligned': {
                        'cbo': self.ui.cboBreaklineCellRowsAttr,
                        'checkName': ['rows', 'cellsnr', 'meshrows']
                    }
                },
                'geomType': 1 # lines
            },

            '2D Breakpoints': {
                'cbo': self.ui.cboBreakpoints,
                'className': 'BreakPoints2d',
                'attrs': {},
                'geomType': 0 # points
            },

            'Bridges/Culverts': {
                'cbo': self.ui.cboBridgesLayer,
                'className': 'Bridges',
                'attrs': {
                    'NodeName': {
                        'cbo': self.ui.cboBridgesName,
                        'checkName': ['name', 'nodename', 'desc']
                    },
                    'USDistance': {
                        'cbo': self.ui.cboBridgesUsDist,
                        'checkName': ['usdist', 'usdistance', 'distance']
                    },
                    'TopWidth': {
                        'cbo': self.ui.cboBridgesTopWidth,
                        'checkName': ['width', 'topwidth', 'top_width']
                    }
                },
                'geomType': 1 # lines
            },

            'Inline Structures': {
                'cbo': self.ui.cboInlineStrLayer,
                'className': 'InlineStructures',
                'attrs': {
                    'NodeName': {
                        'cbo': self.ui.cboInlineStrName,
                        'checkName': ['name', 'nodename', 'desc']
                    },
                    'USDistance': {
                        'cbo': self.ui.cboInlineStrUsDist,
                        'checkName': ['usdist', 'usdistance', 'distance']
                    },
                    'TopWidth': {
                        'cbo': self.ui.cboInlineStrTopWidth,
                        'checkName': ['width', 'topwidth', 'top_width']
                    }
                },
                'geomType': 1 # lines
            },

            'Lateral Structures': {
                'cbo': self.ui.cboLateralStrLayer,
                'className': 'InlineStructures',
                'attrs': {
                    'NodeName': {
                        'cbo': self.ui.cboLateralStrName,
                        'checkName': ['name', 'nodename', 'desc']
                    },
                    'USDistance': {
                        'cbo': self.ui.cboLateralStrUsDist,
                        'checkName': ['usdist', 'usdistance', 'distance']
                    },
                    'TopWidth': {
                        'cbo': self.ui.cboLateralStrTopWidth,
                        'checkName': ['width', 'topwidth', 'top_width']
                    }
                },
                'geomType': 1 # lines
            }
        }

        self.populateCbos()
        for layer, data in self.layers.iteritems():
            if data['attrs']:
                data['cbo'].currentIndexChanged.connect(self.layerCboChanged)


    def processLayers(self, name, data):
        if not data['cbo'].currentText() == '':
            curInd = data['cbo'].currentIndex()
            lid = data['cbo'].itemData(curInd)
            layer = self.rgis.mapRegistry.mapLayer(lid)
            attrMap = {}
            for attr, attrData in data['attrs'].iteritems():
                curText = attrData['cbo'].currentText()
                if curText:
                    attrMap[attr] = curText
            self.rgis.rdb.insert_layer(
                        layer,
                        self.rgis.rdb.register[data['className']],
                        attr_map=attrMap,
                        onlySelected=self.onlySel
            )
            self.importInfo.append(name)
            if self.rgis.iface.mapCanvas().isCachingEnabled():
                layer.setCacheImage(None)


    def acceptDialog(self):
        QApplication.setOverrideCursor(Qt.WaitCursor)
        self.onlySel = self.ui.chkOnlySelected.isChecked()
        for key, data in self.layers.iteritems():
            self.processLayers(key, data)
        self.rgis.addInfo("  Imported layers:\n    {0}".format('\n    '.join(self.importInfo)))
        self.rgis.iface.mapCanvas().refresh()
        QApplication.restoreOverrideCursor()
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


