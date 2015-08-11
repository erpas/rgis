#CREATE TABLE <schema_name>.<table_name>(<column_name>)
#SELECT AddgeometryColumn('<schema_name>','<table_name>','<column_name>','<SRID>','<type>','<dimension>'


#StreamCenterline 
CREATE TABLE <schema_name>.StreamCenterline(HydroID Decimal, RiverCode Varchar(16), ReachCode Varchar(16), FromNode numeric, ToNode numeric, ArcLength real, FromSta real, ToSta real);
SELECT AddGeometryColumn('<schema_name>', 'StreamCenterline', 'line', -1, 'LINESTRING', 2)

#BankLines
CREATE TABLE <schema_name>.BankLines(HydroID Decimal);
SELECT AddGeometryColumn('<schema_name>', 'banklines', 'line', -1, 'LINESTRING', 2)

#BankPoints
CREATE TABLE <schema_name>.BankPoints(BankPosition Real);
SELECT AddGeometryColumn('<schema_name>', 'bankpoints', 'point', -1, 'POINT', 2)

#Flowpaths
CREATE TABLE <schema_name>.Flowpaths(LineType Varchar(7));
SELECT AddGeometryColumn('<schema_name>', 'flowpaths', 'line', -1, 'LINESTRING', 2)

#XSCutLines
CREATE TABLE <schema_name>.XSCutLines(HydroID Decimal, Station Real, RiverCode Varchar(16), ReachCode Varchar(16), LeftBank Real, RightBank Real, Llength Real, ChLength Real, Rlength Real, NodeName Varchar(32));
SELECT AddGeometryColumn('<schema_name>', 'xscutlines', 'line', -1, 'LINESTRING', 2)

#Bridges
CREATE TABLE <schema_name>.Bridges(HydroID Decimal, RiverCode Varchar(16), ReachCode Varchar(16), Station Real, USDistance Real, TopWidth Real, NodeName Varchar(32));
SELECT AddGeometryColumn('<schema_name>', 'bridges', 'line', -1, 'LINESTRING', 2)

#InefAreas
CREATE TABLE <schema_name>.InefAreas(HydroID Decimal);
SELECT AddGeometryColumn('<schema_name>', 'inefareas', 'polygon', -1, 'POLYGON', 2)

#BlockedObs
CREATE TABLE <schema_name>.BlockedObs(HydroID Decimal);
SELECT AddGeometryColumn('<schema_name>', 'blockedobs', 'polygon', -1, 'POLYGON', 2)

#LandusesAreas
CREATE TABLE <schema_name>.LandusesAreas(LuCode Varchar(32), N_Value Real);
SELECT AddGeometryColumn('<schema_name>', 'landusesareas', 'polygon', -1, 'POLYGON', 2)

#LeveeAlignment
CREATE TABLE <schema_name>.LeveeAlignment(HydroID Decimal);
SELECT AddGeometryColumn('<schema_name>', 'leveealignment', 'line', -1, 'LINESTRING',2)

#LeveePoints
CREATE TABLE <schema_name>.LeveePoints(LeveeID Decimal, Station Real, Elevation Real);
SELECT AddGeometryColumn('<schema_name>', 'leveepoints', 'point', -1, 'POINT',2)

#InlineStructures
CREATE TABLE <schema_name>.InlineStructures(HydroID Decimal, RiverCode Varchar(16), ReachCode Varchar(16), Station Real, USDistance Real, TopWidth Real, NodeName Varchar(32));
SELECT AddGeometryColumn('<schema_name>', 'inlinestructures', 'line', -1, 'LINESTRING', 2)

#LateralStructures
CREATE TABLE <schema_name>.LateralStructures(HydroID Decimal, RiverCode Varchar(16), ReachCode Varchar(16), Station Real, USDistance Real, TopWidth Real, NodeName Varchar(32));
SELECT AddGeometryColumn('<schema_name>', 'lateralstructures', 'line', -1, 'LINESTRING', 2)

#StorageAreas
CREATE TABLE <schema_name>.StorageAreas(HydroID Decimal, MaxElev Real, MinElev Real, UserElev Real);
SELECT AddGeometryColumn('<schema_name>', 'storageareas', 'polygon', -1, 'POLYGON', 2)

#SAConnections
CREATE TABLE <schema_name>.SAConnections(HydroID Decimal, USSA Decimal, DSSA Decimal, TopWidth Real);
SELECT AddGeometryColumn('<schema_name>', 'saconnections', 'line', -1, 'LINESTRING', 2)

#StreamCenterline3D
CREATE TABLE <schema_name>.StreamCenterline3D(HydroID Decimal, RiverCode Varchar(16), ReachCode Varchar(16), FromNode numeric, ToNode numeric, ArcLength real, FromSta real, ToSta real);
SELECT AddGeometryColumn('<schema_name>', 'streamcenterline3d', 'line', -1, 'LINESTRINGZ', 3)

#XSCutLines3D
CREATE TABLE <schema_name>.XSCutLines3D(HydroID Decimal, Station Real, RiverCode Varchar(16), ReachCode Varchar(16), LeftBank Real, RightBank Real, Llength Real, ChLength Real, Rlength Real, NodeName Varchar(32));
SELECT AddGeometryColumn('<schema_name>', 'xscutlines3d', 'line', -1, 'LINESTRINGZ', 3)

#Bridges3D
CREATE TABLE <schema_name>.Bridges3D(HydroID Decimal, RiverCode Varchar(16), ReachCode Varchar(16), Station Real, USDistance Real, TopWidth Real, NodeName Varchar(32));
SELECT AddGeometryColumn('<schema_name>', 'bridges3d', 'line', -1, 'LINESTRINGZ', 3)