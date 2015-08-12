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

try:
  from . import resources_rc
except ImportError:
  pass

class RiverGISPlugin:
  def __init__(self, iface):
    self.iface = iface
    self.dlg = None

  def initGui(self): 
    self.action = QAction( QIcon(":/rivergis/icons/rivergis.svg"), QApplication.translate("RiverGIS","RiverGIS"), self.iface.mainWindow() )
    self.action.setObjectName("rivergis")
    QObject.connect( self.action, SIGNAL( "triggered()" ), self.run )
    # Add toolbar button and menu item
    self.iface.addToolBarIcon(self.action)
    self.iface.addPluginToMenu( QApplication.translate("RiverGIS","RiverGIS"), self.action )

  def unload(self):
    # Remove the plugin menu item and icon
    self.iface.removeToolBarIcon(self.action)
    self.iface.removePluginMenu( QApplication.translate("RiverGIS","RiverGIS"), self.action )

    if self.dlg != None:
      self.dlg.close()

  def run(self):
    # keep opened only one instance
    if self.dlg == None:
      from rivergis import RiverGIS
      self.dlg = RiverGIS(self.iface)
      QObject.connect(self.dlg, SIGNAL("destroyed(QObject *)"), self.onDestroyed)
    self.dlg.show()
    self.dlg.raise_()
    self.dlg.setWindowState( self.dlg.windowState() & ~Qt.WindowMinimized )
    self.dlg.activateWindow()

  def onDestroyed(self, obj):
    self.dlg = None
