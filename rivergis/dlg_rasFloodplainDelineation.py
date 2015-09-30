# -*- coding: utf-8 -*-

from subprocess import call
from os.path import expanduser, join, abspath, basename
import uuid

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *
from qgis.gui import *
from qgis.utils import *
import processing
from ui.ui_rasFloodplainDelineation import *


class DlgRasFloodplainDelineation(QDialog):
    def __init__(self, rgis):
        QDialog.__init__(self)
        self.ui = Ui_DlgFloodplainDelineation()
        self.ui.setupUi(self)
        self.rgis = rgis

        self.ui.buttonBox.accepted.connect(self.acceptDialog)
        self.ui.buttonBox.rejected.connect(self.reject)
        self.ui.helpButton.clicked.connect(self.displayHelp)
        self.ui.cboDtm.currentIndexChanged.connect(self.cboDtmChanged)
        self.ui.cboWsel.currentIndexChanged.connect(self.cboWselChanged)

        
        self.ui.cboDtm.addItem("")
        self.ui.cboWsel.addItem("")
        self.populateCombos()
        self.dtmLayer = None
        self.wselLayer = None
        self.rgis.addInfo('<br><b>Running floodplain delineation.</b>' )

    def acceptDialog(self ):
        if not self.dtmLayer or not self.wselLayer:
            return
        QApplication.setOverrideCursor(Qt.WaitCursor)
        if self.ui.tileSize.text():
            Tile_size = int(self.ui.tileSize.text())
        else:
            self.rgis.addInfo('Empty or wrong tile size value. Cancelling...' )
        if self.ui.bufferSize.text():
            Tile_buffer_size = int(self.ui.bufferSize.text())
        else:
            self.rgis.addInfo('Empty or wrong buffer size value. Cancelling...' )

        depthRasterName = 'Depths_temporary'
        floodRangePolygons = 'Flood_range_temporary'

        workDirName = join(expanduser("~"), "qgis_processing_temp", str(uuid.uuid4()))
        shpDir = join(workDirName, "polygons")
        # lf = join(workDirName,'log.txt')

        call(["mkdir", join(expanduser("~"), "qgis_processing_temp")], shell=True)
        call(["mkdir", workDirName], shell=True)
        call(["mkdir", shpDir], shell=True)

        self.rgis.addInfo("  Creating tiles...")
        pExt = self.wselLayer.extent()
        xmin = pExt.xMinimum()
        xmax = pExt.xMaximum()
        ymin = pExt.yMinimum()
        ymax = pExt.yMaximum()
        pExtStr = '%.2f, %.2f, %.2f, %.2f' % (xmin, xmax, ymin, ymax)
        siatka = processing.runalg('qgis:vectorgrid', pExtStr, Tile_size, Tile_size, 0, None)
        siatkaLayer = processing.getObject(siatka['OUTPUT'])
        siatkaLayer.startEditing()
        attrs= siatkaLayer.pendingFields()
        siatkaLayer.dataProvider().addAttributes( [ QgsField("grid_id", QVariant.Int) ] )
        siatkaLayer.commitChanges()
        siatkaLayer.startEditing()
        feats = siatkaLayer.getFeatures()
        for feat in feats:
            feat['grid_id'] = feat.id()
            siatkaLayer.updateFeature(feat)
        siatkaLayer.commitChanges()
        tiles = []
        depths = ""
        ranges = []

        feats = siatkaLayer.getFeatures()
        nFeats = siatkaLayer.featureCount()

        self.rgis.addInfo("  Preparing data for tiles...")

        for i, feat in enumerate(feats):
            fid = feat['grid_id']
            sel = siatkaLayer.getFeatures( QgsFeatureRequest().setFilterExpression ( u'"grid_id" = %i' % fid ) )
            siatkaLayer.setSelectedFeatures( [ f.id() for f in sel ] )
            s1 = processing.runalg("qgis:saveselectedfeatures",siatkaLayer,None)
            sBuf = processing.runalg("qgis:fixeddistancebuffer",s1['OUTPUT_LAYER'],Tile_buffer_size,5,False,None)
            siatkaLayer.removeSelection()
            sBufExt = self.getLayerExtent(processing.getObject(sBuf['OUTPUT']))
            dtm = processing.runalg("gdalogr:cliprasterbyextent",self.dtmLayer,"none",sBufExt,"",None)
            wsel = processing.runalg("gdalogr:cliprasterbyextent",self.wselLayer,"none",sBufExt,"",None)
            tiles.append([fid, s1['OUTPUT_LAYER'], dtm['OUTPUT'], wsel['OUTPUT']])

        self.rgis.addInfo("  Calculating depths and ranges...")
        for i, tile in enumerate(tiles):
            siatka = abspath(tile[1])
            dtm = abspath(tile[2])
            wsel = abspath(tile[3])
            depth = processing.runalg("saga:rastercalculator",dtm,wsel,"ifelse(gt((b-a),0),(b-a), (-9999))",False,8,None)
            if not depth:
                continue
            depthClipped = processing.runalg("saga:clipgridwithpolygon",depth['RESULT'],siatka,None)
            depths += depthClipped['OUTPUT'] + '\n'
            maska = processing.runalg("saga:reclassifygridvalues",depth['RESULT'],2,0,1,0,0,1,2,0,"-999999,0,-99999,0,20,1,20,100,1",0,True,0,True,0,None)
            r1 = processing.runalg("gdalogr:polygonize",maska['RESULT'],"DN",None)
            shpName = join(shpDir, 'range_'+str(i)+'.shp')
            processing.runalg("gdalogr:clipvectorsbypolygon",r1['OUTPUT'],siatka,"",shpName)
            ranges.append(shpName)
        self.rgis.addInfo("  Depths clipped and range polygons created!\n")
        self.rgis.addInfo("  Temporary results saved to:<br>  %s" % workDirName)

        depthTilesFilename = join(workDirName, 'depth_tiles.txt')
        depthVrtFile = join(workDirName, 'depth_tiles.vrt')
        depthTilesFile = open(depthTilesFilename, "w")
        depthTilesFile.write(depths)
        depthTilesFile.close()

        self.rgis.addInfo("Stitching depths and ranges")
        self.rgis.addInfo(depthVrtFile)
        call(["gdalbuildvrt", "-input_file_list", depthTilesFilename, depthVrtFile])
        processing.load(depthVrtFile, depthRasterName)
        # depthVrt = processing.getObject( depthVrtFile )
        # d = processing.runalg("saga:rastercalculator",depthVrt,None,"a",False,8,None)
        # processing.load(d['RESULT'], depthRasterName)

        t = '''<OGRVRTDataSource>
            <OGRVRTUnionLayer name="unionLayer">\n'''
        for i, shp in enumerate(ranges):
            t += '        <OGRVRTLayer name="range_%i">\n' % i
            t += '            <SrcDataSource relativeToVRT="1">%s</SrcDataSource>\n' % basename(shp)
            t += '        </OGRVRTLayer>\n'
        t += '''    </OGRVRTUnionLayer>
        </OGRVRTDataSource>\n'''
        rangeVrtFilename = join(shpDir, 'ranges.vrt')
        self.rgis.addInfo("{}".format(rangeVrtFilename))
        rangeVrtFile = open(rangeVrtFilename, "w")
        rangeVrtFile.write(t)
        rangeVrtFile.close()
        processing.load(rangeVrtFilename, floodRangePolygons)

        QApplication.setOverrideCursor(Qt.ArrowCursor)
        QDialog.accept(self)

    
    def displayHelp(self):
        pass

    def populateCombos(self):
        for layerId, layer in self.rgis.mapRegistry.mapLayers().iteritems():
            if layer.type() == 0 and layer.geometryType() == 0: # vector and points
                pass
            if layer.type() == 0 and layer.geometryType() == 1: # vector and polylines
                pass
            if layer.type() == 0 and layer.geometryType() == 2: # vector and polygons
                pass
            if layer.type() == 1: # it's a raster
                self.ui.cboDtm.addItem(layer.name(), layerId)
                self.ui.cboWsel.addItem(layer.name(), layerId)

    def cboDtmChanged(self):
        curInd = self.ui.cboDtm.currentIndex()
        lid = self.ui.cboDtm.itemData(curInd)
        self.dtmLayer = self.rgis.mapRegistry.mapLayer(lid)

    def cboWselChanged(self):
        curInd = self.ui.cboWsel.currentIndex()
        lid = self.ui.cboWsel.itemData(curInd)
        self.wselLayer = self.rgis.mapRegistry.mapLayer(lid)

    def getLayerExtent(self, layer, buf=0, hecras=0):
        pExt = layer.extent()
        xmin = pExt.xMinimum()
        xmax = pExt.xMaximum()
        ymin = pExt.yMinimum()
        ymax = pExt.yMaximum()
        if hecras:
            pExtStr = '%.2f, %.2f, %.2f, %.2f' % (xmin-buf, xmax+buf, ymax+buf, ymin-buf)
        else:
            pExtStr = '%.2f, %.2f, %.2f, %.2f' % (xmin-buf, xmax+buf, ymin-buf, ymax+buf)
        return pExtStr
