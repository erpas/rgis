.. _stepbystep1d:

=================================
Step by step: HEC-RAS 1D Geometry
=================================

----------------------------
Create geometry of the model
----------------------------

Required data of the model geometry:

1. River centerlines (polylines)

2. Cross-sections (polylines)

3. DTM, digital terrain model --- a raster layer


Optional geometry data:

4. Channel Bank lines

5. Flow Paths --- flow centerlines for each cross-section part: main channel, right and left overbank (polylines)

6. Levees (polylines)

7. Ineffective flow areas (polygons)

8. Blocked obstructions (polygons)

9. Land cover (polygons)

* To create an empty geometry tables for model data (with right attribute structure) you can use ``Database`` -> ``Create River Databse Tables`` option from context menu or press this button from main RiverGIS window. Next choose tables you want to create. Tables will be created at current active schema and with chosen projection, so be sure that they are defined properly before creating tables.

* To import already existing geometry data into empty PostGIS tables you can use ``Database`` -> ``Import Layers Into River Database Tables`` option from context menu or press this button from main RiverGIS window. Next chose layers you want to import. You can insert multiple geometry data to PostGIS tables at once.

* To add model geometry data from schema to QGIS view you can use ``Database`` -> ``Load River Database Tables Into QGIS`` option from context menu or press this button from main RiverGIS window. RiverGIS will find all registered model geometry data inside active schema and add as QGIS layers with preserved order and symbology.

------------------
Stream Centerlines
------------------

If you have properly prepared stream network layer you can use such RiverGIS tools as:

**1. Topology**  ``RAS Geometry`` -> ``Stream Centerline Attributes`` -> ``Topology`` or  |topology|  button.

  .. |topology| image:: img_ico/ras1dStreamCenterlinesTopology.png
This tool builds topology over **StreamCenterlines** table and fill *'FromNode'* and *'ToNode'* fields. It will also create auxiliary **NodesTable** table inside schema. Remember to split network lines on every reach intersection (junctions).


**2. Lengths/Stations**   ``RAS Geometry`` -> ``Stream Centerline Attributes`` -> ``Lengths/Stations`` or |lengths_stations|  button.

  .. |lengths_stations| image:: img_ico/ras1dStreamCenterlinesLengthsStations.png
This tool calculates reaches lengths taking into account stream network topology. It will fill *'ReachLen'*, *'FromSta'*, *'ToSta'* fields and generate **Endpoints** auxiliary table.


**3. All**  ``RAS Geometry`` -> ``Stream Centerline Attributes`` -> ``All`` or  |stream_all|  button.

  .. |stream_all| image:: img_ico/ras1dStreamCenterlinesAll.png
It will launch all tools (defined above) for **StreamCenterlines** geometry one after another.


**4. Copy Stream Centerlines to Flowpaths**  ``RAS Geometry`` -> ``Stream Centerline Attributes`` -> ``Copy Stream Centerlines to Flowpaths``

This option is for copying features from **StreamCenterlines** table to **Flowpaths** as *'Channel'* type. Note that **Flowpaths** table have to be already created.


------------------------
Cross-sections Cut Lines
------------------------

If you have properly prepared cross-sections layer you can use such RiverGIS tools as:

**1. River/Reach Names**  ``RAS Geometry`` -> ``XS Cut Line Attributes`` -> ``River/Reach Names`` or  |xs_names|  button.

  .. |xs_names| image:: img_ico/ras1dXsRiverNames.png
This tool assigns *'ReachID'*, *'RiverCode'* and *'ReachCode'* values from **StreamCenterlines** layer to cross sections.
Note that each cross section can intersect only once with any **StreamCenterlines+* feature.


**2. Stationing**  ``RAS Geometry`` -> ``XS Cut Line Attributes`` -> ``Stationing`` or |xs_stationing|  button.

  .. |xs_stationing| image:: img_ico/ras1dXsStationing.png
This tool calculates *'Station'* values for each cross section.


**3. Bank Stations**  ``RAS Geometry`` -> ``XS Cut Line Attributes`` -> ``Bank Stations`` or  |xs_banks|  button.

  .. |xs_banks| image:: img_ico/ras1dXsBanks.png
This tool calculates fraction on which features from **BankLines** table intersects with each cross section and decides if bank is left or right. Calculated values fills *'LeftBank'* and *'RightBank'* fields in **XSCutLines** table.


