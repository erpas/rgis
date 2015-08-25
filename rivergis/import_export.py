# -*- coding: utf-8 -*-

"""
/***************************************************************************
Name                 : RiverGIS
Description          : HEC-RAS tools for QGIS
Date                 : January, 2015
copyright            : (C) 2015 by RiverGIS Group
email                : rpasiok@gmail.com
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *
from qgis.utils import *

from qgis.gui import QgsMessageBar
from dlg_importRiverFromIsokp import *

def importRiverFromIsokp(rgis):
  rgis.addInfo('\n<b>Running Import River Data From ISOKP Database</b>' )
  db = rgis.tree.currentDatabase()
  if db is None:
    rgis.addInfo(rgis, "No database selected or you are not connected to it.")
    return

  layers = DlgImportRiverFromIsokp(rgis)
  layers.show()
  if layers.exec_() == QDialog.Accepted:
    riv_id = layers.riv_id
  elif layers.exec_() == QDialog.Rejected:
    print "rejected :-)"
    # layers.reject()
    return