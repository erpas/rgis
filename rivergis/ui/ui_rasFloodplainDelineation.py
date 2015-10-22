# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui/ui_rasFloodplainDelineation.ui'
#
# Created: Thu Oct 22 10:50:06 2015
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

class Ui_DlgFloodplainDelineation(object):
    def setupUi(self, DlgFloodplainDelineation):
        DlgFloodplainDelineation.setObjectName(_fromUtf8("DlgFloodplainDelineation"))
        DlgFloodplainDelineation.resize(294, 260)
        self.gridLayout = QtGui.QGridLayout(DlgFloodplainDelineation)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.verticalLayout = QtGui.QVBoxLayout()
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.label = QtGui.QLabel(DlgFloodplainDelineation)
        self.label.setObjectName(_fromUtf8("label"))
        self.verticalLayout.addWidget(self.label)
        self.cboDtm = QtGui.QComboBox(DlgFloodplainDelineation)
        self.cboDtm.setAcceptDrops(False)
        self.cboDtm.setObjectName(_fromUtf8("cboDtm"))
        self.verticalLayout.addWidget(self.cboDtm)
        self.AreaNameAttributeLabel = QtGui.QLabel(DlgFloodplainDelineation)
        self.AreaNameAttributeLabel.setObjectName(_fromUtf8("AreaNameAttributeLabel"))
        self.verticalLayout.addWidget(self.AreaNameAttributeLabel)
        self.cboWsel = QtGui.QComboBox(DlgFloodplainDelineation)
        self.cboWsel.setObjectName(_fromUtf8("cboWsel"))
        self.verticalLayout.addWidget(self.cboWsel)
        self.tilesGroup = QtGui.QGroupBox(DlgFloodplainDelineation)
        self.tilesGroup.setObjectName(_fromUtf8("tilesGroup"))
        self.gridLayout_2 = QtGui.QGridLayout(self.tilesGroup)
        self.gridLayout_2.setObjectName(_fromUtf8("gridLayout_2"))
        self.AreaNameAttributeLabel_4 = QtGui.QLabel(self.tilesGroup)
        self.AreaNameAttributeLabel_4.setObjectName(_fromUtf8("AreaNameAttributeLabel_4"))
        self.gridLayout_2.addWidget(self.AreaNameAttributeLabel_4, 3, 0, 1, 1)
        self.tileSize = QtGui.QLineEdit(self.tilesGroup)
        self.tileSize.setObjectName(_fromUtf8("tileSize"))
        self.gridLayout_2.addWidget(self.tileSize, 1, 0, 1, 1)
        self.AreaNameAttributeLabel_3 = QtGui.QLabel(self.tilesGroup)
        self.AreaNameAttributeLabel_3.setObjectName(_fromUtf8("AreaNameAttributeLabel_3"))
        self.gridLayout_2.addWidget(self.AreaNameAttributeLabel_3, 0, 0, 1, 1)
        self.bufferSize = QtGui.QLineEdit(self.tilesGroup)
        self.bufferSize.setObjectName(_fromUtf8("bufferSize"))
        self.gridLayout_2.addWidget(self.bufferSize, 4, 0, 1, 1)
        self.verticalLayout.addWidget(self.tilesGroup)
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.helpButton = QtGui.QPushButton(DlgFloodplainDelineation)
        self.helpButton.setObjectName(_fromUtf8("helpButton"))
        self.horizontalLayout.addWidget(self.helpButton)
        self.buttonBox = QtGui.QDialogButtonBox(DlgFloodplainDelineation)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.horizontalLayout.addWidget(self.buttonBox)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.gridLayout.addLayout(self.verticalLayout, 0, 0, 1, 1)
        self.label.setBuddy(self.cboDtm)
        self.AreaNameAttributeLabel.setBuddy(self.cboWsel)

        self.retranslateUi(DlgFloodplainDelineation)
        QtCore.QMetaObject.connectSlotsByName(DlgFloodplainDelineation)

    def retranslateUi(self, DlgFloodplainDelineation):
        DlgFloodplainDelineation.setWindowTitle(_translate("DlgFloodplainDelineation", "Floodplain Delineation", None))
        self.label.setText(_translate("DlgFloodplainDelineation", "DTM raster", None))
        self.AreaNameAttributeLabel.setText(_translate("DlgFloodplainDelineation", "Water surface elevation raster", None))
        self.tilesGroup.setTitle(_translate("DlgFloodplainDelineation", "Tiles", None))
        self.AreaNameAttributeLabel_4.setText(_translate("DlgFloodplainDelineation", "Tile buffer size", None))
        self.tileSize.setText(_translate("DlgFloodplainDelineation", "3000", None))
        self.AreaNameAttributeLabel_3.setText(_translate("DlgFloodplainDelineation", "Tile size", None))
        self.bufferSize.setText(_translate("DlgFloodplainDelineation", "50", None))
        self.helpButton.setText(_translate("DlgFloodplainDelineation", "Help", None))

