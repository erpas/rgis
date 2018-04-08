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
from . import hecobjects as heco
from qgis.core import QgsProject
from qgis.PyQt import uic
from qgis.PyQt.QtCore import Qt
from qgis.PyQt.QtWidgets import QDialog, QApplication


class DlgImportDataIntoRasTables(QDialog):
    def __init__(self, rgis):
        QDialog.__init__(self)
        tdir = os.path.dirname(os.path.realpath(__file__))
        uif = os.path.join(tdir, "ui", "ui_importDataIntoRasTables.ui")
        self.ui = uic.loadUi(uif, self)
        self.rgis = rgis
        self.ui.buttonBox.accepted.connect(self.acceptDialog)
        self.ui.buttonBox.rejected.connect(self.rejectDlg)
        self.importInfo = []

        self.layers = {

            # General

            'Stream Centerlines': {
                'cbo': self.ui.cboStreamCenterlines,
                'className': 'StreamCenterlines',
                'attrs': {
                    'RiverCode': {
                        'cbo': self.ui.cboRiverNameAttr,
                        'checkName': ['name', 'river', 'nazwa']
                    },
                    'ReachCode': {
                        'cbo': self.ui.cboReachNameAttr,
                        'checkName': ['name', 'reach', 'nazwa']
                    }
                },
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
                        'checkName': ['usdist', 'usdistance', 'distance', 'dist']
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
                        'checkName': ['usdist', 'usdistance', 'distance', 'dist']
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
                'className': 'LateralStructures',
                'attrs': {
                    'NodeName': {
                        'cbo': self.ui.cboLateralStrName,
                        'checkName': ['name', 'nodename', 'desc']
                    },
                    'USDistance': {
                        'cbo': self.ui.cboLateralStrUsDist,
                        'checkName': ['usdist', 'usdistance', 'distance', 'dist']
                    },
                    'TopWidth': {
                        'cbo': self.ui.cboLateralStrTopWidth,
                        'checkName': ['width', 'topwidth', 'top_width']
                    }
                },
                'geomType': 1 # lines
            },

            'Storage Areas': {
                'cbo': self.ui.cboSALayer,
                'className': 'StorageAreas',
                'attrs': {
                    'Name': {
                        'cbo': self.ui.cboSAName,
                        'checkName': ['name', 'nodename', 'desc']
                    }
                },
                'geomType': 2 # polygons
            },

            'Storage Area Connections': {
                'cbo': self.ui.cboSacLayer,
                'className': 'SAConnections',
                'attrs': {
                    'Name': {
                        'cbo': self.ui.cboSacName,
                        'checkName': ['name', 'nodename', 'desc']
                    }
                },
                'geomType': 1 # lines
            }
        }

        self.populateCbos()
        for layer, data in self.layers.items():
            if data['attrs']:
                data['cbo'].currentIndexChanged.connect(self.layerCboChanged)

    def processLayers(self, name, data):
        curInd = data['cbo'].currentIndex()
        lid = data['cbo'].itemData(curInd)
        layer = QgsProject.instance().mapLayer(lid)
        attrMap = {}
        for attr, attrData in data['attrs'].items():
            curText = attrData['cbo'].currentText()
            if curText:
                attrMap[attr] = curText
        self.rgis.rdb.insert_layer(
                    layer,
                    self.rgis.rdb.register[data['className']],
                    attr_map=attrMap,
                    selected=self.onlySel)
        self.importInfo.append(name)
        # if self.rgis.iface.mapCanvas().isCachingEnabled():
        #     layer.setCacheImage(None)

    def acceptDialog(self):
        QApplication.setOverrideCursor(Qt.WaitCursor)
        self.onlySel = self.ui.chkOnlySelected.isChecked()
        tabs = self.rgis.rdb.list_tables()
        for key, data in self.layers.items():
            if not data['cbo'].currentText() == '':
                if data['className'] not in tabs:
                    hecobject = getattr(heco, data['className'])
                    self.rgis.rdb.process_hecobject(hecobject, 'pg_create_table')
                else:
                    pass
                self.processLayers(key, data)
            else:
                pass
        self.rgis.addInfo('  Imported layers:\n    {0}'.format('\n    '.join(self.importInfo)))
        self.rgis.iface.mapCanvas().refresh()
        QApplication.restoreOverrideCursor()
        QDialog.accept(self)

    def populateCbos(self):
        allCbosByGeomType = {0: [], 1: [], 2: []}
        for impLayer, data in self.layers.items():
            data['cbo'].clear()
            data['cbo'].addItem('')
            allCbosByGeomType[data['geomType']].append(data['cbo'])
            for attr, attrData in data['attrs'].items():
                attrData['cbo'].clear()
                attrData['cbo'].addItem('')
        for layerId, layer in sorted(QgsProject.instance().mapLayers().items()):
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
        cboLayer = QgsProject.instance().mapLayer(lid)
        if cboLayer:
            if cboLayer.featureCount():
                impLayerAttrs = cboLayer.fields()
                # find data of the current combo
                for layer, data in self.layers.items():
                    # if the combos match
                    if data['cbo'] == layerCbo:
                        # for all attributes combos
                        for attr, attrData in data['attrs'].items():
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