**4. Downstream Reach Lengths**  ``RAS Geometry`` -> ``XS Cut Line Attributes`` -> ``Downstream Reach Lengths`` or  |xs_dsl|  button.

  .. |xs_dsl| image:: img_ico/ras1dXsDSLengths.png
This tool calculates each cross section station along flow paths. Calculated values fills *'LLength'*, *'ChLength'* and *'RLength'* fields in **XSCutLines**.


**5. Elevations**  ``RAS Geometry`` -> ``XS Cut Line Attributes`` -> ``Elevations`` or  |xs_elev|  button.

  .. |xs_elev| image:: img_ico/ras1dXsElevations.png
This tool generates points along cross sections (and saves them into **XSSurface** table) and use them to probe DTM rasters. Note that before running tool you have add  DTM tiles into QGIS view and select them in ``RiverGIS Options`` window on ``DTM`` tab. If you have high resolution DTMs consider changing ``chunksize`` value. This option says how many points can be load at once to memory to probe DTM. Default value ``0`` means RiverGIS will try to take all points at once into the analysis.


**6. All**  ``RAS Geometry`` -> ``XS Cut Line Attributes`` -> ``All`` or  |xs_all|  button.

  .. |xs_all| image:: img_ico/ras1dXsAll.png
It will launch all **XSCutLines** tools one after another.


---------------------
Flow Path Centerlines
---------------------
There are 2 methods connected with **FlowPaths** geometry type. Both were already shortly introduced in chapters about **StreamCenterlines** and **XSCutLines**:

1. ``RAS Geometry`` -> ``Stream Centerline Attributes`` -> ``Copy Stream Centerlines to Flowpaths``

2. ``RAS Geometry`` -> ``XS Cut Line Attributes`` -> ``Downstream Reach Lengths`` or  |xs_dsl|  button.

---------------------
Main Channel Banks
---------------------

-----------------
Ineffective Areas
-----------------

--------------------
Blocked Obstructions
--------------------

----------------
Levee Alignments
----------------

--------
Land Use
--------

To make Manning’s values table you need to prepare two layers:

* LanduseAreas polygon layer
* XSCutLines polyline layer

Both LanduseAreas and XSCutLines you can create by clicking this button |createbutton| on toolbar and choosing appropriate layers to create. You can also find it in database context menu as it is shown below. Created layers are empty and must be edited manually. This guide assume that XSCutLines and LanduseAreas layers are already done and all attributes are filled.

  .. |createbutton| image:: img_ico/dbCreateRasTables.png

  .. note::

     For more information about creation and edition of XSCutLines and LanduseAreas layers please look `HERE <http://www.hec.usace.army.mil/software/hec-georas/documentation/HEC-GeoRAS_43_Users_Manual.pdf>`_ Chapter 4-11 and 4-28


  .. _fig_man_create:
  .. figure:: img/create_layer.png

     Database context menu

  .. figure:: img/landuse_create.png
     :align: center

     Create RAS Layers window


Land use layer must contain “LUID”, “LUCode” and “N_Value” attributes and it should contain multipart polygons. In this example "LUID" and "LUCode" is the same but it can be different.

  .. _fig_man_luatttable:
  .. figure:: img/lu_att_table.png
     :align: center

     Exemplary Landuse attribute table

For correct Manning's values extraction all of the cross sections in XSCutLines layer have to cover land use polygons

  .. _fig_man_xslupic:
  .. figure:: img/xs_lu_pic.png
     :align: center

     Cross sections and Land use layers coverage

Next step is pushing a button |mannbuton| which is located on main toolbar or you can find it also in context menu as is shown below

  .. |mannbuton| image:: img/man_ico.png

  .. _fig_man_mancontextmenu:
  .. figure:: img/man_context_menu.png
     :align: center

     RAS Geometry context menu

Main RiverGIS window should display following message if the extraction was done properly

  .. _fig_manmandone:
  .. figure:: img/man_done.png
     :align: center

     Correct Manning's values extraction

You should obtain table with "XsecID", "Fraction", "N_Value" and "LUCode" attributes. Table will be added to view and in this form is ready for SDF export.

  .. _fig_man_mantable:
  .. figure:: img/man_table.png
     :align: center

     Exemplary Manning's values table
----------------
Bridges/Culverts
----------------

