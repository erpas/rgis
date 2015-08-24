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

import processing

def ras2dPreviewMesh(rgis):
  """Loads the mesh points to the canvas and builds Voronoi polygons"""

  if not rgis.crs.postgisSrid():
    rgis.addInfo(rgis, '\n  Default CRS not set. Choose a projection and try again.\n')
    return
  uri = QgsDataSourceURI()
  uri.setConnection(rgis.host, rgis.port, rgis.database, rgis.user, rgis.passwd)
  uri.setDataSource(rgis.schema, "mesh_pts", "geom")
  uri.setSrid(str(rgis.crs.postgisSrid()))
  mesh_pts = QgsVectorLayer(uri.uri(), "mesh_pts", "postgres")
  QgsMapLayerRegistry.instance().addMapLayers([mesh_pts])
  # TODO: add some style definition

  voronoi = processing.runalg("qgis:voronoipolygons",mesh_pts,100,None)
  # processing.runalg("gdalogr:clipvectorsbypolygon",voronoi,"d:/cmp4/POTENCJALNE/L10/gis/obszar2d.shp","",None)
  processing.load(voronoi['OUTPUT'], "Mesh preview")


  

