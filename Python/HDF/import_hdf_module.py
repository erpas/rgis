import netCDF4

r = netCDF4.Dataset(r"C:\Users\rpasiok\Documents\MODEL_HECRAS\Wawa_6\P6_temp.p02.hdf")
names = r['Geometry']['2D Flow Areas']['Names'][:]
cme = r['Geometry']['2D Flow Areas']['{}'.format(names[0].strip())]['Cells Minimum Elevation']