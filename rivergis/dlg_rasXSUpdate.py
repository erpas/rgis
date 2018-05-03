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
from qgis.PyQt import uic
from . import hecobjects as heco
from qgis.core import QgsProject


class DlgXSUpdateInsertMeasuredPts(QDialog):
    def __init__(self, rgis):
        QDialog.__init__(self)
        tdir = os.path.dirname(os.path.realpath(__file__))
        uif = os.path.join(tdir, "ui", "ui_rasXSUpdate.ui")
        self.ui = uic.loadUi(uif, self)
        self.rgis = rgis
        self.ui.buttonBox.accepted.connect(self.acceptDialog)
        self.ui.buttonBox.rejected.connect(self.rejectDialog)
        self.populateCbos()
        self.ui.cboMeasuredLayer.currentIndexChanged.connect(self.cboMeasuredLayerChanged)
        self.ui.groupBanksExt.clicked.connect(self.groupBanksExtToggled)
        self.ui.groupBathyExt.clicked.connect(self.groupBathyExtToggled)

    def acceptDialog(self):
        QApplication.setOverrideCursor(Qt.WaitCursor)
        if not self.ui.xsTol.text() == '':
                tol = self.ui.xsTol.text()
        else:
            self.rgis.addInfo("XS tolerance must be specifeid. Cancelling.")
            QApplication.restoreOverrideCursor()
            return

        # create bathymetry points table
        obj = self.rgis.rdb.process_hecobject(heco.Bathymetry, 'pg_create_table')
        try:
            self.rgis.addInfo('  Table {0} created.'.format(obj.name))
        except:
            self.rgis.addInfo('  Could not create bathymetry points table.')

        # get the bathymetry points data
        data = {
            'cbo': self.ui.cboMeasuredLayer,
            'className': 'Bathymetry',
            'attrs': {
                'Elevation': {
                    'cbo': self.ui.cboMeasuredElevation,
                    'checkName': ['elevation', 'elev']
                }
            },
            'geomType': 0 # points
            }
        if not data['cbo'].currentText() == '':
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
                selected=self.ui.chkOnlySelected.isChecked())

        # Update area defined by bank lines

        if self.ui.groupBanksExt.isChecked():

            # check if bank stations are calculated for each cross-section
            qry = '''
SELECT DISTINCT
    "RiverCode", "ReachCode"
FROM
"{0}"."XSCutLines" as xs
WHERE
xs."LeftBank" IS NULL OR
xs."RightBank" IS NULL;
'''.format(self.rgis.rdb.SCHEMA)
            miss = self.rgis.rdb.run_query(qry, fetch=True)
            if miss:
                for id in miss:
                    self.rgis.addInfo(
                        'There is at least one NULL bank station on river {}, reach {}'.format(id[0], id[1]))
                self.rgis.addInfo('  Cannot continue with NULL bank station. Please, set the bank stations and try again.<br>  Cancelling...')
                QApplication.restoreOverrideCursor()
                return
            upArea = self.ui.cboInterpArea.currentText()
            self.rgis.rdb.process_hecobject(heco.XSCutLines, 'pg_update_banks', area=upArea, xs_tol=tol)

        # Update area defined by bathymetry extents polygons

        else:

            # create bathymetry extents table
            obj = self.rgis.rdb.process_hecobject(heco.BathymetryExtents, 'pg_create_table')
            try:
                self.rgis.addInfo('  Table {0} created.'.format(obj.name))
            except:
                self.rgis.addInfo('  Could not create bathymetry extents table.')

            # insert bathymetry extents into the database
            data = {
                'cbo': self.ui.cboBathyExtLayer,
                'className': 'BathymetryExtents',
                'attrs': {},
                'geomType': 2 # polygons
                }
            if not data['cbo'].currentText() == '':
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
                    attr_map=attrMap)

            self.rgis.rdb.process_hecobject(heco.XSCutLines, 'pg_update_polygons', xs_tol=tol)

        self.rgis.addInfo("  Done.")
        self.rgis.iface.mapCanvas().refresh()
        QApplication.restoreOverrideCursor()
        QDialog.accept(self)

    def populateCbos(self):
        self.ui.cboMeasuredLayer.clear()
        self.ui.cboMeasuredLayer.addItem('')
        self.ui.cboBathyExtLayer.clear()
        self.ui.cboBathyExtLayer.addItem('')
        for layerId, layer in sorted(QgsProject.instance().mapLayers().items()):
            if layer.type() == 0 and layer.geometryType() == 0: # vector and points
                self.ui.cboMeasuredLayer.addItem(layer.name(), layerId)
            if layer.type() == 0 and layer.geometryType() == 1: # vector and polylines
                pass
            if layer.type() == 0 and layer.geometryType() == 2: # vector and polygons
                self.ui.cboBathyExtLayer.addItem(layer.name(), layerId)
            if layer.type() == 1: # it's a raster
                pass
        areas = ['Channel', 'Left', 'Right']
        for area in areas:
            self.ui.cboInterpArea.addItem(area)
            self.ui.cboInterpArea.setCurrentIndex(0)

    def cboMeasuredLayerChanged(self):
        curInd = self.ui.cboMeasuredLayer.currentIndex()
        lid = self.ui.cboMeasuredLayer.itemData(curInd)
        cboLayer = QgsProject.instance().mapLayer(lid)
        if cboLayer:
            if cboLayer.featureCount():
                self.ui.cboMeasuredElevation.clear()
                self.ui.cboMeasuredElevation.addItem('')
                for a in cboLayer.fields():
                    self.ui.cboMeasuredElevation.addItem(a.name())
                attrIndex = self.ui.cboMeasuredElevation.findText('elevation', flags=Qt.MatchFixedString)
                if attrIndex > 0:
                    self.ui.cboMeasuredElevation.setCurrentIndex(attrIndex)

    def groupBanksExtToggled(self):
        if self.ui.groupBanksExt.isChecked():
            self.ui.groupBathyExt.setChecked(False)

    def groupBathyExtToggled(self):
        if self.ui.groupBathyExt.isChecked():
            self.ui.groupBanksExt.setChecked(False)

    def rejectDialog(self):
        self.rgis.addInfo("  Updating cancelled.")
        self.reject()

    def displayHelp(self):
        pass
