# -*- coding: utf-8 -*-

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *
from qgis.gui import *
from qgis.utils import *
import river_database as rivdb
import hecobjects as heco

from ui.ui_rasCreateRASLayers import *

class DlgCreateRasLayers(QDialog):
    def __init__(self, parent=None):
        QDialog.__init__(self, parent)
        self.ui = Ui_CreateRasLayers()
        self.ui.setupUi(self)
        self.rgis = parent
        self.rdb = parent.rdb

        self.ui.buttonBox.accepted.connect(self.acceptDialog)
        self.ui.buttonBox.rejected.connect(self.reject)
        self.ui.helpButton.clicked.connect(self.displayHelp)
        self.ui.allChbox.toggled.connect(self.allChboxToggled)

        self.checkBoxes = [
            (self.ui.bankLinesChbox, heco.BankLines),
            (self.ui.blockedChbox, heco.BlockedObs),
            (self.ui.bridgesChbox, heco.Bridges),
            (self.ui.flowPathChbox, heco.Flowpaths),
            (self.ui.ineffectiveChbox, heco.IneffAreas),
            (self.ui.inlineStructChbox, heco.InlineStructures),
            (self.ui.streamChbox, heco.StreamCenterlines),
            (self.ui.landuseChbox, heco.LanduseAreas),
            (self.ui.lateralStructChbox, heco.LateralStructures),
            (self.ui.leveeChbox, heco.LeveeAlignment),
            (self.ui.storageAreasChbox, heco.StorageAreas),
            (self.ui.xsCutLinesChbox, heco.XSCutLines)
        ]


    def addInfo(self, text):
        self.rgis.ui.textEdit.append(text)


    def acceptDialog(self):
        QApplication.setOverrideCursor(Qt.WaitCursor)
        self.addInfo('<br><b>Running Create RAS Layers and Tables...</b>')
        tablesToCreate = []
        tablesToCreateTxt = ''
        for chbox, hecobj_class in self.checkBoxes:
            if chbox.isChecked():
                tablesToCreate.append(hecobj_class)
                tablesToCreateTxt += '    {0}\n'.format(chbox.text())
                a = self.rdb.process_hecobject(hecobj_class, 'pg_create_table')
                self.rdb.add_to_view(a)

        self.addInfo('Following tables were created:\n%s' % tablesToCreateTxt)
        QApplication.setOverrideCursor(Qt.ArrowCursor)
        QDialog.accept(self)

    def displayHelp(self):
        pass


    def allChboxToggled(self):
        checked = self.ui.allChbox.isChecked()
        for chbox, hecobj_class in self.checkBoxes:
            chbox.setChecked(checked)