.. _stepbystep1d:

=================================
Step by step: HEC-RAS 1D Geometry
=================================

RiverGIS tries to mimic the workflow of HEC-GeoRAS where it is possible and users are encouraged to read the `HEC-GeoRAS documentation`_.

  .. _HEC-GeoRAS documentation: http://rivergis.com/GeoRAS_docs/HEC_GeoRAS_10_for_ArcGIS_10.pdf


-------------------------
Typical RiverGIS workflow
-------------------------

#. :ref:`Create a new database schema for a model<ras1d_create_schema>`
#. :ref:`Set model's spatial projection <ras1d_projection>`
#. :ref:`Create/import geometry <ras1d_geometry_creation>` of the model (river lines, cross-sections, hydraulic structures)
#. Build river network topology (reach connectivity and order, reach lengths)
#. Calculate cross-sections' attributes (stations, downstream lengths, etc.)
#. Probe vertical shape of cross-sections from a DTM raster(s)
#. Define additional cross-sections' data (banks, levees, ineffecive flow areas, obstructions et.)
#. Find Manning's roughness coefficients for each cross-section
#. Build hydraulic structures (bridges/culverts, inline and lateral structures, storage areas, etc.).
#. Create HEC-RAS GIS Import file (*.sdf)

.. _ras1d_create_schema:

----------------------
Create database schema
----------------------

A fundamental difference from HEC-GeoRAS is that the RiverGIS uses a ``PostgreSQL`` database with ``PostGIS`` spatial extension for data storage (see :ref:`requirements` for installation instructions). A term *river database* refers to a database used by RiverGIS. Until a database and schema are set in RiverGIS window, most of the tools are inactive.

A single ``PostgreSQL`` database can be used to store many models geometries. Each model goes to its own `schema <http://www.postgresql.org/docs/current/static/ddl-schemas.html>`_, a kind of database directory for data grouping. Therefore, the first step is to create a new schema for a model.

Users can create a schema in a number of ways: using `pgAdmin <http://pgadmin.org>`_, QGIS' own `DB Manager <http://docs.qgis.org/2.8/en/docs/user_manual/plugins/plugins_db_manager.html>`_ or from within RiverGIS dialog by choosing ``Database`` > ``Create New Schema`` or clicking |createschema| tool icon from Database toolbar. RiverGIS will automatically switch to the newly created schema, as shown below.

.. |createschema| image:: img_ico/dbCreateSchema.png

.. figure:: img/ras1d_new_schema_created.png
   :align: center

HEC-RAS 1D flow model geometry consist of rivers network, cross-sections and, optionally, hydraulic structures such as weirs, bridges or storage areas. Users have an option to import spatial data to the database from other data formats (i.e. ESRI Shapefiles) or create it from scratch.

.. note::
    In PostgreSQL spatial layer data are kept in tables. In this manual we will use terms *table* and *layer* interchangably.

Each table has a number of columns defining object attributes. Some of the attributes, such as `RiverCode` (a river name), are to be set by a user and some are produced by RiverGIS. Users should *not* change the structure of river database tables.

.. _ras1d_projection:

------------------------
Model spatial projection
------------------------

.. note::
    Spatial data are always stored using a projection. See QGIS Manual for `Working with Projections <http://docs.qgis.org/2.2/en/docs/user_manual/working_with_projections/working_with_projections.html>`_

.. figure:: img/ras1d_projection.png
   :align: center

Before creating geometry objects users must choose a projection for a model data using projection selector at the bottom of RiverGIS window (shown above). **All the model geometry data must use projection defined in the projection selector**. If data for a model already exist in a spatial layer a user must check its projection for consistency with a projection chosen in RiverGIS projection selector and convert it if needed.

.. _ras1d_geometry_creation:

------------------------------
Model Geometry Creation/Import
------------------------------

Model geometry data are stored in a river database tables. There is a table for river lines, cross-sections etc. The table below lists river database tables that can be created by RiverGIS. If a table needs a user specified attribute, it is given in the *Required attributes* column.

======================  ==================  ==========  ====================
Table name              Contains            Type        Required attributes
======================  ==================  ==========  ====================
``StreamCenterlines``   river lines         polyline    ``RiverCode``
                                                        ``ReachCode``
``XSCutlines``          cross-sections      polyline    ---
``Flowpaths``           flow paths          polyline    ``LineType`` ---
                                                        Channel, Left or
                                                        Right
``BankLines``           channel bank lines  polyline    ---
``LeveeAlignment``      levees              polyline    ---
``IneffAreas``          ineffective flow    polygon     ``Elevation``
                        areas
