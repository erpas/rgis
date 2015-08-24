.. _create_wsel_raster:

Create Water Surface Raster 
---------------------------
Menu: 2D Results

Creates water surface raster using previously loaded point :abbr:`WSEL (water surface elevation)` layer (see :ref:`load_wsel_from_hdf`).
This tool uses SAGA's raster module for interpolation

.. _fig_createWselRaster_dialog:
.. figure:: img/createWselRast.png
   :align: center
   
   Create Water Surface Raster dialog window.

^^^^^^^^^^^^^^^^
Tool parameters
^^^^^^^^^^^^^^^^

* :dfn:`Water surface elevation point layer` --- point layer with :abbr:`WSEL (water surface elevation)` data.
* :dfn:`Water surface elevation attribute` --- name of the attribute with :abbr:`WSEL (water surface elevation)`
* :dfn:`Target raster cell size` --- specify water surface raster cell size.
* :dfn:`Tile size` --- SAGA raster module has a memory limitations and cannot deal with BIG rasters. If your raster is going to have more than 20 000 000 cells you need to divide the task and perform interpolation on smaller parts: RiverGIS does it on square tiles. Specify the tile size in pixels according to your data. The size shouldn't be bigger than 3000. 
* :dfn:`Tile buffer size` --- there should be no gap between the tiles. Moreover, they have to overlap and that overlapping distance is the buffer size.





