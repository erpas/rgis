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
  def __init__(self, parent=None):
    QDialog.__init__(self, parent)
    self.ui = Ui_importDataIntoRasTables()
    self.ui.setupUi(self)
    self.rgis = parent

    QObject.connect(self.ui.buttonBox, SIGNAL("accepted()"), self.accept)
    QObject.connect(self.ui.buttonBox, SIGNAL("rejected()"), self.reject)
    # QObject.connect(self.ui.helpButton, SIGNAL("clicked()"), self.displayHelp)

    self.populateCbos()
    self.riv_id = None

  def displayHelp(self):
    pass

  def populateCbos(self):
    self.ui.cboRivers.clear()
    rivers = []
    if not self.mydb:
      return
    cur = self.mydb.cursor()
    qry = "SELECT * FROM river_data"
    cur.execute(qry)
    data = cur.fetchall()
    for row in data:
      rivers.append([row[0], row[1], row[2], row[3]] )
    del cur

    for riv in rivers:
      self.ui.cboRivers.addItem(riv[1], riv)


  def accept(self):
    QApplication.setOverrideCursor(Qt.WaitCursor)
    self.rgis.addInfo("<b>Importing data into RAS PostGIS tables...</b>")

    # TODO: insert the code

    self.rgis.addInfo("  Import completed.")
    QApplication.setOverrideCursor(Qt.ArrowCursor)
    QDialog.accept(self)