``BlockedObs``          blocked             polygon     ``Elevation``
                        obstructions
``LanduseAreas``        landuse             polygon     ``N_Value`` ---
                                                        Manning's *n* value
``Bridges``             bridges/culverts    polyline    ---
``InlineStructures``    inline structures   polyline    ---
``LateralStructures``   lateral structures  polyline    ---
``StorageAreas``        storage areas       polygon     ---
``SAConnections``       storage areas       polyline    ---
                        connections
======================  ==================  ==========  ====================

There three tables always required for a model creation: river lines, cross-sections and flow paths. The rest is optional.

Users create new tables using ``Database`` -> ``Create River Database Tables`` or |createtables| tool. The following dialog allows for selection of tables to be created.

  .. |createtables| image:: img_ico/dbCreateRasTables.png

.. figure:: img/ras1d_create_tables.png
   :align: center

Newly created tables are automatically loaded into current QGIS project. Users have an option to add all tables into QGIS project using ``Database`` -> ``Load River Database Tables Into QGIS`` or |loadtables| tool. RiverGIS finds all geometry data tables in the current schema and adds them into QGIS project.

  .. |loadtables| image:: img_ico/loadRdbTablesIntoQgis.png

The loaded tables can be `edited using QGIS editing tools <http://docs.qgis.org/2.8/en/docs/user_manual/working_with_vector/editing_geometry_attributes.html>`_ or populated by importing data from other spatial layers using ``Database`` -> ``Import Layers Into River Database Tables`` or |importlayers| tool. Multiple geometry data can be specified.

  .. |importlayers| image:: img_ico/importLayersIntoRdb.png


Here, we use modified Bald Eagle project data from HEC-RAS Unsteady Examples. The project spatial data can be downloaded from `rivergis.com <http://rivergis.com/examples/baldeagle.zip>`_. The archive contains also QGIS project file with all the data and projection defined (NAD 1983 StatePlane Pennsylvania North FIPS 3701 Feet). Unzip the archive and open the QGIS project ``BaldEagle.qgs``.

.. figure:: img/ras1d_bald_start.png
   :align: center

The data should be always inspected before importing into a river database. At least layer's projection should be the same as RiverGIS projection. If the source layer's attribute names differ from the database table required attribute, you can always map a source attribute name to the right column. If the required attributes are empty or nonexistant, you will have to fill the database columns by hand after the import.

The Bald Eagle example contains river lines, cross-sections, flowpaths, banklines etc. --- let's import them all to a new schema.




* Before running RiverGIS tools we recommend to **setup DTM options first**. You have to add DTM tiles into QGIS view and select them from ``Settings`` -> ``Options``  or  |optionbutton| in ``DTM`` tab. If you have high resolution DTMs consider changing ``Chunk size`` value. This option says how many points can be load at once to memory to probe DTMs. Default value is ``'0'`` and it means that RiverGIS will try to take all points at once into the analysis.

  .. |optionbutton| image:: img_ico/options.png

  .. _fig_bridgdtm:
  .. figure:: img/dtm_setup.png
     :align: center

     DTM option window

------------------
Stream Centerlines
------------------

If you have properly prepared stream network layer you can use such RiverGIS tools as:

```````````````
Topology
```````````````
``RAS Geometry`` -> ``Stream Centerline Attributes`` -> ``Topology`` or  |topology|  button.

  .. |topology| image:: img_ico/ras1dStreamCenterlinesTopology.png
This tool builds topology over **StreamCenterlines** table and fill *'FromNode'* and *'ToNode'* fields. It will also create auxiliary **NodesTable** table inside schema.

  .. note::

    Remember to split network lines on every reach intersection (junctions).

```````````````
Lengths/Stations
```````````````
``RAS Geometry`` -> ``Stream Centerline Attributes`` -> ``Lengths/Stations`` or |lengths_stations|  button.

  .. |lengths_stations| image:: img_ico/ras1dStreamCenterlinesLengthsStations.png
This tool calculates reaches lengths taking into account stream network topology. It will fill *'ReachLen'*, *'FromSta'*, *'ToSta'* fields and generate **Endpoints** auxiliary table.

```````````````
All
```````````````
``RAS Geometry`` -> ``Stream Centerline Attributes`` -> ``All`` or  |stream_all|  button.

  .. |stream_all| image:: img_ico/ras1dStreamCenterlinesAll.png
It will launch all tools (defined above) for **StreamCenterlines** geometry one after another.

```````````````
Copy Stream Centerlines to Flowpaths
```````````````
``RAS Geometry`` -> ``Stream Centerline Attributes`` -> ``Copy Stream Centerlines to Flowpaths``

