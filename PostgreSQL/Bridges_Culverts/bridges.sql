UPDATE mosty."Bridges" AS a
SET "RiverCode" = b."RiverCode" , "ReachCode" = b."ReachCode" FROM mosty."StreamCenterlines" AS b
WHERE ST_Intersects(a.geom,b.geom);




SELECT DISTINCT (ST_Dump(ST_Intersection(a.geom,b.geom))).geom AS geom,b."RiverCode", b."ReachCode", b."BridgeID"  INTO mosty.pkt
FROM mosty."StreamCenterlines" AS a, mosty."Bridges" as b;
ALTER TABLE mosty.pkt
	ALTER COLUMN geom TYPE geometry(POINT,2180)
	USING ST_SetSRID(geom,2180);




SELECT b."BridgeID", b."RiverCode",b."ReachCode", (a."ToSta" - a."FromSta")*(1-ST_Line_Locate_Point(a.geom,b.geom)) AS "Station" INTO mosty.lokalizacja FROM mosty."StreamCenterlines" AS a, mosty.pkt AS b
WHERE a."ReachCode" = b."ReachCode"
ORDER BY "ReachCode", "Station" ;



UPDATE mosty."Bridges" AS a
SET "Station" = b."Station" FROM mosty.lokalizacja as b
WHERE  a."BridgeID" = b."BridgeID";

DROP TABLE mosty.pkt, mosty.lokalizacja;