.. _stepbystep1d:

=================================================
Step by step tutorial: Create HEC-RAS 1D Geometry
=================================================

--------------------------------------
1. Create source geometry of the model
--------------------------------------

* Create empty river database tables for 1d HEC-RAS model or
* Import the model geometry from existing layers loaded into a QGIS project

Required data of the model geometry:

1. River centerlines (polylines)

2. Cross-sections (polylines)

3. DTM, digital terrain model --- a raster layer


Optional geometry data:

4. Channel Bank lines

5. Flow Paths --- flow centerlines for each cross-section part:main channel, right and left overbank (polylines)

6. Levees (polylines)

7. Ineffecive flow areas (polygons)

8. Blocked obstructions (polygons)

9. Land cover --- a polygon layer. HEC-RAS will use it to calculate mesh cells roughness.



.. note::

  QGIS User Manual `Loading raster data <http://docs.qgis.org/2.6/en/docs/user_manual/working_with_raster/supported_data.html>`_ and `Loading vector data in QGIS <http://docs.qgis.org/2.6/en/docs/user_manual/working_with_vector/supported_data.html>`_ is an excellent start point for QGIS beginners.
  
1. **Start from saving QGIS project** in a favourite directory :menuselection:`Project --> Save` 
2. **Load a raster of digital terrain model (DTM)**\ . Below you can see a DTM with a hillshade as an overlay (`see QGIS Training Manual  <http://docs.qgis.org/2.6/en/docs/training_manual/rasters/terrain_analysis.html?highlight=hillshade>`_).

  .. _fig_sbs_loadDtm:
  .. figure:: img/sbs02.png
     :align: center
     
     DTM and hillshade overlay loaded into QGIS project

3. **Create a 2D Flow Areas** polygon layer (:menuselection:`Layer --> Create Layer --> New Shapefile Layer...`) with required fields:

  * name of 2D Flow Area (text) and
  * cell size (whole number) --- a default mesh points spacing in layer's CRS units.

--------------------------------------
2. Manning's values extraction
--------------------------------------

To prepare Manning’s value table you need to prepare two layers:

* LanduseAreas polygon layer
* XSCutLines  polyline layer

Land use layer must contain “LUID”, “LUCode” and “N_Value” attributes and it should contain multipart polygons. In this example "LUID" and "LUCode" is the same but it can be different.

  .. _fig_man_luatttable:
  .. figure:: img/lu_att_table.png
     :align: center

     Exemplary Land use attribute table

For correct Manning's values extraction all of the cross sections in XSCutLines layer have to cover land use polygons

  .. _fig_man_xslupic:
  .. figure:: img/xs_lu_pic.png
     :align: center

     Cross sections and Land use layers coverage

Next step is pushing a button |Mannbuton| which is located on main toolbar or you can find it also in context menu as is shown below

  .. |Mannbuton| image:: img/Manning_ico.png

  .. _fig_man_mancontextmenu:
  .. figure:: img/man_context_menu.png
     :align: center

     RAS Geometry context menu

Main RiverGIS window should display following message if the extraction was done properly

  .. _fig_man_mandone:
  .. figure:: img/man_done.png
     :align: center

     Correct Manning's values extraction

You should obtain table with "XsecID", "Fraction", "N_Value" and "LUCode" attributes. Table will be added to view and in this form is ready for SDF export.

  .. _fig_man_mantable:
  .. figure:: img/man_table.png
     :align: center

     Exemplary Manning's values table

--------------------------------------
3. Bridges/Culverts
--------------------------------------

This chapter describes processing of bridges/culverts layer. There are three layers required for complete extraction of the data:

* StreamCenterline polyline layer
* Bridges/Culverts polyline layer
* DTM layer (optional)

Both StreamCenterline and Bridges/Culverts you can create by clicking this button |createbutton| on toolbar and choosing appropriate layers to create. You can also find it in database context menu as is shown below. Created layers are empty and must be edited manually. This guide assume that StreamCenterline layer is already done and all attrubutes are filled. We will focus on Bridges/Culverts layer and its functionality.

  .. |createbutton| image:: img/create_ico.png

  .. note::

     For more information about creation and edition of StreamCenterline layer please look :download:`HERE <HEC_help/HEC_GeoRAS_10_for_ArcGIS_10.pdf>`


  .. _fig_man_create:
  .. figure:: img/create_2.png
  .. figure:: img/create_1.png
     :align: center

Bridges/Culverts layer should contain "BridgeID", "RiverCode", "ReachCode", "Station", "USDistance", "TopWidth", "NodeName" and DtmId" attributes. First four attributes are