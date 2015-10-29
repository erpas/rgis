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
* XSCutLines polyline layer

Both LanduseAreas and XSCutLines you can create by clicking this button |createbutton| on toolbar and choosing appropriate layers to create. You can also find it in database context menu as is shown below. Created layers are empty and must be edited manually. This guide assume that XSCutLines and LanduseAreas layers are already done and all attributes are filled.

  .. |createbutton| image:: img/create_ico.png

  .. note::

     For more information about creation and edition of XSCutLines and LanduseAreas layers please look `HERE <http://www.hec.usace.army.mil/software/hec-georas/documentation/HEC-GeoRAS_43_Users_Manual.pdf>`_ Chapter 4-11 and 4-28


  .. _fig_man_create:
  .. figure:: img/create_2.png

     Database context menu

  .. figure:: img/create_3.png
     :align: center

     Create RAS Layers window


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

Both StreamCenterline and Bridges/Culverts you can create by clicking this button |createbutton| on toolbar and choosing appropriate layers to create. You can also find it in database context menu as is shown below. Created layers are empty and must be edited manually. This guide assume that StreamCenterline layer is already done and all attributes are filled. We will focus on Bridges/Culverts layer and its functionality.

  .. |createbutton| image:: img/create_ico.png

  .. note::

     For more information about creation and edition of StreamCenterline layer please look `HERE <http://www.hec.usace.army.mil/software/hec-georas/documentation/HEC-GeoRAS_43_Users_Manual.pdf>`_ Chapter 4-7


  .. _fig_bridge_create:
  .. figure:: img/create_2.png

     Database context menu

  .. figure:: img/create_1.png
     :align: center

     Create RAS Layers window

Bridges/Culverts layer should contain “BridgeID”, “RiverCode”, “ReachCode”, “Station”, “USDistance”, “TopWidth”, “NodeName” and DtmID” attributes. Edit layer and digitize bridges. “BridgeID” will be filed automatically while digitizing. Remember that drawing has to be performed from left bank to right bank looking downstream.

  .. _fig_bridgeedit:
  .. figure:: img/bridge_2.png
     :align: center

     Exemplary bridge edition

After finishing sketch and living edit mode go to RAS Geometry tab and from context menu choose Bridges/Culverts position. You will see sub menu where you can extract River/Reach Names, calculate Stationing and Elevations. There is also option to proceed all of the functions by once by clicking “All”.

  .. _fig_bridgemenu:
  .. figure:: img/bridge_1.png
     :align: center

     Bridge/Culvert menu

If particular function is done without any problem you will see message in main RiverGIS window about successful processing. For elevation extraction you need DTM which covers bridges extent. After clicking “Elevation” or “All” functions there will be dialog window displayed with current DTM rasters. Choose any and click “OK”.

  .. _fig_bridgdtm:
  .. figure:: img/bridge_dtm.png
     :align: center

     DTM option window

You have also access to “All” function from main RiverGIS toolbar by clicking this |bridgebutton| button . “USDistance”, “TopWidth”, “NodeName” have to be filled manually by the user. DtmID will be filled after elevation extraction but for end user filled data are not important. Remember that DTM has to cover all bridges/culverts otherwise extraction will not proceed. If you have more than one DTM in the same extent then raster with better resolution will be chosen for processing. For elevation control after processing point layer will be added to view where you can inspect bridge/culver elevation data.

  .. |bridgebutton| image:: img/bridge_ico.png

--------------------------------------
4. Inline Structures
--------------------------------------

This chapter describes processing of Inline Structures layer. There are three layers required for complete extraction of the data:

* StreamCenterline polyline layer
* InlineStructures polyline layer
* DTM layer (optional)

Both StreamCenterline and InlineStructures you can create by clicking this button |createbutton| on toolbar and choosing appropriate layers to create. You can also find it in database context menu as is shown below. Created layers are empty and must be edited manually. This guide assume that StreamCenterline layer is already done and all attributes are filled. We will focus on InlineStructures layer and its functionality.

  .. |createbutton| image:: img/create_ico.png

  .. note::

     For more information about creation and edition of StreamCenterline layer please look `HERE <http://www.hec.usace.army.mil/software/hec-georas/documentation/HEC-GeoRAS_43_Users_Manual.pdf>`_ Chapter 4-7


  .. _fig_inline_create:
  .. figure:: img/create_2.png

     Database context menu

  .. figure:: img/inline_create.png
     :align: center

     Create RAS Layers window

InlineStructures layer should contain “InlineSID”, “RiverCode”, “ReachCode”, “Station”, “USDistance”, “TopWidth”, “NodeName” and DtmID” attributes. Edit layer and digitize inline structures. “InlineSID” will be filed automatically while digitizing. Remember that drawing has to be performed from left bank to right bank looking downstream.

  .. _fig_inlineedit:
  .. figure:: img/inline_1.png
     :align: center

     Exemplary inline structures

