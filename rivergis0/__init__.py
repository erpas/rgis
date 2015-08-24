# -*- coding: utf-8 -*-
"""
/***************************************************************************
 RiverGis
                                 A QGIS plugin
 Helps you build and manage hydraulic models in Mike 11 by DHI
                             -------------------
        begin                : 2013-11-06
        copyright            : (C) 2013 by Radoslaw Pasiok
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
 This script initializes the plugin, making it known to QGIS.
"""

def classFactory(iface):
  # load RiverGis class from file RiverGis
  from rivergis0 import RiverGis0
  return RiverGis0(iface)
