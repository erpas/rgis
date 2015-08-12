# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui_createWaterSurfRaster.ui'
#
# Created: Fri Jan 30 18:14:33 2015
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

class Ui_DlgCreateWaterSurfRaster(object):
    def setupUi(self, DlgCreateWaterSurfRaster):
        DlgCreateWaterSurfRaster.setObjectName(_fromUtf8("DlgCreateWaterSurfRaster"))
        DlgCreateWaterSurfRaster.resize(294, 305)
        self.gridLayout = QtGui.QGridLayout(DlgCreateWaterSurfRaster)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.verticalLayout = QtGui.QVBoxLayout()
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.label = QtGui.QLabel(DlgCreateWaterSurfRaster)
        self.label.setObjectName(_fromUtf8("label"))
        self.verticalLayout.addWidget(self.label)
        self.cboPoints = QtGui.QComboBox(DlgCreateWaterSurfRaster)
        self.cboPoints.setAcceptDrops(False)
        self.cboPoints.setObjectName(_fromUtf8("cboPoints"))
        self.verticalLayout.addWidget(self.cboPoints)
        self.AreaNameAttributeLabel = QtGui.QLabel(DlgCreateWaterSurfRaster)
        self.AreaNameAttributeLabel.setObjectName(_fromUtf8("AreaNameAttributeLabel"))
        self.verticalLayout.addWidget(self.AreaNameAttributeLabel)
        self.cboWselAttr = QtGui.QComboBox(DlgCreateWaterSurfRaster)
        self.cboWselAttr.setObjectName(_fromUtf8("cboWselAttr"))
        self.verticalLayout.addWidget(self.cboWselAttr)
        self.tilesGroup = QtGui.QGroupBox(DlgCreateWaterSurfRaster)
        self.tilesGroup.setObjectName(_fromUtf8("tilesGroup"))
        self.gridLayout_2 = QtGui.QGridLayout(self.tilesGroup)
        self.gridLayout_2.setObjectName(_fromUtf8("gridLayout_2"))
        self.cellSize = QtGui.QLineEdit(self.tilesGroup)
        self.cellSize.setObjectName(_fromUtf8("cellSize"))
        self.gridLayout_2.addWidget(self.cellSize, 1, 0, 1, 1)
        self.AreaNameAttributeLabel_2 = QtGui.QLabel(self.tilesGroup)
        self.AreaNameAttributeLabel_2.setObjectName(_fromUtf8("AreaNameAttributeLabel_2"))
        self.gridLayout_2.addWidget(self.AreaNameAttributeLabel_2, 0, 0, 1, 1)
        self.AreaNameAttributeLabel_4 = QtGui.QLabel(self.tilesGroup)
        self.AreaNameAttributeLabel_4.setObjectName(_fromUtf8("AreaNameAttributeLabel_4"))
        self.gridLayout_2.addWidget(self.AreaNameAttributeLabel_4, 5, 0, 1, 1)
        self.tileSize = QtGui.QLineEdit(self.tilesGroup)
        self.tileSize.setObjectName(_fromUtf8("tileSize"))
        self.gridLayout_2.addWidget(self.tileSize, 3, 0, 1, 1)
        self.AreaNameAttributeLabel_3 = QtGui.QLabel(self.tilesGroup)
        self.AreaNameAttributeLabel_3.setObjectName(_fromUtf8("AreaNameAttributeLabel_3"))
        self.gridLayout_2.addWidget(self.AreaNameAttributeLabel_3, 2, 0, 1, 1)
        self.bufferSize = QtGui.QLineEdit(self.tilesGroup)
        self.bufferSize.setObjectName(_fromUtf8("bufferSize"))
        self.gridLayout_2.addWidget(self.bufferSize, 6, 0, 1, 1)
        self.verticalLayout.addWidget(self.tilesGroup)
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.helpButton = QtGui.QPushButton(DlgCreateWaterSurfRaster)
        self.helpButton.setObjectName(_fromUtf8("helpButton"))
        self.horizontalLayout.addWidget(self.helpButton)
        self.buttonBox = QtGui.QDialogButtonBox(DlgCreateWaterSurfRaster)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.horizontalLayout.addWidget(self.buttonBox)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.gridLayout.addLayout(self.verticalLayout, 0, 0, 1, 1)
        self.label.setBuddy(self.cboPoints)
        self.AreaNameAttributeLabel.setBuddy(self.cboWselAttr)

        self.retranslateUi(DlgCreateWaterSurfRaster)
        QtCore.QMetaObject.connectSlotsByName(DlgCreateWaterSurfRaster)

    def retranslateUi(self, DlgCreateWaterSurfRaster):
        DlgCreateWaterSurfRaster.setWindowTitle(_translate("DlgCreateWaterSurfRaster", "Create WSEL Raster", None))
        self.label.setText(_translate("DlgCreateWaterSurfRaster", "Water surface elevation point layer", None))
        self.AreaNameAttributeLabel.setText(_translate("DlgCreateWaterSurfRaster", "Water surface elevation attribute", None))
        self.tilesGroup.setTitle(_translate("DlgCreateWaterSurfRaster", "Tiles", None))
        self.cellSize.setText(_translate("DlgCreateWaterSurfRaster", "5", None))
        self.AreaNameAttributeLabel_2.setText(_translate("DlgCreateWaterSurfRaster", "Target raster cell size", None))
        self.AreaNameAttributeLabel_4.setText(_translate("DlgCreateWaterSurfRaster", "Tile buffer size (map units)", None))
        self.tileSize.setText(_translate("DlgCreateWaterSurfRaster", "2000", None))
        self.AreaNameAttributeLabel_3.setText(_translate("DlgCreateWaterSurfRaster", "Tile size (map units)", None))
        self.bufferSize.setText(_translate("DlgCreateWaterSurfRaster", "100", None))
        self.helpButton.setText(_translate("DlgCreateWaterSurfRaster", "Help", None))