This option is for copying features from **StreamCenterlines** table to **Flowpaths** as *'Channel'* type.

  .. note::

    **Flowpaths** empty table have to be created before running this tool. You can use |createbutton| button.


------------------------
Cross-sections Cut Lines
------------------------

If you have properly prepared cross-sections layer you can use such RiverGIS tools as:

```````````````
River/Reach Names
```````````````
``RAS Geometry`` -> ``XS Cut Line Attributes`` -> ``River/Reach Names`` or  |xs_names|  button.

  .. |xs_names| image:: img_ico/ras1dXsRiverNames.png
This tool assigns *'ReachID'*, *'RiverCode'* and *'ReachCode'* values from **StreamCenterlines** layer to cross sections. Each cross section can intersect only once with any **StreamCenterlines** feature.

```````````````
Stationing
```````````````

``RAS Geometry`` -> ``XS Cut Line Attributes`` -> ``Stationing`` or |xs_stationing|  button.

  .. |xs_stationing| image:: img_ico/ras1dXsStationing.png
This tool calculates *'Station'* values for each cross section based on the intersection with river. Note that each cross section can have only one intersection point with river. Each cross section can intersect only once with any **StreamCenterlines** feature.

```````````````
Bank Stations
```````````````
``RAS Geometry`` -> ``XS Cut Line Attributes`` -> ``Bank Stations`` or  |xs_banks|  button.

  .. |xs_banks| image:: img_ico/ras1dXsBanks.png
This tool calculates fraction on which features from **BankLines** table intersects with each cross section and decides if bank is left or right. Calculated values fills *'LeftBank'* and *'RightBank'* fields in **XSCutLines** table.

```````````````
Downstream Reach Lengths
```````````````
``RAS Geometry`` -> ``XS Cut Line Attributes`` -> ``Downstream Reach Lengths`` or  |xs_dsl|  button.

  .. |xs_dsl| image:: img_ico/ras1dXsDSLengths.png
This tool calculates each cross section station along flow paths. Calculated values fills *'LLength'*, *'ChLength'* and *'RLength'* fields in **XSCutLines**.

```````````````
Elevations
```````````````

``RAS Geometry`` -> ``XS Cut Line Attributes`` -> ``Elevations`` or  |xs_elev|  button.

  .. |xs_elev| image:: img_ico/ras1dXsElevations.png
This tool generates points along cross sections (and saves them into **XSSurface** table) and use them to probe DTM rasters.

  .. note::

    Before running tool you should customize DTM options. But if you forgot - don't worry -  DTM options dialog will appear anyway. ;)

```````````````
All
```````````````
``RAS Geometry`` -> ``XS Cut Line Attributes`` -> ``All`` or  |xs_all|  button.

  .. |xs_all| image:: img_ico/ras1dXsAll.png
It will launch all **XSCutLines** tools one after another.


---------------------
Flow Path Centerlines
---------------------
There are 2 methods connected with **FlowPaths** geometry type. Both were already shortly introduced in chapters about **StreamCenterlines** and **XSCutLines**:

```````````````
Copy Stream Centerlines to Flowpaths
```````````````
* ``RAS Geometry`` -> ``Stream Centerline Attributes`` -> ``Copy Stream Centerlines to Flowpaths``

```````````````
Downstream Reach Lengths
```````````````
* ``RAS Geometry`` -> ``XS Cut Line Attributes`` -> ``Downstream Reach Lengths`` or  |xs_dsl|  button.

---------------------
Main Channel Banks
---------------------
There is only one method for **BankLines** layer and it depends on **XSCutLines** polyline layer.

```````````````
Bank Stations
```````````````
It can be run from context menu ``RAS Geometry`` -> ``XS Cut Line Attributes`` -> ``Bank Stations`` or by pressing   |xs_banks|  button.

--------
Land Use Areas
--------
**LanduseAreas** layer have one method and it depends on **XSCutLines** polyline layer.

```````````````
Extract Manning's n Values
```````````````
``RAS Geometry`` -> ``Extract Manning's n Values`` or  |manbutton|  button.

  .. |manbutton| image:: img_ico/ras1dXsMannings.png

  .. note::

     For more information about creation and edition of XSCutLines and LanduseAreas layers please look `HERE <http://www.hec.usace.army.mil/software/hec-georas/documentation/HEC-GeoRAS_43_Users_Manual.pdf>`_ Chapter 4-11 and 4-28


**LanduseAreas** layer must contain *'LUID'*, *'LUCode'* and *'N_Value'* attributes and it should contain *multipart* polygons. In this example *'LUID'* and *'LUCode'* is the same but it can be different.

  .. _fig_man_luatttable:
  .. figure:: img/lu_att_table.png
     :align: center

     Exemplary Landuse attribute table

