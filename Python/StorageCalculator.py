__author__ = 'Karol Zielinski'

# Konwersja rastra do formatu xyz
import sys
from qgis.core import QgsApplication
from osgeo import gdal

# Inicjalizacja instancji QGIS
app = QgsApplication([], True)
QgsApplication.setPrefixPath(r'C:\OSGeo4W\apps\qgis', True)
QgsApplication.initQgis()

# Import i inicjalizacja modulu processing
sys.path.append(r'C:\Users\kzielinski1\.qgis2\python\plugins')
import processing
from processing.core.Processing import Processing
Processing.initialize()

# Przyciecie rastra do maski zbiornika
ras_input = r'X:\NARZEDZIA\VCS\test_data\Brda_Zbiornik_NMT12m.tif'
poly_input = r'X:\NARZEDZIA\VCS\test_data\ZbKoronowski_Poligon.shp'
ras_output = r'X:\NARZEDZIA\VCS\test_data\Brda_Zbiornik_NMT12m_clip.tif'
processing.runalg('gdalogr:cliprasterbymasklayer', ras_input, poly_input, -9999, False, False, '', ras_output)

# Obliczenie statystyk przecietego rastra
gtif = gdal.Open(ras_input)
gtifs = gtif.GetGeoTransform()
resolution = gtifs[1]
stat = r'X:\NARZEDZIA\VCS\test_data\stat.html'
processing.runalg('qgis:rasterlayerstatistics', ras_output, stat)

# Wyciagniecie statystyk do zmiennej
html = open(stat)
read = html.readline()
lststat = read.split('</p><p>')
strmax = lststat[3]
strmin = lststat[2]
maxs = float(strmax.split(':')[1])
mins = float(strmin.split(':')[1])

# Obliczanie wartosci przedzialow
cnt = mins
lis = []
compart_num = raw_input('Podaj liczbe przedzialow: ')
compart_value = (maxs-mins)/float(compart_num)
for i in range(int(compart_num)):
    cnt += compart_value
    lis.append(cnt)

# Tworzenie rastrow warstwic i obliczenie objetosci
lis_path = []
rsl_int = resolution*resolution
for x in range(len(lis)):
    exp = '(A<{0})*abs(A)*{1}'.format(lis[x], rsl_int)
    ras_out2 = r'X:\NARZEDZIA\VCS\test_data\Brda_Zbiornik_NMT12m{0}.tif'.format(lis[x])
    processing.runalg('gdalogr:rastercalculator', ras_output, '1', None, '1', None, '1', None, '1', None, '1', None, '1', exp, '-9999', 5, None, ras_out2)
    lis_path.append(ras_out2)

# Statystki rastrow
lis_path_stat = []
for y in range(len(lis_path)):
    path_stat = lis_path[y]+'_stat'
    processing.runalg('qgis:rasterlayerstatistics', lis_path[y], path_stat)
    lis_path_stat.append(path_stat)

# Wyrzucenie rastrow do slownika
lis_suma = []
for z in range(len(lis_path_stat)):
    html2 = open(r''+lis_path_stat[z]+'.html')
    read2 = html2.readline()
    lststat2 = read2.split('</p><p>')
    strsum = lststat2[-3]
    suma = float(strsum.split(':')[1])/1000
    lis_suma.append(suma)
print zip(lis, lis_suma)

