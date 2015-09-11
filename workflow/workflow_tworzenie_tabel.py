from rivergis import river_database as rdb
baza = rdb.RiverDatabase('rivergis', 'localhost', '5432', 'postgres', 'pass')
baza.SCHEMA = 'start'
baza.SRID = 2180
baza.connect_pg()
sc = baza.process_hecobject(rdb.StreamCenterlines, 'pg_create_table')
xs = baza.process_hecobject(rdb.XSCutLines, 'pg_create_table')
bl = baza.process_hecobject(rdb.BankLines, 'pg_create_table')
la = baza.process_hecobject(rdb.LeveeAlignment, 'pg_create_table')
fp = baza.process_hecobject(rdb.Flowpaths, 'pg_create_table')
lu = baza.process_hecobject(rdb.LanduseAreas, 'pg_create_table')

baza.add_to_view(sc)
baza.add_to_view(xs)
baza.add_to_view(bl)
baza.add_to_view(la)
baza.add_to_view(fp)
baza.add_to_view(lu)
