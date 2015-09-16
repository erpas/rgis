# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui/ui_rasCreateRASLayers.ui'
#
# Created: Tue Sep 15 08:46:53 2015
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

class Ui_CreateRasLayers(object):
    def setupUi(self, CreateRasLayers):
        CreateRasLayers.setObjectName(_fromUtf8("CreateRasLayers"))
        CreateRasLayers.resize(377, 232)
        self.gridLayout = QtGui.QGridLayout(CreateRasLayers)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.gridLayout_2 = QtGui.QGridLayout()
        self.gridLayout_2.setObjectName(_fromUtf8("gridLayout_2"))
        self.ineffectiveChbox = QtGui.QCheckBox(CreateRasLayers)
        self.ineffectiveChbox.setObjectName(_fromUtf8("ineffectiveChbox"))
        self.gridLayout_2.addWidget(self.ineffectiveChbox, 8, 0, 1, 1)
        self.inlineStructChbox = QtGui.QCheckBox(CreateRasLayers)
        self.inlineStructChbox.setObjectName(_fromUtf8("inlineStructChbox"))
        self.gridLayout_2.addWidget(self.inlineStructChbox, 6, 1, 1, 1)
        self.buttonBox = QtGui.QDialogButtonBox(CreateRasLayers)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridLayout_2.addWidget(self.buttonBox, 10, 1, 1, 1)
        self.leveeChbox = QtGui.QCheckBox(CreateRasLayers)
        self.leveeChbox.setObjectName(_fromUtf8("leveeChbox"))
        self.gridLayout_2.addWidget(self.leveeChbox, 5, 1, 1, 1)
        self.blockedChbox = QtGui.QCheckBox(CreateRasLayers)
        self.blockedChbox.setObjectName(_fromUtf8("blockedChbox"))
        self.gridLayout_2.addWidget(self.blockedChbox, 3, 1, 1, 1)
        self.landuseChbox = QtGui.QCheckBox(CreateRasLayers)
        self.landuseChbox.setObjectName(_fromUtf8("landuseChbox"))
        self.gridLayout_2.addWidget(self.landuseChbox, 4, 1, 1, 1)
        self.xsCutLinesChbox = QtGui.QCheckBox(CreateRasLayers)
        self.xsCutLinesChbox.setObjectName(_fromUtf8("xsCutLinesChbox"))
        self.gridLayout_2.addWidget(self.xsCutLinesChbox, 6, 0, 1, 1)
        self.flowPathChbox = QtGui.QCheckBox(CreateRasLayers)
        self.flowPathChbox.setObjectName(_fromUtf8("flowPathChbox"))
        self.gridLayout_2.addWidget(self.flowPathChbox, 5, 0, 1, 1)
        self.bridgesChbox = QtGui.QCheckBox(CreateRasLayers)
        self.bridgesChbox.setObjectName(_fromUtf8("bridgesChbox"))
        self.gridLayout_2.addWidget(self.bridgesChbox, 7, 0, 1, 1)
        self.bankLinesChbox = QtGui.QCheckBox(CreateRasLayers)
        self.bankLinesChbox.setObjectName(_fromUtf8("bankLinesChbox"))
        self.gridLayout_2.addWidget(self.bankLinesChbox, 4, 0, 1, 1)
        self.lateralStructChbox = QtGui.QCheckBox(CreateRasLayers)
        self.lateralStructChbox.setObjectName(_fromUtf8("lateralStructChbox"))
        self.gridLayout_2.addWidget(self.lateralStructChbox, 7, 1, 1, 1)
        self.streamChbox = QtGui.QCheckBox(CreateRasLayers)
        self.streamChbox.setObjectName(_fromUtf8("streamChbox"))
        self.gridLayout_2.addWidget(self.streamChbox, 3, 0, 1, 1)
        self.storageAreasChbox = QtGui.QCheckBox(CreateRasLayers)
        self.storageAreasChbox.setObjectName(_fromUtf8("storageAreasChbox"))
        self.gridLayout_2.addWidget(self.storageAreasChbox, 8, 1, 1, 1)
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.helpButton = QtGui.QPushButton(CreateRasLayers)
        self.helpButton.setObjectName(_fromUtf8("helpButton"))
        self.horizontalLayout.addWidget(self.helpButton)
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.gridLayout_2.addLayout(self.horizontalLayout, 10, 0, 1, 1)
        self.gridLayout.addLayout(self.gridLayout_2, 2, 0, 1, 1)
        self.label = QtGui.QLabel(CreateRasLayers)
        self.label.setObjectName(_fromUtf8("label"))
        self.gridLayout.addWidget(self.label, 0, 0, 1, 1)
        self.allChbox = QtGui.QCheckBox(CreateRasLayers)
        self.allChbox.setObjectName(_fromUtf8("allChbox"))
        self.gridLayout.addWidget(self.allChbox, 1, 0, 1, 1)

        self.retranslateUi(CreateRasLayers)
        QtCore.QMetaObject.connectSlotsByName(CreateRasLayers)

    def retranslateUi(self, CreateRasLayers):
        CreateRasLayers.setWindowTitle(_translate("CreateRasLayers", "Create RAS Layers and Tables", None))
        self.ineffectiveChbox.setText(_translate("CreateRasLayers", "Ineffective Flow Areas", None))
        self.inlineStructChbox.setText(_translate("CreateRasLayers", "Inline Structures", None))
        self.leveeChbox.setText(_translate("CreateRasLayers", "Levee Alignment", None))
        self.blockedChbox.setText(_translate("CreateRasLayers", "Blocked Obstructions", None))
        self.landuseChbox.setText(_translate("CreateRasLayers", "Landuse Areas", None))
        self.xsCutLinesChbox.setText(_translate("CreateRasLayers", "XS Cut Lines", None))
        self.flowPathChbox.setText(_translate("CreateRasLayers", "Flow Path Centerlines", None))
        self.bridgesChbox.setText(_translate("CreateRasLayers", "Bridges/Culverts", None))
        self.bankLinesChbox.setText(_translate("CreateRasLayers", "Bank Lines", None))
        self.lateralStructChbox.setText(_translate("CreateRasLayers", "Lateral Structures", None))
        self.streamChbox.setText(_translate("CreateRasLayers", "Stream Centerlines", None))
        self.storageAreasChbox.setText(_translate("CreateRasLayers", "Storage Areas", None))
        self.helpButton.setText(_translate("CreateRasLayers", "Help", None))
        self.label.setText(_translate("CreateRasLayers", "Select Layers to create:", None))
        self.allChbox.setText(_translate("CreateRasLayers", "Select All", None))

