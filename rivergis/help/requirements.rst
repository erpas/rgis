.. _requirements:

-------------
Requirements
-------------

 RiverGIS needs an active connection to a PostGIS database. You can create a new connection from QGIS menu :menuselection:`Layer --> Add layer --> Add PostGIS layers...`.

Installation of required Python packages
----------------------------------------
^^^^^^^^^^^^^^^^
h5py
^^^^^^^^^^^^^^^^
On **Windows** and 32-bit QGIS installation you can experience difficulties trying to install :file:`h5py` for :file:`OSGeo4W` Python. If you're desperate, try the following:

#. Install 32-bit QGIS using OSGeo4W Network Installer --- you need :file:`qgis` from Desktop.
#. Download `h5py from rivergis.com <http://rivergis.com/h5py_for_osgeo4w.7z>`_, unpack it and copy folder :file:`h5py` to :file:`C:\\Osgeo4W\\apps\\Python27\\Lib\\site-packages`.
#. Restart QGIS and try to run :ref:`load_wsel_from_hdf` from :menuselection:`2D results` menu --- if it asks you for a HDF file, the package is properly installed.

If the above doesn't work for you, please, `let me know <mailto:rpasiok@gmail.com>`_.




