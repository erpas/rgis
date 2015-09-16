
-- Looking closest point to the lateral structure on stream centerline layer and calculating distance between
-- lateral structure and stream centerline layer. As a result we obtain number of points which intersects
-- not only closest river line but all lines in naighborhood

DROP TABLE IF EXISTS pkt3;
SELECT ST_ClosestPoint(a.geom,ST_StartPoint(b.geom)) AS geom, ST_Distance(a.geom,ST_StartPoint(b.geom)) AS dist, a."RiverCode", a."ReachCode", b."LateralStrID"
	INTO pkt3
		FROM "Dzierzgon"."StreamCenterlines" AS a, "Dzierzgon"."Lateral_Structures" AS b
		WHERE a.geom && b.geom ORDER BY b."LateralStrID";

ALTER TABLE pkt3
    ALTER COLUMN geom TYPE geometry(POINT,2180)
 	USING ST_SetSRID(geom,2180);

CREATE INDEX idx_pkt3
  	ON pkt3
  	 	USING gist(geom);

--- Selection of points which have the smalest distance to the river
DROP TABLE IF EXISTS pkt4;
SELECT "LateralStrID","RiverCode", "ReachCode", dist, geom INTO pkt4
FROM (
  SELECT "LateralStrID","RiverCode", "ReachCode", dist, geom, RANK() OVER (PARTITION BY "LateralStrID"  ORDER BY dist) AS rnk
  FROM pkt3) AS temp
WHERE rnk = 1;

ALTER TABLE pkt4
    ALTER COLUMN geom TYPE geometry(POINT,2180)
 	USING ST_SetSRID(geom,2180);

CREATE INDEX idx_pkt4
  	ON pkt4
  	 	USING gist(geom);

--- Calculation of Stationing for those points
SELECT b."LateralStrID", b."RiverCode",b."ReachCode", (a."ToSta" - a."FromSta")*(1-ST_Line_Locate_Point(a.geom,b.geom)) AS "Station"
	INTO lokalizacja3
		FROM "Dzierzgon"."StreamCenterlines" AS a, pkt4 AS b
        WHERE  a."ReachCode" = b."ReachCode"
        ORDER BY "ReachCode", "Station" ;
        
--- Update Lateral_Structure layer by dane from previos step basing on LateralStrID
UPDATE "Dzierzgon"."Lateral_Structures" AS a
SET "Station" = b."Station", "ReachCode" = b."ReachCode", "RiverCode" = b."RiverCode"
	FROM lokalizacja3 as b
    WHERE a."LateralStrID" = b."LateralStrID";
DROP TABLE pkt3, pkt4, lokalizacja3;