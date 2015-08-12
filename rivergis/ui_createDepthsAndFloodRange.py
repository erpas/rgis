# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui_createDepthsAndFloodRange.ui'
#
# Created: Thu Mar 05 16:28:16 2015
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

class Ui_DlgCreateDepthsAndFloodRange(object):
    def setupUi(self, DlgCreateDepthsAndFloodRange):
        DlgCreateDepthsAndFloodRange.setObjectName(_fromUtf8("DlgCreateDepthsAndFloodRange"))
        DlgCreateDepthsAndFloodRange.resize(294, 260)
        self.gridLayout = QtGui.QGridLayout(DlgCreateDepthsAndFloodRange)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.verticalLayout = QtGui.QVBoxLayout()
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.label = QtGui.QLabel(DlgCreateDepthsAndFloodRange)
        self.label.setObjectName(_fromUtf8("label"))
        self.verticalLayout.addWidget(self.label)
        self.cboDtm = QtGui.QComboBox(DlgCreateDepthsAndFloodRange)
        self.cboDtm.setAcceptDrops(False)
        self.cboDtm.setObjectName(_fromUtf8("cboDtm"))
        self.verticalLayout.addWidget(self.cboDtm)
        self.AreaNameAttributeLabel = QtGui.QLabel(DlgCreateDepthsAndFloodRange)
        self.AreaNameAttributeLabel.setObjectName(_fromUtf8("AreaNameAttributeLabel"))
        self.verticalLayout.addWidget(self.AreaNameAttributeLabel)
        self.cboWsel = QtGui.QComboBox(DlgCreateDepthsAndFloodRange)
        self.cboWsel.setObjectName(_fromUtf8("cboWsel"))
        self.verticalLayout.addWidget(self.cboWsel)
        self.tilesGroup = QtGui.QGroupBox(DlgCreateDepthsAndFloodRange)
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
        self.helpButton = QtGui.QPushButton(DlgCreateDepthsAndFloodRange)
        self.helpButton.setObjectName(_fromUtf8("helpButton"))
        self.horizontalLayout.addWidget(self.helpButton)
        self.buttonBox = QtGui.QDialogButtonBox(DlgCreateDepthsAndFloodRange)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.horizontalLayout.addWidget(self.buttonBox)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.gridLayout.addLayout(self.verticalLayout, 0, 0, 1, 1)
        self.label.setBuddy(self.cboDtm)
        self.AreaNameAttributeLabel.setBuddy(self.cboWsel)

        self.retranslateUi(DlgCreateDepthsAndFloodRange)
        QtCore.QMetaObject.connectSlotsByName(DlgCreateDepthsAndFloodRange)

    def retranslateUi(self, DlgCreateDepthsAndFloodRange):
        DlgCreateDepthsAndFloodRange.setWindowTitle(_translate("DlgCreateDepthsAndFloodRange", "Form", None))
        self.label.setText(_translate("DlgCreateDepthsAndFloodRange", "DTM raster", None))
        self.AreaNameAttributeLabel.setText(_translate("DlgCreateDepthsAndFloodRange", "Water surface elevation raster", None))
        self.tilesGroup.setTitle(_translate("DlgCreateDepthsAndFloodRange", "Tiles", None))
        self.AreaNameAttributeLabel_4.setText(_translate("DlgCreateDepthsAndFloodRange", "Tile buffer size", None))
        self.tileSize.setText(_translate("DlgCreateDepthsAndFloodRange", "3000", None))
        self.AreaNameAttributeLabel_3.setText(_translate("DlgCreateDepthsAndFloodRange", "Tile size", None))
        self.bufferSize.setText(_translate("DlgCreateDepthsAndFloodRange", "50", None))
        self.helpButton.setText(_translate("DlgCreateDepthsAndFloodRange", "Help", None))

