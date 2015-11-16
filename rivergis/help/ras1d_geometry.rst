.. _stepbystep1d:

=================================
Step by step: HEC-RAS 1D Geometry
=================================

****************************
Create geometry of the model
****************************

Required data of the model geometry:

1. River centerlines (polylines)

2. Cross-sections (polylines)

3. DTM, digital terrain model --- a raster layer


Optional geometry data:

4. Channel Bank lines

5. Flow Paths --- flow centerlines for each cross-section part: main channel, right and left overbank (polylines)

6. Levees (polylines)

7. Ineffecive flow areas (polygons)

8. Blocked obstructions (polygons)

9. Land cover (polygons)

Trzeba napisać o tym, że dane mogą zostac zaimportowane do bazy z instniejących warstw lub stworzone od nowa w pustych tabelach bazy. Cos jak:

* Create empty river database tables of HEC-RAS geometry data
* Import the model geometry from existing layers loaded into a QGIS project

------------------
Stream Centerlines
------------------

------------------
Main Channel Banks
------------------


---------------------
Flow Path Cemterlines
---------------------


------------------------
Cross-sections Cut Lines
------------------------

----------------
Bridges/Culverts
----------------

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


-----------------
inline Structures
-----------------

------------------
lateral Structures
------------------



-------------
Storage Areas
-------------


************************************
Create HEC-RAS GIS Import file (SDF)
************************************


