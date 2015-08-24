# -*- coding: utf-8 -*-
"""
/***************************************************************************
 RiverGisDialog
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
"""
from os.path import dirname
import logging

logfile = dirname(__file__)+"/log.txt"
logging.basicConfig(filename=logfile, filemode='w', level=logging.DEBUG)
