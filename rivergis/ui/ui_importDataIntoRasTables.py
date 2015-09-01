# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui/ui_importDataIntoRasTables.ui'
#
# Created: Tue Sep 01 22:50:24 2015
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
        importDataIntoRasTables.resize(344, 350)
        self.gridLayout = QtGui.QGridLayout(importDataIntoRasTables)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.verticalLayout = QtGui.QVBoxLayout()
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.label = QtGui.QLabel(importDataIntoRasTables)
        self.label.setObjectName(_fromUtf8("label"))
        self.verticalLayout.addWidget(self.label)
        self.cboRivers = QtGui.QComboBox(importDataIntoRasTables)
        self.cboRivers.setObjectName(_fromUtf8("cboRivers"))
        self.verticalLayout.addWidget(self.cboRivers)
        self.label_2 = QtGui.QLabel(importDataIntoRasTables)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.verticalLayout.addWidget(self.label_2)
        self.cboXs = QtGui.QComboBox(importDataIntoRasTables)
        self.cboXs.setObjectName(_fromUtf8("cboXs"))
        self.verticalLayout.addWidget(self.cboXs)
        self.label_3 = QtGui.QLabel(importDataIntoRasTables)
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.verticalLayout.addWidget(self.label_3)
        self.cboLevees = QtGui.QComboBox(importDataIntoRasTables)
        self.cboLevees.setObjectName(_fromUtf8("cboLevees"))
        self.verticalLayout.addWidget(self.cboLevees)
        self.label_4 = QtGui.QLabel(importDataIntoRasTables)
        self.label_4.setObjectName(_fromUtf8("label_4"))
        self.verticalLayout.addWidget(self.label_4)
        self.cboBanks = QtGui.QComboBox(importDataIntoRasTables)
        self.cboBanks.setObjectName(_fromUtf8("cboBanks"))
        self.verticalLayout.addWidget(self.cboBanks)
        self.label_5 = QtGui.QLabel(importDataIntoRasTables)
        self.label_5.setObjectName(_fromUtf8("label_5"))
        self.verticalLayout.addWidget(self.label_5)
        self.cboIneffective = QtGui.QComboBox(importDataIntoRasTables)
        self.cboIneffective.setObjectName(_fromUtf8("cboIneffective"))
        self.verticalLayout.addWidget(self.cboIneffective)
        self.label_6 = QtGui.QLabel(importDataIntoRasTables)
        self.label_6.setObjectName(_fromUtf8("label_6"))
        self.verticalLayout.addWidget(self.label_6)
        self.cboObstructions = QtGui.QComboBox(importDataIntoRasTables)
        self.cboObstructions.setObjectName(_fromUtf8("cboObstructions"))
        self.verticalLayout.addWidget(self.cboObstructions)
        self.label_7 = QtGui.QLabel(importDataIntoRasTables)
        self.label_7.setObjectName(_fromUtf8("label_7"))
        self.verticalLayout.addWidget(self.label_7)
        self.cboFlowPaths = QtGui.QComboBox(importDataIntoRasTables)
        self.cboFlowPaths.setObjectName(_fromUtf8("cboFlowPaths"))
        self.verticalLayout.addWidget(self.cboFlowPaths)
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
        self.label_5.setText(_translate("importDataIntoRasTables", "Ineffective Flow Areas", None))
        self.label_6.setText(_translate("importDataIntoRasTables", "Blocked Obstructions", None))
        self.label_7.setText(_translate("importDataIntoRasTables", "Flow Paths Centerlines ", None))

