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

        self.ui.buttonBox.accepted.connect(self.accept)
        self.ui.buttonBox.rejected.connect(self.reject)
        self.ui.helpButton.clicked.connect(self.displayHelp)
        self.ui.allChbox.toggled.connect(self.allChboxToggled)

        self.checkBoxes = [
            (self.ui.bankLinesChbox, rivdb.BankLines),
            (self.ui.blockedChbox, rivdb.BlockedObs),
            (self.ui.bridgesChbox, rivdb.Bridges),
            (self.ui.flowPathChbox, rivdb.Flowpaths),
            (self.ui.ineffectiveChbox, rivdb.IneffAreas),
            (self.ui.inlineStructChbox, rivdb.InlineStructures),
            (self.ui.streamChbox, rivdb.StreamCenterlines),
            (self.ui.landuseChbox, rivdb.LanduseAreas),
            (self.ui.lateralStructChbox, rivdb.LateralStructures),
            (self.ui.leveeChbox, rivdb.LeveeAlignment),
            (self.ui.storageAreasChbox, rivdb.StorageAreas),
            (self.ui.xsCutLinesChbox, rivdb.XSCutLines)
        ]


    def addInfo(self, text):
        self.rgis.ui.textEdit.append(text)


    def accept(self):
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
        for chbox in self.checkBoxes:
            chbox.setChecked(checked)