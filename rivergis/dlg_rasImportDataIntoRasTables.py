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
    QObject.connect(self.ui.buttonBox, SIGNAL("accepted()"), self.accept)
    QObject.connect(self.ui.buttonBox, SIGNAL("rejected()"), self.rejectDlg)
    # QObject.connect(self.ui.helpButton, SIGNAL("clicked()"), self.displayHelp)
    self.populateCbos()

  def displayHelp(self):
    pass

  def populateCbos(self):
    self.ui.cboRivers.clear()
    self.ui.cboXs.clear()
    self.ui.cboLevees.clear()
    self.ui.cboBanks.clear()
    self.ui.cboIneffective.clear()
    self.ui.cboObstructions.clear()
    self.ui.cboFlowPaths.clear()
    self.ui.cboRivers.addItem("")
    self.ui.cboXs.addItem("")
    self.ui.cboLevees.addItem("")
    self.ui.cboBanks.addItem("")
    self.ui.cboIneffective.addItem("")
    self.ui.cboObstructions.addItem("")
    self.ui.cboFlowPaths.addItem("")
    for layerId, layer in self.rgis.mapRegistry.mapLayers().iteritems():
      if layer.type() == 0 and layer.geometryType() == 0: # vector and points
        pass
      if layer.type() == 0 and layer.geometryType() == 1: # vector and polylines
        self.ui.cboRivers.addItem(layer.name(), layerId)
        self.ui.cboXs.addItem(layer.name(), layerId)
        self.ui.cboLevees.addItem(layer.name(), layerId)
        self.ui.cboBanks.addItem(layer.name(), layerId)
        self.ui.cboFlowPaths.addItem(layer.name(), layerId)
      if layer.type() == 0 and layer.geometryType() == 2: # vector and polygons
        self.ui.cboIneffective.addItem(layer.name(), layerId)
        self.ui.cboObstructions.addItem(layer.name(), layerId)
      if layer.type() == 1: # it's a raster
        pass

  def rejectDlg(self):
    self.rgis.addInfo("  Importing data cancelled.")
    self.reject()

  def accept(self):
    QApplication.setOverrideCursor(Qt.WaitCursor)

    # TODO: insert the code

    self.rgis.addInfo("  Import completed.")
    QApplication.setOverrideCursor(Qt.ArrowCursor)
    QDialog.accept(self)



