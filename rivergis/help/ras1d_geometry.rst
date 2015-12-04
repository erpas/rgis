.. _stepbystep1d:

=================================
Step by step: HEC-RAS 1D Geometry
=================================

This manual presents using the RiverGIS plugin for creation of HEC-RAS 1D flow model.

RiverGIS tries to mimic the workflow of HEC-GeoRAS where it is possible and users are encouraged to read the `HEC-GeoRAS documentation`_.

  .. _HEC-GeoRAS documentation: http://rivergis.com/GeoRAS_docs/HEC_GeoRAS_10_for_ArcGIS_10.pdf

As an example, a modified *Bald Eagle* project data from *HEC-RAS Unsteady Examples* are used. The project source data can be downloaded from `rivergis.com <http://rivergis.com/download/baldeagle.zip>`_. The archive contains also QGIS project file with all the data and projection defined (NAD 1983 StatePlane Pennsylvania North FIPS 3701 Feet). Unzip the archive and open ``BaldEagle.qgs`` project file.

.. figure:: img/ras1d_bald_start.png
   :align: center

-------------------------
Typical RiverGIS workflow
-------------------------

#. :ref:`Create a new database schema for a model<ras1d_create_schema>`
#. :ref:`Set model's spatial projection <ras1d_projection>`
#. :ref:`Create/import geometry <ras1d_geometry_creation>` of the model (river lines, cross-sections, hydraulic structures)
#. :ref:`Build rivers network <ras1d_network>` (topology, i.e. reach connectivity and order, reach lengths)
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

Each table has a number of columns defining object attributes. Some of the attributes, such as ``RiverCode`` , are to be set by a user and some are produced by RiverGIS. Users should *not* change the structure of river database tables.

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
.. _user_def_attrs:

Model geometry data are stored in a river database tables. There is a table for river lines, cross-sections etc. The table below lists river database tables created by RiverGIS. If a table needs a user specified attribute, it is given in the *User defined attributes* column.

======================  ==================  ==========  =======================
Table name              Contains            Type        User defined attributes
======================  ==================  ==========  =======================
``StreamCenterlines``   river lines         polyline    ``RiverCode``
                                                        ``ReachCode``
``XSCutlines``          cross-sections      polyline    ---
``Flowpaths``           flow paths          polyline    ``LineType``:
                                                        Channel, Left or
                                                        Right
``BankLines``           channel bank lines  polyline    ---
``LeveeAlignment``      levees              polyline    ---
``IneffAreas``          ineffective flow    polygon     ``Elevation``
                        areas
``BlockedObs``          blocked             polygon     ``Elevation``
                        obstructions
``LanduseAreas``        landuse             polygon     ``N_Value``:
                                                        Manning's *n* value
``Bridges``             bridges/culverts    polyline    ``USDistance``,
                                                        ``TopWidth``
``InlineStructures``    inline structures   polyline    ``USDistance``,
                                                        ``TopWidth``
``LateralStructures``   lateral structures  polyline    ``USDistance``,
                                                        ``TopWidth``
``StorageAreas``        storage areas       polygon     ``Name``
``SAConnections``       storage areas       polyline    ``Name``
                        connections
======================  ==================  ==========  =======================

There are three tables always required for a model creation: river lines, cross-sections and flow paths. The rest is optional.

Users create new tables using ``Database`` -> ``Create River Database Tables`` or |createtables| tool. The following dialog allows for selection of tables to be created.

  .. |createtables| image:: img_ico/dbCreateRasTables.png

.. figure:: img/ras1d_create_tables.png
   :align: center

Newly created tables are automatically loaded into current QGIS project. QGIS always adds new layers above the active layer selected in the layers panel tree.

``Database`` -> ``Load River Database Tables Into QGIS`` or |loadtables| tool loads all river database tables that are not loaded already into QGIS project.

  .. |loadtables| image:: img_ico/loadRdbTablesIntoQgis.png

The loaded tables can be `edited using QGIS editing tools <http://docs.qgis.org/2.8/en/docs/user_manual/working_with_vector/editing_geometry_attributes.html>`_ or populated by importing data from other spatial layers using ``Database`` -> ``Import Layers Into River Database Tables`` or |importlayers| tool. Multiple geometry data can be specified.

  .. |importlayers| image:: img_ico/importLayersIntoRdb.png

Geometry objects created by a user must comply the rules described in `HEC-GeoRAS documentation`_, chapter 4.

We will import the Bald Eagle example data into the newly created schema. The source layers are grouped in the ``src`` group and there is ``RiverGIS`` group for data produced by the plugin. Select the ``RiverGIS`` as a target group for loading new layers before starting the import.