For correct Manning's values extraction all of the cross sections in **XSCutLines** layer have to cover land use polygons

  .. _fig_man_xslupic:
  .. figure:: img/xs_lu_pic.png
     :align: center

     Cross sections and Land use layers coverage

After running tool you should obtain **Manning** table with *'XsecID'*, *'Fraction'*, *'N_Value'* and *'LUCode'* attributes. Table will be added to view and in this form is ready for SDF export.

  .. _fig_man_mantable:
  .. figure:: img/man_table.png
     :align: center

     Exemplary Manning's values table

----------------
Levee Alignments
----------------
There is one method for **LeveeAlignments** layer and it depends on **XSCutLines** polyline layer.

```````````````
Levees
```````````````
It can be run from context menu ``RAS Geometry`` -> ``Levees`` or by pressing  |leveebutton|  button.

  .. |leveebutton| image:: img_ico/ras1dXsLevees.png

Result is **LeveePoints** table inside schema which will be used during export to SDF file.

-----------------
Ineffective Areas
-----------------
There is one method for **IneffAreas** layer and it depends on **XSCutLines** polyline layer.

```````````````
Ineffective Flow Areas
```````````````
It can be run from context menu ``RAS Geometry`` -> ``Ineffective Flow Areas`` or by pressing  |ineffbutton|  button.

  .. |ineffbutton| image:: img_ico/ras1dXsIneffective.png

Result is **IneffLines** table inside schema which will be used during export to SDF file.

--------------------
Blocked Obstructions
--------------------
There is one method for **BlockedObs** layer and it depends on **XSCutLines** polyline layer.

```````````````
Blocked Obstructions
```````````````
It can be run from context menu ``RAS Geometry`` -> ``Blocked Obstructions`` or by pressing  |blockbutton|  button.

  .. |blockbutton| image:: img_ico/ras1dXsBlockedObs.png

Result is **BlockLines** table inside schema which will be used during export to SDF file.

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

**StorageAreas** have 3 methods for volume calculations which are:

```````````````
Terrain Point Extraction
```````````````
Algorithm can be run from context menu ``RAS Geometry`` -> ``Storage Areas`` -> ``Terrain Point Extraction`` or by pressing  |extractionbutton|  button.

  .. |extractionbutton| image:: img_ico\ras1dSATerPtExtract.png

Tool generates point grid inside every storage area and probe elevation rasters with it. Spacing between points equals DTMs cellsize. Result is **SASurface** which contains those points. They are needed to calculate volume of the storages. Also remember to setup DTMs before running algorithm.

  .. note::

     Creating points grid for large storage areas and high resolution DTMs can take a while, so please be patient. Changing ``Chunk size`` value is recomended in such situations.

```````````````
Elevation-Volume Data
```````````````
Next step after ``Terrain Point Extraction`` is ``RAS Geometry`` -> ``Storage Areas`` -> ``Elevation-Volume Data``. It can also be run by pressing |volumebutton| button. Algorithm will ask you about number of slices for volume calculations.

  .. |volumebutton| image:: img_ico\ras1dSAElevVolume.png

Result is **SAVolume** table inside schema which will be used during export to SDF file.

```````````````
All
```````````````
``RAS Geometry`` -> ``Storage Areas`` -> ``All`` or  |sa_all|  button.

  .. |sa_all| image:: img_ico\ras1dStorageAreas.png
It will launch all **StorageAreas** tools one after another.


-------------
Storage Areas Connections
-------------

**SAConnections** is another geometry class related with storage areas. Tool has 3 methods which are:

```````````````
Assign Nearest SA
```````````````
Algorithm can be run from context menu ``RAS Geometry`` -> ``Storage Areas Connections`` -> ``Assign Nearest SA``. This tool defines which storage area is upstream and downstream. It saves results (which is *'StorageID'* from **StorageAreas**) in *'USSA'* and *'DSSA'* columns inside **SAConnections** table.

```````````````
Elevations
```````````````
``RAS Geometry`` -> ``Storage Areas Connections`` -> ``Elevations``.

This tool generates points along storage area connections (and saves them into **SACSurface** table) and use them to probe DTM rasters.

```````````````
All
```````````````
``RAS Geometry`` -> ``Storage Areas Connections`` -> ``All`` or  |sac_all|  button.

  .. |sac_all| image:: img_ico\ras1dSAConnections.png
It will launch all **StorageAreas** tools one after another.

-------------
Create HEC-RAS GIS Import file (SDF)
-------------