This chapter describes processing of bridges/culverts layer. There are three layers required for complete extraction of the data:

* StreamCenterlines polyline layer
* Bridges/Culverts polyline layer
* DTM layer (optional)

Both StreamCenterline and Bridges/Culverts you can create by clicking this button |createbutton| on toolbar and choosing appropriate layers to create. You can also find it in database context menu as is shown below. Created layers are empty and must be edited manually. This guide assume that StreamCenterline layer is already done and all attributes are filled. We will focus on Bridges/Culverts layer and its functionality.

  .. note::

     For more information about creation and edition of StreamCenterlines layer please look `HERE <http://www.hec.usace.army.mil/software/hec-georas/documentation/HEC-GeoRAS_43_Users_Manual.pdf>`_ Chapter 4-7


  .. _fig_bridgecreate:
  .. figure:: img/create_layer.png

     Database context menu

  .. figure:: img/bridge_create.png
     :align: center

     Create RAS Layers window

Bridges/Culverts layer should contain “BridgeID”, “RiverCode”, “ReachCode”, “Station”, “USDistance”, “TopWidth”, “NodeName” and DtmID” attributes. Edit layer and digitize bridges. “BridgeID” will be filed automatically while digitizing. Remember that drawing has to be performed from left bank to right bank looking downstream.

  .. _fig_bridgeedit:
  .. figure:: img/bridge_edit.png
     :align: center

     Exemplary bridge edition

After finishing sketch and living edit mode go to RAS Geometry tab and from context menu choose Bridges/Culverts position. You will see sub menu where you can extract River/Reach Names, calculate Stationing and Elevations. There is also option to proceed all of the functions by once by clicking “All”.

  .. _fig_bridgemenu:
  .. figure:: img/bridge_submenu.png
     :align: center

     Bridge/Culvert menu

If particular function is done without any problem you will see message in main RiverGIS window about successful processing. For elevation extraction you need DTM which covers bridges extent. After clicking “Elevation” or “All” functions there will be dialog window displayed with current DTM rasters. Choose any and click “OK”.

  .. _fig_bridgdtm:
  .. figure:: img/bridge_dtm.png
     :align: center

     DTM option window

You have also access to “All” function from main RiverGIS toolbar by clicking this |bridgebutton| button . “USDistance”, “TopWidth”, “NodeName” have to be filled manually by the user. DtmID will be filled after elevation extraction but for end user filled data are not important. Remember that DTM has to cover all bridges/culverts otherwise extraction will not proceed. If you have more than one DTM in the same extent then raster with better resolution will be chosen for processing. For elevation control after processing point layer will be added to view where you can inspect bridge/culver elevation data.

  .. |bridgebutton| image:: img/bridge_ico.png

-----------------
Inline Structures
-----------------

This chapter describes processing of Inline Structures layer. There are three layers required for complete extraction of the data:

* StreamCenterlines polyline layer
* InlineStructures polyline layer
* DTM layer (optional)

Both StreamCenterline and InlineStructures you can create by clicking this button |createbutton| on toolbar and choosing appropriate layers to create. You can also find it in database context menu as is shown below. Created layers are empty and must be edited manually. This guide assume that StreamCenterline layer is already done and all attributes are filled. We will focus on InlineStructures layer and its functionality.

  .. note::

     For more information about creation and edition of StreamCenterline layer please look `HERE <http://www.hec.usace.army.mil/software/hec-georas/documentation/HEC-GeoRAS_43_Users_Manual.pdf>`_ Chapter 4-7


  .. _fig_inline_create:
  .. figure:: img/create_layer.png

     Database context menu

  .. figure:: img/inline_create.png
     :align: center

     Create RAS Layers window

InlineStructures layer should contain “InlineSID”, “RiverCode”, “ReachCode”, “Station”, “USDistance”, “TopWidth”, “NodeName” and DtmID” attributes. Edit layer and digitize inline structures. “InlineSID” will be filed automatically while digitizing. Remember that drawing has to be performed from left bank to right bank looking downstream.

  .. _fig_inlineedit:
  .. figure:: img/inline_edit.png
     :align: center

     Exemplary inline structures

After finishing sketch and living edit mode go to RAS Geometry tab and from context menu choose Inline Structures position. You will see sub menu where you can extract River/Reach Names, calculate Stationing and Elevations. There is also option to proceed all of the functions by once by clicking “All”.

  .. _fig_inlinemenu:
  .. figure:: img/inline_submenu.png
     :align: center

     Inline Structures menu