.. figure:: img/ras1d_import.png
   :align: center

Attribute names of the source data can differ from the database attribute names, but can be mapped easilly to the right column, as shown above. If the required attributes are empty or nonexistent, users have to fill the database columns by hand after the import.

.. figure:: img/ras1d_imported.png
   :align: center

If the source layers group is switch off, only the imported layers should be visible. In the above picture also the landuse layer is turned off for clarity.

It is always good idea to check the imported data visually and have a look into the attribute tables. Here we check the ``StreamCenterlines`` if the :ref:`required attributes <req_attrs>` are defined.

.. figure:: img/ras1d_import_check_table.png
   :align: center

Creating the HEC-RAS geometry requires all user defined attributes to be non-empty.

.. _ras1d_network:

-------------
River network
-------------

Topology
--------

==============  ========================================================================
|topology|      ``RAS Geometry`` > ``Stream Centerline Attributes`` > ``Topology``
==============  ========================================================================

The river network is built from ``StreamCenterlines`` layer by ``Topology`` |topology| tool . At each reach end a node is created (``FromNode`` and ``ToNode``), as shown below.

.. |topology| image:: img_ico/ras1dStreamCenterlinesTopology.png

.. figure:: img/ras1d_nodes.png
   :align: center

Lengths/Stations
----------------

==================  =============================================================================
|lengths_stations|  ``RAS Geometry`` > ``Stream Centerline Attributes`` > ``Lengths/Stations``
==================  =============================================================================

The ``Lengths/Station`` tool finds flow direction and calculates river stationing for each reach end. It fills ``ReachLen``, ``FromSta`` and ``ToSta`` reach attributes. Users can override the calculated values to adjust cross-sections stationing.

.. |lengths_stations| image:: img_ico/ras1dStreamCenterlinesLengthsStations.png

.. figure:: img/ras1d_length_stations_table.png
   :align: center

All
----

==============  ========================================================================
|stream_all|    ``RAS Geometry`` > ``Stream Centerline Attributes`` > ``All``
==============  ========================================================================

Runs all river network tools, i.e. ``Topology`` and ``Lengths/Stations``.

.. |stream_all| image:: img_ico/ras1dStreamCenterlinesAll.png


Copy Stream Centerlines to Flowpaths
------------------------------------

====  =================================================================================================
.      ``RAS Geometry`` > ``Stream Centerline Attributes`` > ``Copy Stream Centerlines to Flowpaths``
====  =================================================================================================

This will copy ``StreamCenterlines`` features to ``Flowpaths`` table and assign them ``Channel`` type.



--------------
Cross-sections
--------------


River/Reach Names
-----------------
==============  ========================================================================
|xs_names|      ``RAS Geometry`` > ``XS Cut Line Attributes`` > ``River/Reach Names``
==============  ========================================================================

.. |xs_names| image:: img_ico/ras1dXsRiverNames.png

Assigns each cross-sections a ``ReachID``, ``RiverCode`` and ``ReachCode`` values.


Stationing
----------

==============  ========================================================================
|xs_station|    ``RAS Geometry`` > ``XS Cut Line Attributes`` > ``Stationing``
==============  ========================================================================

  .. |xs_station| image:: img_ico/ras1dXsStationing.png

Calculates ``Station`` value for each cross-section.


Bank Stations
-------------

==============  ========================================================================
|xs_banks|      ``RAS Geometry`` > ``XS Cut Line Attributes`` > ``Bank Stations``
==============  ========================================================================

.. |xs_banks| image:: img_ico/ras1dXsBanks.png

Calculates banks positions for each cross-section. Fills ``LeftBank`` and ``RightBank`` fields in **XSCutLines** table.


Downstream Reach Lengths
------------------------

==============  ==============================================================================
|xs_dsl|        ``RAS Geometry`` > ``XS Cut Line Attributes`` > ``Downstream Reach Lengths``
==============  ==============================================================================

.. |xs_dsl| image:: img_ico/ras1dXsDSLengths.png

Calculates distances to a next downstream cross-section along a flowpath. Fills the ``LLength``, ``ChLength`` and ``RLength`` attributes of ``XSCutLines`` table.


Elevations
----------

==============  ==============================================================================
|xs_elev|       ``RAS Geometry`` > ``XS Cut Line Attributes`` > ``Elevations``
==============  ==============================================================================

.. |xs_elev| image:: img_ico/ras1dXsElevations.png

