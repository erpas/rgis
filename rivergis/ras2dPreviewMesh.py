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
from os.path import join
import processing

def ras2dPreviewMesh(rgis):
  """Loads the mesh points to the canvas and builds Voronoi polygons"""
  areas = None
  if not rgis.crs.postgisSrid():
    rgis.addInfo(rgis, '\n  Default CRS not set. Choose a projection and try again.\n')
    return
  u1 = QgsDataSourceURI()
  u1.setConnection(rgis.host, rgis.port, rgis.database, rgis.user, rgis.passwd)
  u1.setDataSource(rgis.schema, "mesh_pts", "geom")
  # uri.setSrid(str(rgis.crs.postgisSrid()))
  mesh_pts = QgsVectorLayer(u1.uri(), "Mesh points", "postgres")
  voronoi = processing.runalg("qgis:voronoipolygons",mesh_pts,3,None)
  QgsMapLayerRegistry.instance().addMapLayers([mesh_pts])

  # try to load the 2D Area polygon and clip the Voronoi diagram
  try:
    u2 = QgsDataSourceURI()
    u2.setConnection(rgis.host, rgis.port, rgis.database, rgis.user, rgis.passwd)
    u2.setDataSource(rgis.schema, "areas2d", "geom")
    areas = QgsVectorLayer(u2.uri(), "areas2d", "postgres")
    # TODO: construct voronoi polygons separately for each 2d mesh area
    voronoiClip = processing.runalg("qgis:clip",voronoi['OUTPUT'],areas,None)
    voronoiClipLayer = QgsVectorLayer(voronoiClip['OUTPUT'], "Mesh preview", "ogr")
    QgsMapLayerRegistry.instance().addMapLayers([voronoiClipLayer])

  except:
    voronoiLayer = QgsVectorLayer(voronoi['OUTPUT'], "Mesh preview", "ogr")
    QgsMapLayerRegistry.instance().addMapLayers([voronoiLayer])

  # change layers' style
  root = QgsProject.instance().layerTreeRoot()
  for child in root.children():
    if isinstance(child, QgsLayerTreeLayer):
      if child.layerName() == 'Mesh preview':
        stylePath = join(rgis.rivergisPath,'styles/ras2dmesh.qml')
        child.layer().loadNamedStyle(stylePath)
        rgis.iface.legendInterface().refreshLayerSymbology(child.layer())
        rgis.iface.mapCanvas().refresh()
      elif child.layerName() == 'Mesh points':
        stylePath = join(rgis.rivergisPath,'styles/ras2dMeshPts.qml')
        child.layer().loadNamedStyle(stylePath)
        rgis.iface.legendInterface().refreshLayerSymbology(child.layer())
        rgis.iface.mapCanvas().refresh()



