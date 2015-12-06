.. _stepbystep2d:

=================================
Step by step: HEC-RAS 2D Geometry
=================================

This manual presents creating HEC-RAS 2D Flow Areas in RiverGIS plugin. 2D functionality is introduced in HEC-RAS version 5.0. Users are strongly encouraged to read the `2D Modeling with HEC-RAS 5.0`_.

  .. _2D Modeling with HEC-RAS 5.0: http://rivergis.com/GeoRAS_docs/2D_Modeling_with_HEC_RAS_50.pdf

The following layers are used for 2d flow geometry:

1. ``FlowAreas2D`` (required) --- a polygon layer with a name and mesh spacing attributes:
  * ``Name`` --- 2D Flow Area name
  * ``CellSize`` --- a default mesh cell size for a flow area.

2. ``BreakLines2D`` (optional) --- a polyline layer for aligning cell faces along the breaklines with attributes:
  * ``CellSizeAlong`` --- default mesh points spacing along a structure
  * ``CellSizeAcross`` --- default mesh points spacing across a structure
  * ``RowsAligned`` --- number of mesh rows that should be aligned to a breakline

3. ``BreakPoints2D`` (optional) --- a point layer for creating a cell face at exact locations along the breaklines (optional). No attributes required.

4. ``DTM`` (required) --- a digital terrain raster layers set.



