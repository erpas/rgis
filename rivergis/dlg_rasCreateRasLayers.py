# -*- coding: utf-8 -*-

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *
from qgis.gui import *
from qgis.utils import *

from ui.ui_rasCreateRASLayers import *

class DlgCreateRasLayers(QDialog):
  def __init__(self, parent=None):
    QDialog.__init__(self, parent)
    self.ui = Ui_CreateRasLayers()
    self.ui.setupUi(self)
    self.rgis = parent

    self.ui.buttonBox.accepted.connect(self.accept)
    self.ui.buttonBox.rejected.connect(self.reject)
    self.ui.helpButton.clicked.connect(self.displayHelp)
    self.ui.allChbox.toggled.connect(self.allChboxToggled)

    self.checkBoxes = [
                  self.ui.bankLinesChbox,
                  self.ui.blockedChbox,
                  self.ui.bridgesChbox,
                  self.ui.flowPathChbox,
                  self.ui.ineffectiveChbox,
                  self.ui.inlineStructChbox,
                  self.ui.streamChbox,
                  self.ui.landuseChbox,
                  self.ui.lateralStructChbox,
                  self.ui.leveeChbox,
                  self.ui.storageAreasChbox,
                  self.ui.xsCutLinesChbox
    ]


  def addInfo(self, text):
    self.rgis.ui.textEdit.append(text)


  def accept(self):
    QApplication.setOverrideCursor(Qt.WaitCursor)
    self.addInfo('\n\n<b>Running Create RAS Layers and Tables...</b>\n')
    tablesToCreate = []
    tablesToCreateTxt = ''
    for chbox in self.checkBoxes:
      if chbox.isChecked():
        tablesToCreate.append(chbox)
        tablesToCreateTxt += '    %s\n' % chbox.text()

    # TODO: dodać definicje odpowiednich tabel

    self.addInfo('\nFollowing tables were created:\n%s' % tablesToCreateTxt)
    QApplication.setOverrideCursor(Qt.ArrowCursor)
    QDialog.accept(self)

  def displayHelp(self):
    pass


  def allChboxToggled(self):
    checked = self.ui.allChbox.isChecked()
    for chbox in self.checkBoxes:
      chbox.setChecked(checked)