# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui/ui_dtmSetup.ui'
#
# Created: Sun Sep 20 13:29:07 2015
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
        DTMSelectionDialog.resize(294, 330)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(_fromUtf8(":/rivergis/icons/ras1dDTMSetup.svg")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        DTMSelectionDialog.setWindowIcon(icon)
        DTMSelectionDialog.setLocale(QtCore.QLocale(QtCore.QLocale.English, QtCore.QLocale.UnitedStates))
        self.gridLayout = QtGui.QGridLayout(DTMSelectionDialog)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.label = QtGui.QLabel(DTMSelectionDialog)
        self.label.setObjectName(_fromUtf8("label"))
        self.gridLayout.addWidget(self.label, 0, 0, 1, 1)
        self.dtmListView = QtGui.QListView(DTMSelectionDialog)
        self.dtmListView.setSelectionMode(QtGui.QAbstractItemView.MultiSelection)
        self.dtmListView.setSelectionBehavior(QtGui.QAbstractItemView.SelectItems)
        self.dtmListView.setObjectName(_fromUtf8("dtmListView"))
        self.gridLayout.addWidget(self.dtmListView, 2, 0, 1, 1)
        self.allChbox = QtGui.QCheckBox(DTMSelectionDialog)
        self.allChbox.setObjectName(_fromUtf8("allChbox"))
        self.gridLayout.addWidget(self.allChbox, 1, 0, 1, 1)
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setContentsMargins(-1, 20, -1, -1)
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
        self.gridLayout.addLayout(self.horizontalLayout, 3, 0, 1, 1)

        self.retranslateUi(DTMSelectionDialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), DTMSelectionDialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), DTMSelectionDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(DTMSelectionDialog)

    def retranslateUi(self, DTMSelectionDialog):
        DTMSelectionDialog.setWindowTitle(_translate("DTMSelectionDialog", "DTM(s) Selection", None))
        self.label.setText(_translate("DTMSelectionDialog", "Choose DTM(s) for cross-section intepolation", None))
        self.allChbox.setText(_translate("DTMSelectionDialog", "Select all", None))
        self.helpButton.setText(_translate("DTMSelectionDialog", "Help", None))

import resources_rc
