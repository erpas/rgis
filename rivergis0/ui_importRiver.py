# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui_importRiver.ui'
#
# Created: Tue Jan 28 18:51:06 2014
#      by: PyQt4 UI code generator 4.8.3
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_importRiver2RDbDialog(object):
    def setupUi(self, importRiver2RDbDialog):
        importRiver2RDbDialog.setObjectName(_fromUtf8("importRiver2RDbDialog"))
        importRiver2RDbDialog.resize(408, 223)
        self.gridLayout_2 = QtGui.QGridLayout(importRiver2RDbDialog)
        self.gridLayout_2.setObjectName(_fromUtf8("gridLayout_2"))
        self.gridLayout = QtGui.QGridLayout()
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.comboTopoIDAttr = QtGui.QComboBox(importRiver2RDbDialog)
        self.comboTopoIDAttr.setObjectName(_fromUtf8("comboTopoIDAttr"))
        self.gridLayout.addWidget(self.comboTopoIDAttr, 1, 1, 1, 1)
        self.comboRivernameAttr = QtGui.QComboBox(importRiver2RDbDialog)
        self.comboRivernameAttr.setMinimumSize(QtCore.QSize(250, 0))
        self.comboRivernameAttr.setObjectName(_fromUtf8("comboRivernameAttr"))
        self.gridLayout.addWidget(self.comboRivernameAttr, 0, 1, 1, 1)
        self.buttonBox = QtGui.QDialogButtonBox(importRiver2RDbDialog)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridLayout.addWidget(self.buttonBox, 4, 1, 1, 1)
        self.label_4 = QtGui.QLabel(importRiver2RDbDialog)
        self.label_4.setObjectName(_fromUtf8("label_4"))
        self.gridLayout.addWidget(self.label_4, 3, 0, 1, 1)
        self.comboChainDownstreamAttr = QtGui.QComboBox(importRiver2RDbDialog)
        self.comboChainDownstreamAttr.setObjectName(_fromUtf8("comboChainDownstreamAttr"))
        self.gridLayout.addWidget(self.comboChainDownstreamAttr, 3, 1, 1, 1)
        self.label = QtGui.QLabel(importRiver2RDbDialog)
        self.label.setObjectName(_fromUtf8("label"))
        self.gridLayout.addWidget(self.label, 0, 0, 1, 1)
        self.label_2 = QtGui.QLabel(importRiver2RDbDialog)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.gridLayout.addWidget(self.label_2, 1, 0, 1, 1)
        self.label_3 = QtGui.QLabel(importRiver2RDbDialog)
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.gridLayout.addWidget(self.label_3, 2, 0, 1, 1)
        self.comboChainUpstreamAttr = QtGui.QComboBox(importRiver2RDbDialog)
        self.comboChainUpstreamAttr.setObjectName(_fromUtf8("comboChainUpstreamAttr"))
        self.gridLayout.addWidget(self.comboChainUpstreamAttr, 2, 1, 1, 1)
        self.gridLayout_2.addLayout(self.gridLayout, 0, 0, 1, 1)

        self.retranslateUi(importRiver2RDbDialog)
        QtCore.QMetaObject.connectSlotsByName(importRiver2RDbDialog)

    def retranslateUi(self, importRiver2RDbDialog):
        importRiver2RDbDialog.setWindowTitle(QtGui.QApplication.translate("importRiver2RDbDialog", "Choose River Layer Attributes to Import", None, QtGui.QApplication.UnicodeUTF8))
        self.label_4.setText(QtGui.QApplication.translate("importRiver2RDbDialog", "Chainage \n"
"Downstream", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("importRiver2RDbDialog", "River name", None, QtGui.QApplication.UnicodeUTF8))
        self.label_2.setText(QtGui.QApplication.translate("importRiver2RDbDialog", "Topo ID", None, QtGui.QApplication.UnicodeUTF8))
        self.label_3.setText(QtGui.QApplication.translate("importRiver2RDbDialog", "Chainage Upstream", None, QtGui.QApplication.UnicodeUTF8))

