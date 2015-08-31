# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui/ui_importDataIntoRasTables.ui'
#
# Created: Tue Aug 25 11:05:16 2015
#      by: PyQt4 UI code generator 4.11.3
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

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

class Ui_importDataIntoRasTables(object):
    def setupUi(self, importDataIntoRasTables):
        importDataIntoRasTables.setObjectName(_fromUtf8("importDataIntoRasTables"))
        importDataIntoRasTables.resize(344, 223)
        self.gridLayout = QtGui.QGridLayout(importDataIntoRasTables)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.verticalLayout = QtGui.QVBoxLayout()
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.label = QtGui.QLabel(importDataIntoRasTables)
        self.label.setObjectName(_fromUtf8("label"))
        self.verticalLayout.addWidget(self.label)
        self.riversCbo = QtGui.QComboBox(importDataIntoRasTables)
        self.riversCbo.setObjectName(_fromUtf8("riversCbo"))
        self.verticalLayout.addWidget(self.riversCbo)
        self.label_2 = QtGui.QLabel(importDataIntoRasTables)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.verticalLayout.addWidget(self.label_2)
        self.xsCbo = QtGui.QComboBox(importDataIntoRasTables)
        self.xsCbo.setObjectName(_fromUtf8("xsCbo"))
        self.verticalLayout.addWidget(self.xsCbo)
        self.label_3 = QtGui.QLabel(importDataIntoRasTables)
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.verticalLayout.addWidget(self.label_3)
        self.leveesCbo = QtGui.QComboBox(importDataIntoRasTables)
        self.leveesCbo.setObjectName(_fromUtf8("leveesCbo"))
        self.verticalLayout.addWidget(self.leveesCbo)
        self.label_4 = QtGui.QLabel(importDataIntoRasTables)
        self.label_4.setObjectName(_fromUtf8("label_4"))
        self.verticalLayout.addWidget(self.label_4)
        self.banksCbo = QtGui.QComboBox(importDataIntoRasTables)
        self.banksCbo.setObjectName(_fromUtf8("banksCbo"))
        self.verticalLayout.addWidget(self.banksCbo)
        self.buttonBox = QtGui.QDialogButtonBox(importDataIntoRasTables)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.verticalLayout.addWidget(self.buttonBox)
        self.gridLayout.addLayout(self.verticalLayout, 0, 0, 1, 1)

        self.retranslateUi(importDataIntoRasTables)
        QtCore.QMetaObject.connectSlotsByName(importDataIntoRasTables)

    def retranslateUi(self, importDataIntoRasTables):
        importDataIntoRasTables.setWindowTitle(_translate("importDataIntoRasTables", "Import Data Into RAS PostGIS Tables", None))
        self.label.setText(_translate("importDataIntoRasTables", "Rivers Layer", None))
        self.label_2.setText(_translate("importDataIntoRasTables", "Cross-sections Layer", None))
        self.label_3.setText(_translate("importDataIntoRasTables", "Levees Layer", None))
        self.label_4.setText(_translate("importDataIntoRasTables", "Banks Layer", None))

