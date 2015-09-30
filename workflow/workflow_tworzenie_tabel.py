# -*- coding: utf-8 -*-

from rivergis import river_database as rdb
from rivergis import hecobjects as heco

# UWAGA: W QGIS odpal wtyczkę RiverGIS i zaznacz warstwe z przebiegiem rzeki !
# Warstwa oprócz geometrii może miec wypełnione wszystkie pozostałe atrybuty.

# odwołanie do wtyczki
rgis = qgis.utils.plugins['rivergis'].dlg
# biezaca warstwa do importu
s = iface.activeLayer()

# utworzenie bazy
baza = rdb.RiverDatabase(rgis, 'rivergis', 'localhost', '5432', 'postgres', 'pass')
baza.SCHEMA = 'start'
baza.SRID = 2180
baza.connect_pg()
# utworzenie w bazie funkcji tworzacej indeks przestrzenny, jesli nie istnieje
baza.create_spatial_index()

baza.register_existing(heco)
sc = baza.process_hecobject(heco.StreamCenterlines, 'pg_create_table')
xs = baza.process_hecobject(heco.XSCutLines, 'pg_create_table')
bl = baza.process_hecobject(heco.BankLines, 'pg_create_table')
la = baza.process_hecobject(heco.LeveeAlignment, 'pg_create_table')
fp = baza.process_hecobject(heco.Flowpaths, 'pg_create_table')
lu = baza.process_hecobject(heco.LanduseAreas, 'pg_create_table')

baza.add_to_view(sc)
baza.add_to_view(xs)
baza.add_to_view(bl)
baza.add_to_view(la)
baza.add_to_view(fp)
baza.add_to_view(lu)

baza.insert_layer(s, sc)
iface.mapCanvas().refresh()

# export wyników do RAS GIS Import
from rivergis import ras_gis_import

rgis = qgis.utils.plugins['rivergis'].dlg
ex = ras_gis_import.RasGisImport(rgis)
sdf = ex.gis_import_file()

# zapis do pliku SDF
with open(r'E:\test\sdefik.sdf', 'w') as f:
    f.write(sdf)