If particular function is done without any problem you will see message in main RiverGIS window about successful processing. For elevation extraction you need DTM which covers inline structures extent. After clicking “Elevation” or “All” functions there will be dialog window displayed with current DTM rasters. Choose any and click “OK”.

  .. _fig_inlinedtm:
  .. figure:: img/bridge_dtm.png
     :align: center

     DTM option window

You have also access to “All” function from main RiverGIS toolbar by clicking this |inlinebutton| button . “USDistance”, “TopWidth”, “NodeName” have to be filled manually by the user. DtmID will be filled after elevation extraction but for end user filled data are not important. Remember that DTM has to cover all inline structures otherwise extraction will not proceed. If you have more than one DTM in the same extent then raster with better resolution will be chosen for processing. For elevation control after processing point layer will be added to view where you can inspect inline structures elevation data.

  .. |inlinebutton| image:: img/inline_ico.png

------------------
Lateral Structures
------------------

This chapter describes processing of Lateral Structures layer. There are three layers required for complete extraction of the data:

* StreamCenterline polyline layer
* LateralStructures polyline layer
* DTM layer (optional)

Both StreamCenterline and LateralStructures you can create by clicking this button |createbutton| on toolbar and choosing appropriate layers to create. You can also find it in database context menu as is shown below. Created layers are empty and must be edited manually. This guide assume that StreamCenterline layer is already done and all attributes are filled. We will focus on LateralStructures layer and its functionality.

  .. note::

     For more information about creation and edition of StreamCenterline layer please look `HERE <http://www.hec.usace.army.mil/software/hec-georas/documentation/HEC-GeoRAS_43_Users_Manual.pdf>`_ Chapter 4-7


  .. _fig_lateral_create:
  .. figure:: img/create_layer.png

     Database context menu

  .. figure:: img/lateral_create.png
     :align: center

     Create RAS Layers window

LateralStructures layer should contain “LateralSID”, “RiverCode”, “ReachCode”, “Station”, “USDistance”, “TopWidth”, “NodeName” and DtmID” attributes. Edit layer and digitize lateral structures. “LateralSID” will be filed automatically while digitizing. Remember that drawing has to be performed from upstream to downstream.

  .. _fig_lateraledit:
  .. figure:: img/lateral_edit.png
     :align: center

     Exemplary lateral structure

After finishing sketch and living edit mode go to RAS Geometry tab and from context menu choose Lateral Structures position. You will see sub menu where you can extract River/Reach Names, calculate Stationing and Elevations. There is also option to proceed all of the functions by once by clicking “All”. If particular function is done without any problem you will see message in main RiverGIS window about successful processing.

  .. _fig_lateralmenu:
  .. figure:: img/lateral_submenu.png
     :align: center

     Lateral Structures menu

Stationing is calculated basing on upstream start point of lateral structure with shortest distance to StreamCenterline. Please inspect correctness of River/Reach Names and Stationing for lateral structures. There exist probability of mistake in a situation where other channel lie closer to upstream start point of lateral structure than channel to which lateral structure should be referenced to.  For elevation extraction you need DTM which covers lateral structures extent. After clicking “Elevation” or “All” functions there will be dialog window displayed with current DTM rasters. Choose any and click “OK”.

  .. note::

     For more information about creation and edition of LateralStructures layer please look `HERE <http://www.hec.usace.army.mil/software/hec-georas/documentation/HEC-GeoRAS_43_Users_Manual.pdf>`_ Chapter 4-37

  .. _fig_lateraldtm:
  .. figure:: img/bridge_dtm.png
     :align: center

     DTM option window

You have also access to “All” function from main RiverGIS toolbar by clicking this |lateralbutton| button . “USDistance”, “TopWidth”, “NodeName” have to be filled manually by the user. DtmID will be filled after elevation extraction but for end user filled data are not important. Remember that DTM has to cover all lateral structures otherwise extraction will not proceed. If you have more than one DTM in the same extent then raster with better resolution will be chosen for processing. For elevation control after processing point layer will be added to view where you can inspect lateral structures elevation data.

  .. |lateralbutton| image:: img/lateral_ico.png
-------------
Storage Areas
-------------

``````
Create HEC-RAS GIS Import file (SDF)
``````
