# -*- coding: utf-8 -*-
"""
/***************************************************************************
 HECGeoRAS
                                 A QGIS plugin
 HEC-RAS tools for QGIS
                             -------------------
        begin                : 2015-07-06
        copyright            : (C) 2015 by RiverGIS Group
        email                : damnback333@gmail.com
        git sha              : $Format:%H$
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


# noinspection PyPep8Naming
def classFactory(iface):  # pylint: disable=invalid-name
    """Load HECGeoRAS class from file HECGeoRAS.

    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
    #
    from .hecgeoras import HECGeoRAS
    return HECGeoRAS(iface)