This tool generates points along cross-sections, saves them to ``XSSurface`` table and probes chosen DTM rasters for point elevation. The tool requires a proper DTM setup, i.e. which raster layers are to be probed for elevation (see :ref:`options_dtm`). Multiple raster are allowed. If rasters overlap,a raster with higher resolution is used. The rasters must completely cover all cross-sections.


All
----
==============  ==============================================================================
|xs_all|        ``RAS Geometry`` -> ``XS Cut Line Attributes`` -> ``All``
==============  ==============================================================================

  .. |xs_all| image:: img_ico/ras1dXsAll.png

Runs all the ``XSCutLines`` tools.



TODO....


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

Both StreamCenterline and Bridges/Culverts you can create by clicking this button |createtables| on toolbar and choosing appropriate layers to create. You can also find it in database context menu as is shown below. Created layers are empty and must be edited manually. This guide assume that StreamCenterline layer is already done and all attributes are filled. We will focus on Bridges/Culverts layer and its functionality.

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

  .. |bridgebutton| image:: img_ico/ras1dBridges.png

-----------------
Inline Structures
-----------------

This chapter describes processing of Inline Structures layer. There are three layers required for complete extraction of the data:

* StreamCenterlines polyline layer
* InlineStructures polyline layer
* DTM layer (optional)

Both StreamCenterline and InlineStructures you can create by clicking this button |createtables| on toolbar and choosing appropriate layers to create. You can also find it in database context menu as is shown below. Created layers are empty and must be edited manually. This guide assume that StreamCenterline layer is already done and all attributes are filled. We will focus on InlineStructures layer and its functionality.

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

  .. |inlinebutton| image:: img_ico/ras1dInlineStruct.png

------------------
Lateral Structures
------------------

This chapter describes processing of Lateral Structures layer. There are three layers required for complete extraction of the data:

* StreamCenterline polyline layer
* LateralStructures polyline layer
* DTM layer (optional)

Both StreamCenterline and LateralStructures you can create by clicking this button |createtables| on toolbar and choosing appropriate layers to create. You can also find it in database context menu as is shown below. Created layers are empty and must be edited manually. This guide assume that StreamCenterline layer is already done and all attributes are filled. We will focus on LateralStructures layer and its functionality.

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

  .. |lateralbutton| image:: img_ico/ras1dLateralStruct.png

-------------
Storage Areas
-------------

**StorageAreas** have 3 methods for volume calculations which are:

```````````````
Terrain Point Extraction
```````````````
Algorithm can be run from context menu ``RAS Geometry`` -> ``Storage Areas`` -> ``Terrain Point Extraction`` or by pressing  |extractionbutton|  button.

  .. |extractionbutton| image:: img_ico/ras1dSATerPtExtract.png

Tool generates point grid inside every storage area and probe elevation rasters with it. Spacing between points equals DTMs cellsize. Result is **SASurface** which contains those points. They are needed to calculate volume of the storages. Also remember to setup DTMs before running algorithm.

  .. note::

     Creating points grid for large storage areas and high resolution DTMs can take a while, so please be patient. Changing ``Chunk size`` value is recomended in such situations.

```````````````
Elevation-Volume Data
```````````````
Next step after ``Terrain Point Extraction`` is ``RAS Geometry`` -> ``Storage Areas`` -> ``Elevation-Volume Data``. It can also be run by pressing |volumebutton| button. Algorithm will ask you about number of slices for volume calculations.

  .. |volumebutton| image:: img_ico/ras1dSAElevVolume.png

Result is **SAVolume** table inside schema which will be used during export to SDF file.

```````````````
All
```````````````
``RAS Geometry`` -> ``Storage Areas`` -> ``All`` or  |sa_all|  button.

  .. |sa_all| image:: img_ico/ras1dStorageAreas.png

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

  .. |sac_all| image:: img_ico/ras1dSAConnections.png

It will launch all **StorageAreas** tools one after another.

-------------
Create HEC-RAS GIS Import file (SDF)
-------------



---------------
Plugin Settings
---------------
==============  ===================================================
|optionbutton|  ``Settings`` > ``Options``
==============  ===================================================

Options dialog allows users to set up the plugin parameters. Options are divided into several tabs described below.

.. |optionbutton| image:: img_ico/options.png

.. _options_general:

General Options
---------------

TODO

.. _options_db:

Database Options
----------------

TODO


.. _options_dtm:

DTM Options
-----------
  .. figure:: img/options_dtm.png
    :align: center

This options alows users to choose rasters for probing (currently only elevation is probed from rasters).

``Chunk size`` decides how many points can be load at once to memory to probe DTMs. Default value ``0`` allows the plugin to take all points at once.

