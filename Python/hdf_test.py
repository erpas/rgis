__author__ = 'ldebek'

import h5py

f = h5py.File(r'C:\test\S02_Brda.p02.hdf', 'r')

print(f[u'Geometry'][u'Cross Sections'][ u'Station Elevation Values'])