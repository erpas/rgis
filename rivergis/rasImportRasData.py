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

import traceback
from os.path import dirname

from hecras import HecrasProject, HecrasPlan
from dlg_rasImportRasData import DlgImportRasData


class WorkerRasImportRasData(QObject):
  '''Worker for loading water surface elevation data from HEC-RAS result file in HDF format.'''
  def __init__(self, rgis):
    QObject.__init__(self)
    self.rgis = rgis
    self.rgis.addInfo("\n<b>Running Load max WSEL from HEC-RAS</b>...\n")
    self.res = None
    try:
      import h5py
    except:
      self.rgis.addInfo("\n\nQGIS couldn't import h5py Python package and doesn't know how to read HEC-RAS result file (HDF). Check your h5py package installation!")
      QMessageBox.warning(rgis, "Load WSEL from HDF", "QGIS couldn't import h5py Python package and doesn't know how to read HEC-RAS result file (HDF). Check your h5py package installation!")
      self.finished.emit(None)
      return
    s = QSettings()
    lastHecrasDir = s.value("rivergis/lastHecRasDir", "")
    prjFilename = QFileDialog.getOpenFileName(rgis, 'Open HEC-RAS Project', directory=lastHecrasDir, filter='HEC-RAS Project Files (*.prj)')
    if not prjFilename:
      self.rgis.addInfo("  Loading max WSEL cancelled.")
      self.finished.emit(None)
      return
    s.setValue("rivergis/lastHecRasDir", dirname(prjFilename))
    self.prj = HecrasProject(prjFilename)
    # check if there is a result file
    if not self.prj.planHdfFiles:
      self.rgis.addInfo("  Project \"%s\" has no HDF result file. Run some computations and try again.\n" % self.prj.title)
      self.finished.emit(self.res)
      return

    # read project's plans data and populate plans combo
    dlg = DlgImportRasData(rgis)
    for i,id in enumerate(self.prj.planHdfFiles):
      plan = HecrasPlan(self.prj,id)
      dlg.ui.planCbo.addItem(plan.name,plan.file)
      if plan.id == self.prj.curPlanId:
        dlg.ui.planCbo.setCurrentIndex(i)

    # show plans dialog
    dlg.exec_()

    self.rgis.addInfo("  Reading results from file:\n  %s" % rgis.curHdfFile)
    self.curPlan = HecrasPlan(self.prj, rgis.curHdfFile[-7:-4])
    self.curPlan.checkHasResults()
    self.hdf = h5py.File(rgis.curHdfFile,'r')
    self.hdfDirname = dirname(rgis.curHdfFile)
    self.killed = False


  def run(self):
    # check if the plan is a 2D model
    self.curPlan.check2D()
    if self.curPlan.is2D:

      flowAreas = self.hdf['/Geometry/2D Flow Areas/Names']
      t = "nr\tx\ty\twsel\ttime\n"
      try:
        for fa in flowAreas:
          if self.killed is True:
            self.finished.emit(self.res)
            break
          fa = fa.strip()
          cme = self.hdf['/Geometry/2D Flow Areas/%s/Cells Minimum Elevation' % fa]
          cfoi = self.hdf['/Geometry/2D Flow Areas/%s/Cells Face and Orientation Info' % fa]
          summary = self.hdf['/Results/Unsteady/Output/Output Blocks/Base Output/Summary Output/2D Flow Areas/%s/' % fa]
          wselMax = summary['Maximum Water Surface'][0]
          timeMax = summary['Maximum Water Surface'][1]
          ccc = self.hdf['/Geometry/2D Flow Areas/%s/Cells Center Coordinate' % fa]
          cccLen = float(len(ccc))
          pr = 0

          for i, cc in enumerate(ccc):
            if self.killed is True:
              self.finished.emit(self.res)
              break
            wsel = wselMax[i]
            grel = cme[i]
            if cfoi[i][1] == 1: # point on the boundary
              continue
            if wsel - 0.01 <= grel: # dry cell
              continue
            stime = timeMax[i]
            t += "%i\t%.2f\t%.2f\t%.2f\t%.4f\n" % (i, cc[0], cc[1], wsel, stime)
            if  100*i / cccLen > pr+1:
              pr +=1
              self.progress.emit( pr )

        wselFile = open("%s/wselMax.csv" % self.hdfDirname, "w")
        wselFile.write(t)
        wselFile.close()
        self.rgis.addInfo("  Loading maximum WSEL to a temporary layer...")

        vrt = '''<OGRVRTDataSource>
            <OGRVRTLayer name="wselMax">
                <SrcDataSource relativeToVRT="1">wselmax.csv</SrcDataSource>
                <GeometryType>wkbPoint</GeometryType>
                <LayerSRS>%s</LayerSRS>
                <GeometryField encoding="PointFromColumns" x="x" y="y"/>
            </OGRVRTLayer>
        </OGRVRTDataSource>''' % self.rgis.wselCrs.authid()

        vrtFile = open("%s/wselMax.vrt" % self.hdfDirname, "w")
        vrtFile.write(vrt)
        vrtFile.close()
        self.hdf.close()
        #self.res = processing.runalg("gdalogr:convertformat","%s/wselMax.vrt" % self.hdfDirname,0,"",None)
        self.res = QgsVectorLayer("%s/wselMax.vrt" % self.hdfDirname, "max WSEL", "ogr")
        self.res = "%s/wselMax.vrt" % self.hdfDirname

        self.rgis.addInfo("  Done!\n  Review and save the results.\n\n")

      except Exception, e:
        # forward the exception upstream
        self.error.emit(e, traceback.format_exc())

      self.finished.emit(self.res)

    else: # 1D case

      pass

  def kill(self):
    self.killed = True

  finished = pyqtSignal(object)
  error = pyqtSignal(Exception, basestring)
  progress = pyqtSignal(float)




