# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui/ui_importDataIntoRasTables.ui'
#
# Created: Thu Sep 17 12:05:10 2015
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
        importDataIntoRasTables.resize(337, 586)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.MinimumExpanding, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(importDataIntoRasTables.sizePolicy().hasHeightForWidth())
        importDataIntoRasTables.setSizePolicy(sizePolicy)
        self.gridLayout = QtGui.QGridLayout(importDataIntoRasTables)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.tabWidget = QtGui.QTabWidget(importDataIntoRasTables)
        self.tabWidget.setObjectName(_fromUtf8("tabWidget"))
        self.general = QtGui.QWidget()
        self.general.setObjectName(_fromUtf8("general"))
        self.gridLayout_2 = QtGui.QGridLayout(self.general)
        self.gridLayout_2.setObjectName(_fromUtf8("gridLayout_2"))
        self.verticalLayout = QtGui.QVBoxLayout()
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.label = QtGui.QLabel(self.general)
        self.label.setObjectName(_fromUtf8("label"))
        self.verticalLayout.addWidget(self.label)
        self.cboStreamCenterlines = QtGui.QComboBox(self.general)
        self.cboStreamCenterlines.setObjectName(_fromUtf8("cboStreamCenterlines"))
        self.verticalLayout.addWidget(self.cboStreamCenterlines)
        self.label_2 = QtGui.QLabel(self.general)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.verticalLayout.addWidget(self.label_2)
        self.cboXsecs = QtGui.QComboBox(self.general)
        self.cboXsecs.setObjectName(_fromUtf8("cboXsecs"))
        self.verticalLayout.addWidget(self.cboXsecs)
        self.label_4 = QtGui.QLabel(self.general)
        self.label_4.setObjectName(_fromUtf8("label_4"))
        self.verticalLayout.addWidget(self.label_4)
        self.cboBanks = QtGui.QComboBox(self.general)
        self.cboBanks.setObjectName(_fromUtf8("cboBanks"))
        self.verticalLayout.addWidget(self.cboBanks)
        self.label_7 = QtGui.QLabel(self.general)
        self.label_7.setObjectName(_fromUtf8("label_7"))
        self.verticalLayout.addWidget(self.label_7)
        self.cboFlowPaths = QtGui.QComboBox(self.general)
        self.cboFlowPaths.setObjectName(_fromUtf8("cboFlowPaths"))
        self.verticalLayout.addWidget(self.cboFlowPaths)
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.label_8 = QtGui.QLabel(self.general)
        self.label_8.setObjectName(_fromUtf8("label_8"))
        self.horizontalLayout.addWidget(self.label_8)
        self.cboFlowpathType = QtGui.QComboBox(self.general)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.MinimumExpanding, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.cboFlowpathType.sizePolicy().hasHeightForWidth())
        self.cboFlowpathType.setSizePolicy(sizePolicy)
        self.cboFlowpathType.setMinimumSize(QtCore.QSize(0, 0))
        self.cboFlowpathType.setObjectName(_fromUtf8("cboFlowpathType"))
        self.horizontalLayout.addWidget(self.cboFlowpathType)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.label_3 = QtGui.QLabel(self.general)
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.verticalLayout.addWidget(self.label_3)
        self.cboLevees = QtGui.QComboBox(self.general)
        self.cboLevees.setObjectName(_fromUtf8("cboLevees"))
        self.verticalLayout.addWidget(self.cboLevees)
        self.label_5 = QtGui.QLabel(self.general)
        self.label_5.setObjectName(_fromUtf8("label_5"))
        self.verticalLayout.addWidget(self.label_5)
        self.cboIneffective = QtGui.QComboBox(self.general)
        self.cboIneffective.setObjectName(_fromUtf8("cboIneffective"))
        self.verticalLayout.addWidget(self.cboIneffective)
        self.horizontalLayout_3 = QtGui.QHBoxLayout()
        self.horizontalLayout_3.setObjectName(_fromUtf8("horizontalLayout_3"))
        self.label_10 = QtGui.QLabel(self.general)
        self.label_10.setObjectName(_fromUtf8("label_10"))
        self.horizontalLayout_3.addWidget(self.label_10)
        self.cboIneffElev = QtGui.QComboBox(self.general)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.MinimumExpanding, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.cboIneffElev.sizePolicy().hasHeightForWidth())
        self.cboIneffElev.setSizePolicy(sizePolicy)
        self.cboIneffElev.setObjectName(_fromUtf8("cboIneffElev"))
        self.horizontalLayout_3.addWidget(self.cboIneffElev)
        self.verticalLayout.addLayout(self.horizontalLayout_3)
        self.label_6 = QtGui.QLabel(self.general)
        self.label_6.setObjectName(_fromUtf8("label_6"))
        self.verticalLayout.addWidget(self.label_6)
        self.cboObstructions = QtGui.QComboBox(self.general)
        self.cboObstructions.setObjectName(_fromUtf8("cboObstructions"))
        self.verticalLayout.addWidget(self.cboObstructions)
        self.horizontalLayout_4 = QtGui.QHBoxLayout()
        self.horizontalLayout_4.setObjectName(_fromUtf8("horizontalLayout_4"))
        self.label_11 = QtGui.QLabel(self.general)
        self.label_11.setObjectName(_fromUtf8("label_11"))
        self.horizontalLayout_4.addWidget(self.label_11)
        self.cboObstructionsElev = QtGui.QComboBox(self.general)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.MinimumExpanding, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.cboObstructionsElev.sizePolicy().hasHeightForWidth())
        self.cboObstructionsElev.setSizePolicy(sizePolicy)
        self.cboObstructionsElev.setObjectName(_fromUtf8("cboObstructionsElev"))
        self.horizontalLayout_4.addWidget(self.cboObstructionsElev)
        self.verticalLayout.addLayout(self.horizontalLayout_4)
        self.label_12 = QtGui.QLabel(self.general)
        self.label_12.setObjectName(_fromUtf8("label_12"))
        self.verticalLayout.addWidget(self.label_12)
        self.cboLanduse = QtGui.QComboBox(self.general)
        self.cboLanduse.setObjectName(_fromUtf8("cboLanduse"))
        self.verticalLayout.addWidget(self.cboLanduse)
        self.horizontalLayout_5 = QtGui.QHBoxLayout()
        self.horizontalLayout_5.setObjectName(_fromUtf8("horizontalLayout_5"))
        self.label_13 = QtGui.QLabel(self.general)
        self.label_13.setObjectName(_fromUtf8("label_13"))
        self.horizontalLayout_5.addWidget(self.label_13)
        self.cboLandCodeAttr = QtGui.QComboBox(self.general)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.MinimumExpanding, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.cboLandCodeAttr.sizePolicy().hasHeightForWidth())
        self.cboLandCodeAttr.setSizePolicy(sizePolicy)
        self.cboLandCodeAttr.setObjectName(_fromUtf8("cboLandCodeAttr"))
        self.horizontalLayout_5.addWidget(self.cboLandCodeAttr)
        self.verticalLayout.addLayout(self.horizontalLayout_5)
        self.horizontalLayout_6 = QtGui.QHBoxLayout()
        self.horizontalLayout_6.setObjectName(_fromUtf8("horizontalLayout_6"))
        self.label_14 = QtGui.QLabel(self.general)
        self.label_14.setObjectName(_fromUtf8("label_14"))
        self.horizontalLayout_6.addWidget(self.label_14)
        self.cboManningAttr = QtGui.QComboBox(self.general)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.MinimumExpanding, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.cboManningAttr.sizePolicy().hasHeightForWidth())
        self.cboManningAttr.setSizePolicy(sizePolicy)
        self.cboManningAttr.setObjectName(_fromUtf8("cboManningAttr"))
        self.horizontalLayout_6.addWidget(self.cboManningAttr)
        self.verticalLayout.addLayout(self.horizontalLayout_6)
        self.buttonBox = QtGui.QDialogButtonBox(self.general)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.verticalLayout.addWidget(self.buttonBox)
        self.gridLayout_2.addLayout(self.verticalLayout, 0, 0, 1, 1)
        self.tabWidget.addTab(self.general, _fromUtf8(""))
        self.structures = QtGui.QWidget()
        self.structures.setObjectName(_fromUtf8("structures"))
        self.gridLayout_3 = QtGui.QGridLayout(self.structures)
        self.gridLayout_3.setObjectName(_fromUtf8("gridLayout_3"))
        self.verticalLayout_2 = QtGui.QVBoxLayout()
        self.verticalLayout_2.setObjectName(_fromUtf8("verticalLayout_2"))
        self.gridLayout_3.addLayout(self.verticalLayout_2, 0, 0, 1, 1)
        self.tabWidget.addTab(self.structures, _fromUtf8(""))
        self.tab = QtGui.QWidget()
        self.tab.setObjectName(_fromUtf8("tab"))
        self.tabWidget.addTab(self.tab, _fromUtf8(""))
        self.gridLayout.addWidget(self.tabWidget, 0, 0, 1, 1)

        self.retranslateUi(importDataIntoRasTables)
        self.tabWidget.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(importDataIntoRasTables)

    def retranslateUi(self, importDataIntoRasTables):
        importDataIntoRasTables.setWindowTitle(_translate("importDataIntoRasTables", "Import Data Into RAS PostGIS Tables", None))
        self.label.setText(_translate("importDataIntoRasTables", "Rivers Layer", None))
        self.label_2.setText(_translate("importDataIntoRasTables", "Cross-sections Layer", None))
        self.label_4.setText(_translate("importDataIntoRasTables", "Banks Layer", None))
        self.label_7.setText(_translate("importDataIntoRasTables", "Flow Paths Layer", None))
        self.label_8.setText(_translate("importDataIntoRasTables", "Type attribute", None))
        self.label_3.setText(_translate("importDataIntoRasTables", "Levees Layer", None))
        self.label_5.setText(_translate("importDataIntoRasTables", "Ineffective Flow Areas Layer", None))
        self.label_10.setText(_translate("importDataIntoRasTables", "Elevation attribute", None))
        self.label_6.setText(_translate("importDataIntoRasTables", "Blocked Obstructions Layer", None))
        self.label_11.setText(_translate("importDataIntoRasTables", "Elevation attribute", None))
        self.label_12.setText(_translate("importDataIntoRasTables", "Landuse Areas Layer", None))
        self.label_13.setText(_translate("importDataIntoRasTables", "Land Cover Code attribute", None))
        self.label_14.setText(_translate("importDataIntoRasTables", "Manning\'s n attribute", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.general), _translate("importDataIntoRasTables", "General", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.structures), _translate("importDataIntoRasTables", "Hydraulic Structures", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab), _translate("importDataIntoRasTables", "Storage Areas", None))

