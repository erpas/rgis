# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui/ui_rasWaterSurfaceGeneration.ui'
#
# Created: Thu Oct 22 10:50:07 2015
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

class Ui_DlgWaterSurfaceGeneration(object):
    def setupUi(self, DlgWaterSurfaceGeneration):
        DlgWaterSurfaceGeneration.setObjectName(_fromUtf8("DlgWaterSurfaceGeneration"))
        DlgWaterSurfaceGeneration.resize(386, 260)
        self.gridLayout = QtGui.QGridLayout(DlgWaterSurfaceGeneration)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.verticalLayout = QtGui.QVBoxLayout()
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.label = QtGui.QLabel(DlgWaterSurfaceGeneration)
        self.label.setObjectName(_fromUtf8("label"))
        self.verticalLayout.addWidget(self.label)
        self.cboPoints = QtGui.QComboBox(DlgWaterSurfaceGeneration)
        self.cboPoints.setAcceptDrops(False)
        self.cboPoints.setObjectName(_fromUtf8("cboPoints"))
        self.verticalLayout.addWidget(self.cboPoints)
        self.AreaNameAttributeLabel = QtGui.QLabel(DlgWaterSurfaceGeneration)
        self.AreaNameAttributeLabel.setObjectName(_fromUtf8("AreaNameAttributeLabel"))
        self.verticalLayout.addWidget(self.AreaNameAttributeLabel)
        self.cboWselAttr = QtGui.QComboBox(DlgWaterSurfaceGeneration)
        self.cboWselAttr.setObjectName(_fromUtf8("cboWselAttr"))
        self.verticalLayout.addWidget(self.cboWselAttr)
        self.AreaNameAttributeLabel_2 = QtGui.QLabel(DlgWaterSurfaceGeneration)
        self.AreaNameAttributeLabel_2.setObjectName(_fromUtf8("AreaNameAttributeLabel_2"))
        self.verticalLayout.addWidget(self.AreaNameAttributeLabel_2)
        self.cellSize = QtGui.QLineEdit(DlgWaterSurfaceGeneration)
        self.cellSize.setObjectName(_fromUtf8("cellSize"))
        self.verticalLayout.addWidget(self.cellSize)
        self.horizontalLayout_3 = QtGui.QHBoxLayout()
        self.horizontalLayout_3.setContentsMargins(-1, 0, -1, -1)
        self.horizontalLayout_3.setObjectName(_fromUtf8("horizontalLayout_3"))
        self.label_3 = QtGui.QLabel(DlgWaterSurfaceGeneration)
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.horizontalLayout_3.addWidget(self.label_3)
        self.engineQgisBtn = QtGui.QRadioButton(DlgWaterSurfaceGeneration)
        self.engineQgisBtn.setChecked(True)
        self.engineQgisBtn.setObjectName(_fromUtf8("engineQgisBtn"))
        self.horizontalLayout_3.addWidget(self.engineQgisBtn)
        self.engineScipyBtn = QtGui.QRadioButton(DlgWaterSurfaceGeneration)
        self.engineScipyBtn.setObjectName(_fromUtf8("engineScipyBtn"))
        self.horizontalLayout_3.addWidget(self.engineScipyBtn)
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout_3.addItem(spacerItem)
        self.verticalLayout.addLayout(self.horizontalLayout_3)
        self.horizontalLayout_2 = QtGui.QHBoxLayout()
        self.horizontalLayout_2.setObjectName(_fromUtf8("horizontalLayout_2"))
        self.label_2 = QtGui.QLabel(DlgWaterSurfaceGeneration)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.horizontalLayout_2.addWidget(self.label_2)
        self.interpTypeCbo = QtGui.QComboBox(DlgWaterSurfaceGeneration)
        self.interpTypeCbo.setObjectName(_fromUtf8("interpTypeCbo"))
        self.horizontalLayout_2.addWidget(self.interpTypeCbo)
        self.verticalLayout.addLayout(self.horizontalLayout_2)
        self.onlySelectedCheckBox = QtGui.QCheckBox(DlgWaterSurfaceGeneration)
        self.onlySelectedCheckBox.setEnabled(True)
        self.onlySelectedCheckBox.setChecked(True)
        self.onlySelectedCheckBox.setObjectName(_fromUtf8("onlySelectedCheckBox"))
        self.verticalLayout.addWidget(self.onlySelectedCheckBox)
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.helpButton = QtGui.QPushButton(DlgWaterSurfaceGeneration)
        self.helpButton.setObjectName(_fromUtf8("helpButton"))
        self.horizontalLayout.addWidget(self.helpButton)
        self.buttonBox = QtGui.QDialogButtonBox(DlgWaterSurfaceGeneration)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.horizontalLayout.addWidget(self.buttonBox)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.gridLayout.addLayout(self.verticalLayout, 0, 0, 1, 1)

        self.retranslateUi(DlgWaterSurfaceGeneration)
        QtCore.QMetaObject.connectSlotsByName(DlgWaterSurfaceGeneration)

    def retranslateUi(self, DlgWaterSurfaceGeneration):
        DlgWaterSurfaceGeneration.setWindowTitle(_translate("DlgWaterSurfaceGeneration", "Water Surface Generation", None))
        self.label.setText(_translate("DlgWaterSurfaceGeneration", "Water surface elevation point layer", None))
        self.AreaNameAttributeLabel.setText(_translate("DlgWaterSurfaceGeneration", "Water surface elevation attribute", None))
        self.AreaNameAttributeLabel_2.setText(_translate("DlgWaterSurfaceGeneration", "WSEL raster cell size", None))
        self.cellSize.setText(_translate("DlgWaterSurfaceGeneration", "5", None))
        self.label_3.setText(_translate("DlgWaterSurfaceGeneration", "Interpolation engine: ", None))
        self.engineQgisBtn.setText(_translate("DlgWaterSurfaceGeneration", "QGIS (QgsTinInterpolator)", None))
        self.engineScipyBtn.setText(_translate("DlgWaterSurfaceGeneration", "scipy", None))
        self.label_2.setText(_translate("DlgWaterSurfaceGeneration", "Interpolation type: ", None))
        self.onlySelectedCheckBox.setText(_translate("DlgWaterSurfaceGeneration", "Use only selected points", None))
        self.helpButton.setText(_translate("DlgWaterSurfaceGeneration", "Help", None))

