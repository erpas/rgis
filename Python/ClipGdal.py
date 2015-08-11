__author__ = 'Karol Zielinski'

# Modules import
import operator
from osgeo import gdal, gdalnumeric, ogr, osr
import Image
import ImageDraw
import shapefile

# Data paths
Raster = r'X:\NARZEDZIA\VCS\test_data\Brda_Zbiornik_NMT12m.tif'
shp = r'X:\NARZEDZIA\VCS\test_data\ZbKoronowski_Poligon_PUWG92'
OutRaster = r'X:\NARZEDZIA\VCS\test_data\Brda_Zbiornik_NMT12m_clip.tif'

# Converts a Python Imaging Library array to a gdalnumeric image
def ImageToArray(i):
    a = gdalnumeric.numpy.fromstring(i.tostring(), 'b')
    a.shape = i.im.size[1], i.im.size[0]
    return a

# Uses a gdal geomatrix (gdal.GetGeoTransform()) to calculate the pixel location of a geospatial coordinate
def world2Pixel(geoMatrix, x, y):
    ulX = geoMatrix[0]
    ulY = geoMatrix[3]
    xDist = geoMatrix[1]
    yDist = geoMatrix[5]
    rtnX = geoMatrix[2]
    rtnY = geoMatrix[4]
    pixel = int((x - ulX) / xDist)
    line = int((ulY - y) / yDist)
    return (pixel, line)

# Load the source data as a gdalnumeric array
srcArray = gdalnumeric.LoadFile(Raster)

# Also load as a gdal image to get geotransform
srcImage = gdal.Open(Raster)
geoTrans = srcImage.GetGeoTransform()

# Use pyshp to open the shapefile
r = shapefile.Reader("%s.shp" % shp)

# Convert the layer extent to image pixel coordinates
minX, minY, maxX, maxY = r.bbox
ulX, ulY = world2Pixel(geoTrans, minX, maxY)
lrX, lrY = world2Pixel(geoTrans, maxX, minY)

# Calculate the pixel size of the new image
pxWidth = int(lrX - ulX)
pxHeight = int(ulY - lrY)

clip = srcArray[ulY:lrY, ulX:lrX]

# Create a new geomatrix for the image
geoTrans = list(geoTrans)
geoTrans[0] = minX
geoTrans[3] = maxY

# Map points to pixels for drawing the county boundary
# on a blank 8-bit, black and white, mask image.
pixels = []
for p in r.shape(0).points:
    pixels.append(world2Pixel(geoTrans, p[0], p[1]))
rasterPoly = Image.new('F', (pxWidth, pxHeight), None)

# Create a blank image in PIL to draw the polygon.
rasterize = ImageDraw.Draw(rasterPoly)
rasterize.polygon(pixels, 0)

# Convert the PIL image to a NumPy array
mask = ImageToArray(rasterPoly)

# Clip the image using the mask
clip = gdalnumeric.numpy.choose(mask, (clip, 0)).astype(gdalnumeric.
numpy.uint8)

# Save ndvi as tiff
gdalnumeric.SaveArray(clip, "%s.tif" % OutRaster, \
format = "GTiff", prototype = Raster)