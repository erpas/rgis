# -*- coding: utf-8 -*-

from PyQt4 import QtCore, QtGui
from qgis.gui import *
from os.path import dirname
from miscFunctions import *

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

class Ui_hecrasPlanDialog(object):
  def setupUi(self, planDialog):
    planDialog.resize(400, 137)
    self.gridLayout = QtGui.QGridLayout(planDialog)
    self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
    self.verticalLayout = QtGui.QVBoxLayout()
    self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
    self.label = QtGui.QLabel(planDialog)
    self.label.setObjectName(_fromUtf8("label"))
    self.verticalLayout.addWidget(self.label)
    self.planCbo = QtGui.QComboBox(planDialog)
    self.planCbo.setObjectName(_fromUtf8("planCbo"))
    self.verticalLayout.addWidget(self.planCbo)
    self.label_2 = QtGui.QLabel(planDialog)
    self.label_2.setObjectName(_fromUtf8("label_2"))
    self.verticalLayout.addWidget(self.label_2)
    self.crsWidget = QgsProjectionSelectionWidget(planDialog)
    self.crsWidget.setObjectName(_fromUtf8("crsWidget"))
    self.verticalLayout.addWidget(self.crsWidget)
    self.buttonBox = QtGui.QDialogButtonBox(planDialog)
    self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
    self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
    self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
    self.verticalLayout.addWidget(self.buttonBox)
    self.gridLayout.addLayout(self.verticalLayout, 0, 0, 1, 1)

    self.retranslateUi(planDialog)
    QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), planDialog.accept)
    QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), planDialog.reject)
    QtCore.QMetaObject.connectSlotsByName(planDialog)

  def retranslateUi(self, planDialog):
    planDialog.setWindowTitle(_translate("planDialog", "Choose a HEC-RAS Plan and a CRS", None))
    self.label.setText(_translate("planDialog", "Plan", None))
    self.label_2.setText(_translate("planDialog", "Projection", None))


class DlgLoadWselHecRas(QtGui.QDialog):
  def __init__(self, rgis):
    QtGui.QDialog.__init__(self)
    self.rgis = rgis
    self.ui = Ui_hecrasPlanDialog()
    self.ui.setupUi(self)

    QtCore.QObject.connect(self.ui.buttonBox, QtCore.SIGNAL("accepted()"), self.accept)
    QtCore.QObject.connect(self.ui.buttonBox, QtCore.SIGNAL("rejected()"), self.reject)

  def accept(self):
    self.rgis.wselCrs = self.ui.crsWidget.crs()
    self.rgis.curHdfFile = self.ui.planCbo.itemData(self.ui.planCbo.currentIndex()) + '.hdf'
    QtGui.QDialog.accept(self)



