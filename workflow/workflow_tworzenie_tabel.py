# UWAGA: W QGIS zaznacz warstwe z przebiegiem rzeki !
# Warstwa oprócz geometrii może miec wypełnione wszystkie
# pozostałe atrybuty.

s = iface.activeLayer()

from rivergis import river_database as rdb
from rivergis import hecobjects as heco
baza = rdb.RiverDatabase(iface, 'rivergis', 'localhost', '5432', 'postgres', 'pass')
baza.SCHEMA = 'start'
baza.SRID = 2180
baza.connect_pg()
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
