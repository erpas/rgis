# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui/ui_dtmSetup.ui'
#
# Created: Thu Oct 22 12:54:07 2015
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

class Ui_DTMSelectionDialog(object):
    def setupUi(self, DTMSelectionDialog):
        DTMSelectionDialog.setObjectName(_fromUtf8("DTMSelectionDialog"))
        DTMSelectionDialog.resize(272, 394)
        DTMSelectionDialog.setLocale(QtCore.QLocale(QtCore.QLocale.English, QtCore.QLocale.UnitedStates))
        self.gridLayout = QtGui.QGridLayout(DTMSelectionDialog)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.verticalLayout = QtGui.QVBoxLayout()
        self.verticalLayout.setContentsMargins(-1, -1, -1, 0)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.label = QtGui.QLabel(DTMSelectionDialog)
        self.label.setObjectName(_fromUtf8("label"))
        self.verticalLayout.addWidget(self.label)
        self.allChbox = QtGui.QCheckBox(DTMSelectionDialog)
        self.allChbox.setObjectName(_fromUtf8("allChbox"))
        self.verticalLayout.addWidget(self.allChbox)
        self.dtmListView = QtGui.QListView(DTMSelectionDialog)
        self.dtmListView.setSelectionMode(QtGui.QAbstractItemView.MultiSelection)
        self.dtmListView.setSelectionBehavior(QtGui.QAbstractItemView.SelectItems)
        self.dtmListView.setObjectName(_fromUtf8("dtmListView"))
        self.verticalLayout.addWidget(self.dtmListView)
        self.horizontalLayout_2 = QtGui.QHBoxLayout()
        self.horizontalLayout_2.setContentsMargins(-1, -1, -1, 20)
        self.horizontalLayout_2.setObjectName(_fromUtf8("horizontalLayout_2"))
        self.label_2 = QtGui.QLabel(DTMSelectionDialog)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.horizontalLayout_2.addWidget(self.label_2)
        self.chunksize = QtGui.QLineEdit(DTMSelectionDialog)
        self.chunksize.setObjectName(_fromUtf8("chunksize"))
        self.horizontalLayout_2.addWidget(self.chunksize)
        self.verticalLayout.addLayout(self.horizontalLayout_2)
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setContentsMargins(-1, 0, -1, -1)
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.helpButton = QtGui.QToolButton(DTMSelectionDialog)
        self.helpButton.setMinimumSize(QtCore.QSize(40, 25))
        self.helpButton.setObjectName(_fromUtf8("helpButton"))
        self.horizontalLayout.addWidget(self.helpButton)
        self.buttonBox = QtGui.QDialogButtonBox(DTMSelectionDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.horizontalLayout.addWidget(self.buttonBox)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.gridLayout.addLayout(self.verticalLayout, 0, 0, 1, 1)

        self.retranslateUi(DTMSelectionDialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), DTMSelectionDialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), DTMSelectionDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(DTMSelectionDialog)

    def retranslateUi(self, DTMSelectionDialog):
        DTMSelectionDialog.setWindowTitle(_translate("DTMSelectionDialog", "DTM(s) Selection", None))
        self.label.setText(_translate("DTMSelectionDialog", "Choose DTM(s) for cross-section intepolation", None))
        self.allChbox.setText(_translate("DTMSelectionDialog", "Select all", None))
        self.label_2.setToolTip(_translate("DTMSelectionDialog", "<html><head/><body><p>Maximum number of raster cell values fetched at once by a database query. </p><p>If the number of raster cells exceeds the chunk size they are fetched successively.</p></body></html>", None))
        self.label_2.setText(_translate("DTMSelectionDialog", "Chunk size", None))
        self.chunksize.setToolTip(_translate("DTMSelectionDialog", "<html><head/><body><p>Maximum number of raster cell values fetched at once by a database query. </p><p>If the number of raster cells exceeds the chunk size they are fetched successively.</p></body></html>", None))
        self.chunksize.setText(_translate("DTMSelectionDialog", "10000", None))
        self.helpButton.setText(_translate("DTMSelectionDialog", "Help", None))

