# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'rdpParam.ui'
#
# Created: Tue Mar 24 11:27:20 2015
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

class Ui_SetRDParDialog(object):
    def setupUi(self, SetRDParDialog):
        SetRDParDialog.setObjectName(_fromUtf8("SetRDParDialog"))
        SetRDParDialog.resize(312, 125)
        self.widget = QtGui.QWidget(SetRDParDialog)
        self.widget.setGeometry(QtCore.QRect(10, 11, 291, 101))
        self.widget.setObjectName(_fromUtf8("widget"))
        self.gridLayout = QtGui.QGridLayout(self.widget)
        self.gridLayout.setMargin(0)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.buttonBox = QtGui.QDialogButtonBox(self.widget)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridLayout.addWidget(self.buttonBox, 2, 0, 1, 1)
        self.rdpParam = QtGui.QLineEdit(self.widget)
        self.rdpParam.setPlaceholderText(_fromUtf8("0.05"))
        self.rdpParam.setObjectName(_fromUtf8("rdpParam"))
        self.gridLayout.addWidget(self.rdpParam, 1, 0, 1, 1)
        self.label = QtGui.QLabel(self.widget)
        self.label.setObjectName(_fromUtf8("label"))
        self.gridLayout.addWidget(self.label, 0, 0, 1, 1)

        self.retranslateUi(SetRDParDialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), SetRDParDialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), SetRDParDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(SetRDParDialog)

    def retranslateUi(self, SetRDParDialog):
        SetRDParDialog.setWindowTitle(_translate("SetRDParDialog", "Simplification Parameter", None))
        self.label.setText(_translate("SetRDParDialog", "<html><head/><body><p>Set Ramer-Douglas-Peucker Parameter<br/>(see <a href=\"https://en.wikipedia.org/wiki/Ramer%E2%80%93Douglas%E2%80%93Peucker_algorithm\"><span style=\" text-decoration: underline; color:#0000ff;\">Wikipedia explanation</span></a>)</p></body></html>", None))

