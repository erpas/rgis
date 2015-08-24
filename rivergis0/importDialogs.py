# -*- coding: utf-8 -*-

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from rivergisdef import *
from qgis.core import *
from qgis.gui import *
from logging_rivergis import *

from ui_importRiver import Ui_importRiver2RDbDialog

class ImportRiver2RDbDialog(QDialog):
  def __init__(self, parent=None):
    QDialog.__init__(self, parent)
    self.ui = Ui_importRiver2RDbDialog()
    self.ui.setupUi(self)
    self.rgis = parent
    
    QObject.connect(self.ui.buttonBox, SIGNAL("accepted()"), self.accept)
    QObject.connect(self.ui.buttonBox, SIGNAL("rejected()"), self.reject)
    
    self.ui.comboRivernameAttr.addItem("")
    self.ui.comboTopoIDAttr.addItem("")
    self.ui.comboChainUpstreamAttr.addItem("")
    self.ui.comboChainDownstreamAttr.addItem("")
      
    rivAttrs = self.rgis.rivers2Import.pendingFields()
    for attr in rivAttrs:
      self.ui.comboRivernameAttr.addItem(attr.name())
      self.ui.comboTopoIDAttr.addItem(attr.name())
      self.ui.comboChainUpstreamAttr.addItem(attr.name())
      self.ui.comboChainDownstreamAttr.addItem(attr.name())

    
