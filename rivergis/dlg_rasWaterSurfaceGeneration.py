# -*- coding: utf-8 -*-

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *
from qgis.gui import *
from qgis.utils import *
from osgeo import osr
from osgeo import gdal
import numpy as np
import traceback
import uuid
from os.path import expanduser, join
from subprocess import call

from ui_rasWaterSurfaceGeneration import *

class DlgRasWaterSurfaceGeneration(QDialog):
  def __init__(self, parent=None):
    QDialog.__init__(self, parent)
    self.ui = Ui_DlgWaterSurfaceGeneration()
    self.ui.setupUi(self)
    self.qras = parent
    QObject.connect(self.ui.buttonBox, SIGNAL("accepted()"), self.accept)
    QObject.connect(self.ui.buttonBox, SIGNAL("rejected()"), self.rejectDlg)
    QObject.connect(self.ui.helpButton, SIGNAL("clicked()"), self.displayHelp)
    QObject.connect(self.ui.cboPoints,SIGNAL("currentIndexChanged(int)"),self.cboPointsChanged)
    QObject.connect(self.ui.engineQgisBtn,SIGNAL("toggled(bool)"),self.updateInterpTypeCbo)
    self.ui.cboPoints.addItem("")
    self.populatePointsCombo()
    self.ptsLayer = None
    self.updateInterpTypeCbo()

  def addInfo(self, text):
    self.qras.ui.textEdit.append(text)

  def array2raster(self, newRasterfn,rasterOrigin,pixelWidth,pixelHeight,array):
    cols = array.shape[1]
    rows = array.shape[0]
    originX = rasterOrigin[0]
    originY = rasterOrigin[1]
    driver = gdal.GetDriverByName('GTiff')
    outRaster = driver.Create(newRasterfn, cols, rows, 1, gdal.GDT_Float32)
    outRaster.SetGeoTransform((originX, pixelWidth, 0, originY, 0, pixelHeight))
    outband = outRaster.GetRasterBand(1)
    outband.WriteArray(array)
    outRasterSRS = osr.SpatialReference()
    outRasterSRS.ImportFromEPSG(2180)
    outRaster.SetProjection(outRasterSRS.ExportToWkt())
    outband.FlushCache()

  def rejectDlg(self):
    self.addInfo('  Loading max WSEL failed or was cancelled, check the log...')
    QApplication.setOverrideCursor(Qt.ArrowCursor)
    self.reject()

  def accept(self ):
    from qgis.analysis import *
    import processing
    # check input
    if not self.ptsLayer: # no src layer
      return
    QApplication.setOverrideCursor(Qt.WaitCursor)

    ptsLayer = self.ptsLayer
    Water_level_attribute = self.ui.cboWselAttr.currentIndex() - 1
    Cell_size = float(self.ui.cellSize.text())
    onlySelected = self.ui.onlySelectedCheckBox.isChecked()
    qgisEngine = self.ui.engineQgisBtn.isChecked()
    if qgisEngine:
      print self.ui.interpTypeCbo.currentIndex()
      if self.ui.interpTypeCbo.currentIndex() == 0:
        intMethod = QgsTINInterpolator.Linear
        resRaster = 'WSEL_QgsTINInterp_linear_%i' % int(Cell_size)
      else:
        intMethod = QgsTINInterpolator.CloughTocher
        resRaster = 'WSEL_QgsTINInterp_CloughToucher_%i' % int(Cell_size)
    else: # scipy engine
      try:
        from scipy.interpolate import griddata
      except ImportError:
        self.addInfo('\n\nScipy Python package not installed. Use OSGeo4W installer in advanced mode or execute pip install scipy.' )
        return
      print self.ui.interpTypeCbo.currentIndex()
      if self.ui.interpTypeCbo.currentIndex() == 0:
        intMethod = 'linear'
        resRaster = 'WSEL_scipy_linear_%i' % int(Cell_size)
      else:
        intMethod = 'cubic'
        resRaster = 'WSEL_scipy_cubic_%i' % int(Cell_size)
    uid = str(uuid.uuid4())
    workDirName = join(expanduser("~"), "qgis_processing_temp", uid)
    call(["mkdir", join(expanduser("~"), "qgis_processing_temp")], shell=True)
    call(["mkdir", workDirName], shell=True)
    resRasterFilename = join(workDirName,resRaster+'.tif')
    if ptsLayer.selectedFeatureCount() and onlySelected and not qgisEngine: # take only selected
      pExt = ptsLayer.boundingBoxOfSelected()
      feats = ptsLayer.selectedFeaturesIterator()
    else: # ignore selection
      pExt = ptsLayer.extent()
      feats = ptsLayer.getFeatures()
    xmin = pExt.xMinimum()
    xmax = pExt.xMaximum()
    ymin = pExt.yMinimum()
    ymax = pExt.yMaximum()
    grid_x, grid_y = np.mgrid[xmin:xmax:Cell_size, ymin:ymax:Cell_size]
    if qgisEngine:
      ldata = QgsInterpolator.LayerData()
      ldata.interpolationAttribute = Water_level_attribute
      ldata.vectorLayer = ptsLayer
      ldata.mInputType = 0
      ldata.zCoordInterpolation = False
      tini = QgsTINInterpolator([ldata], interpolation=intMethod, showProgressDialog=True)
      sx,sy = grid_x.shape
      grid = np.empty_like(grid_x)
      for j in range(sy):
        for i in range(sx):
          grid[i,j] = tini.interpolatePoint(grid_x[i,j],grid_y[i,j])[1]
    else: # scipy engine
      ptsList = []
      ptsWsel = []
      for feat in feats:
        geom = feat.geometry().asPoint()
        ptsList.append([geom.x(), geom.y()])
        ptsWsel.append(feat[Water_level_attribute])
      pts = np.array(ptsList)
      vals = np.array(ptsWsel)
      try:
        grid = griddata(pts, vals, (grid_x, grid_y), method=intMethod)
      except MemoryError:
        self.addInfo('\nMemory error! Try to generate smaller raster.')
        return
      except:
        self.addInfo('\nTraceback:\n%s' % traceback.format_exc())
        return
    self.array2raster(resRasterFilename,[xmin,ymin],Cell_size,Cell_size,np.transpose(grid))
    processing.load(resRasterFilename, resRaster)
    self.addInfo('\n  Water surface raster created and saved to a temporary file:\n  %s' % resRasterFilename)

    QApplication.setOverrideCursor(Qt.ArrowCursor)
    QDialog.accept(self)

  def displayHelp(self):
    pass

  def populatePointsCombo(self):
    for layerId, layer in self.qras.mapRegistry.mapLayers().iteritems():
      if layer.type() == 0 and layer.geometryType() == 0: # vector and points
        self.ui.cboPoints.addItem(layer.name(), layerId)
      if layer.type() == 0 and layer.geometryType() == 1: # vector and polylines
        pass
      if layer.type() == 0 and layer.geometryType() == 2: # vector and polygons
        pass
      if layer.type() == 1: # it's a raster
        pass
    self.updatePointsAttrs()

  def cboPointsChanged(self):
    curInd = self.ui.cboPoints.currentIndex()
    lid = self.ui.cboPoints.itemData(curInd)
    self.ptsLayer = self.qras.mapRegistry.mapLayer(lid)
    self.updatePointsAttrs()

  def updateInterpTypeCbo(self):
    self.ui.interpTypeCbo.clear()
    self.ui.interpTypeCbo.addItem("linear")
    if self.ui.engineQgisBtn.isChecked(): # QGIS engine
      self.ui.interpTypeCbo.addItem("Clough Toucher")
      self.ui.onlySelectedCheckBox.setDisabled(True)
    else:  # scipy engine
      self.ui.interpTypeCbo.addItem("cubic")
      self.ui.onlySelectedCheckBox.setDisabled(False)
    self.ui.interpTypeCbo.setCurrentIndex(0)

  def updatePointsAttrs(self):
    if self.ptsLayer:
      if self.ptsLayer.featureCount():
        self.ui.cboWselAttr.clear()
        self.ui.cboWselAttr.addItem("")
        attrs = self.ptsLayer.pendingFields()
        for attr in attrs:
          self.ui.cboWselAttr.addItem(attr.name())