After finishing sketch and living edit mode go to RAS Geometry tab and from context menu choose Inline Structures position. You will see sub menu where you can extract River/Reach Names, calculate Stationing and Elevations. There is also option to proceed all of the functions by once by clicking “All”.

  .. _fig_inlinemenu:
  .. figure:: img/inline_2.png
     :align: center

     Inline Structures menu

If particular function is done without any problem you will see message in main RiverGIS window about successful processing. For elevation extraction you need DTM which covers inline structures extent. After clicking “Elevation” or “All” functions there will be dialog window displayed with current DTM rasters. Choose any and click “OK”.

  .. _fig_inlinedtm:
  .. figure:: img/bridge_dtm.png
     :align: center

     DTM option window

You have also access to “All” function from main RiverGIS toolbar by clicking this |inlinebutton| button . “USDistance”, “TopWidth”, “NodeName” have to be filled manually by the user. DtmID will be filled after elevation extraction but for end user filled data are not important. Remember that DTM has to cover all inline structures otherwise extraction will not proceed. If you have more than one DTM in the same extent then raster with better resolution will be chosen for processing. For elevation control after processing point layer will be added to view where you can inspect inline structures elevation data.

  .. |inlinebutton| image:: img/Inline_str_ico.png

--------------------------------------
5. Lateral Structures
--------------------------------------

This chapter describes processing of Lateral Structures layer. There are three layers required for complete extraction of the data:

* StreamCenterline polyline layer
* LateralStructures polyline layer
* DTM layer (optional)

Both StreamCenterline and LateralStructures you can create by clicking this button |createbutton| on toolbar and choosing appropriate layers to create. You can also find it in database context menu as is shown below. Created layers are empty and must be edited manually. This guide assume that StreamCenterline layer is already done and all attributes are filled. We will focus on LateralStructures layer and its functionality.

  .. |createbutton| image:: img/create_ico.png

  .. note::

     For more information about creation and edition of StreamCenterline layer please look `HERE <http://www.hec.usace.army.mil/software/hec-georas/documentation/HEC-GeoRAS_43_Users_Manual.pdf>`_ Chapter 4-7


  .. _fig_lateral_create:
  .. figure:: img/create_2.png

     Database context menu

  .. figure:: img/lateral_create.png
     :align: center

     Create RAS Layers window

LateralStructures layer should contain “LateralSID”, “RiverCode”, “ReachCode”, “Station”, “USDistance”, “TopWidth”, “NodeName” and DtmID” attributes. Edit layer and digitize lateral structures. “LateralSID” will be filed automatically while digitizing. Remember that drawing has to be performed from upstream to downstream.

  .. _fig_inlineedit:
  .. figure:: img/lateral_1.png
     :align: center

     Exemplary lateral structure

After finishing sketch and living edit mode go to RAS Geometry tab and from context menu choose Lateral Structures position. You will see sub menu where you can extract River/Reach Names, calculate Stationing and Elevations. There is also option to proceed all of the functions by once by clicking “All”. If particular function is done without any problem you will see message in main RiverGIS window about successful processing.

  .. _fig_inlinemenu:
  .. figure:: img/lateral_2.png
     :align: center

     Lateral Structures menu

Stationing is calculated basing on upstream start point of lateral structure with shortest distance to StreamCenterline. Please inspect correctness of River/Reach Names and Stationing for lateral structures. There exist probability of mistake in a situation where other channel lie closer to upstream start point of lateral structure than channel to which lateral structure should be referenced to.  For elevation extraction you need DTM which covers lateral structures extent. After clicking “Elevation” or “All” functions there will be dialog window displayed with current DTM rasters. Choose any and click “OK”.

  .. note::

     For more information about creation and edition of LateralStructures layer please look `HERE <http://www.hec.usace.army.mil/software/hec-georas/documentation/HEC-GeoRAS_43_Users_Manual.pdf>`_ Chapter 4-37

  .. _fig_inlinedtm:
  .. figure:: img/bridge_dtm.png
     :align: center

     DTM option window

You have also access to “All” function from main RiverGIS toolbar by clicking this |lateralbutton| button . “USDistance”, “TopWidth”, “NodeName” have to be filled manually by the user. DtmID will be filled after elevation extraction but for end user filled data are not important. Remember that DTM has to cover all lateral structures otherwise extraction will not proceed. If you have more than one DTM in the same extent then raster with better resolution will be chosen for processing. For elevation control after processing point layer will be added to view where you can inspect lateral structures elevation data.

  .. |lateralbutton| image:: img/Lateral_str_ico.png