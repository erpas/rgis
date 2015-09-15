CREATE TABLE mosty."Lateral_Structures" ("LateralStrID" serial primary key, "RiverCode" text, "ReachCode" text, "Station" double precision, "USDistance" double precision, "TopWidth" double precision, "NodeName" text, geom geometry);
ALTER TABLE mosty."Lateral_Structures"
    ALTER COLUMN geom TYPE geometry(LINESTRING,2180)
 	USING ST_SetSRID(geom,2180);

CREATE INDEX idx_bridges
  	ON mosty."Lateral_Structures"
  	 	USING gist(geom);


SELECT ST_ClosestPoint(a.geom,ST_StartPoint(b.geom)) AS geom,a."RiverCode", a."ReachCode", b."LateralStrID"
	INTO mosty.pkt3
		FROM mosty."StreamCenterlines" AS a, mosty."Lateral_Structures" as b
		WHERE a.geom && b.geom;

ALTER TABLE mosty.pkt3
    ALTER COLUMN geom TYPE geometry(POINT,2180)
 	USING ST_SetSRID(geom,2180);

CREATE INDEX idx_pkt3
  	ON mosty.pkt3
  	 	USING gist(geom);





-- SELECT b."LateralStrID", b."RiverCode",b."ReachCode", (a."ToSta" - a."FromSta")*(1-ST_Line_Locate_Point(a.geom,b.geom)) AS "Station"
-- 	INTO mosty.lokalizacja3
-- 		FROM mosty."StreamCenterlines" AS a, mosty.pkt3 AS b
--         WHERE a."ReachCode" = b."ReachCode"
--         ORDER BY "ReachCode", "Station" ;
--
-- UPDATE mosty."Lateral_Structures" AS a
-- SET "Station" = b."Station", "ReachCode" = b."ReachCode", "RiverCode" = b."RiverCode"
-- 	FROM mosty.lokalizacja3 as b
--     WHERE a."LateralStrID" = b."LateralStrID";
-- DROP TABLE mosty.pkt3, mosty.lokalizacja3;