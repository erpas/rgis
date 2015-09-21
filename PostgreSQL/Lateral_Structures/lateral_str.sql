
-- Looking closest point to the lateral structure on stream centerline layer and calculating distance between
-- lateral structure and stream centerline layer. As a result we obtain number of points which intersects
-- not only closest river line but all lines in neighborhood

DROP TABLE IF EXISTS "Dzierzgon".riverclosestpoint1;
SELECT ST_ClosestPoint(a.geom,ST_StartPoint(b.geom)) AS geom, ST_Distance(a.geom,ST_StartPoint(b.geom)) AS dist, a."RiverCode", a."ReachCode", b."LateralStrID"
	INTO "Dzierzgon".riverclosestpoint1
		FROM "Dzierzgon"."StreamCenterlines" AS a, "Dzierzgon"."Lateral_Structures" AS b
		WHERE a.geom && b.geom ORDER BY b."LateralStrID";

ALTER TABLE "Dzierzgon".riverclosestpoint1
    ALTER COLUMN geom TYPE geometry(POINT,2180)
 	USING ST_SetSRID(geom,2180);

CREATE INDEX idx_riverclosestpoint1
  	ON "Dzierzgon".riverclosestpoint1
  	 	USING gist(geom);

--- Selection of points which have the smallest distance to the river
DROP TABLE IF EXISTS "Dzierzgon".riverclosestpoint2;
SELECT "LateralStrID","RiverCode", "ReachCode", dist, geom INTO "Dzierzgon".riverclosestpoint2
FROM (
  SELECT "LateralStrID","RiverCode", "ReachCode", dist, geom, RANK() OVER (PARTITION BY "LateralStrID"  ORDER BY dist) AS rnk
  FROM "Dzierzgon".riverclosestpoint1) AS temp
WHERE rnk = 1;

ALTER TABLE "Dzierzgon".riverclosestpoint2
    ALTER COLUMN geom TYPE geometry(POINT,2180)
 	USING ST_SetSRID(geom,2180);

CREATE INDEX idx_riverclosestpoint2
  	ON "Dzierzgon".riverclosestpoint2
  	 	USING gist(geom);

--- Calculation of Stationing for those points
DROP TABLE IF EXISTS "Dzierzgon".tempstatclosestpoints;
SELECT b."LateralStrID", b."RiverCode",b."ReachCode", (a."ToSta" - a."FromSta")*(1-ST_Line_Locate_Point(a.geom,b.geom)) AS "Station"
	INTO "Dzierzgon".tempstatclosestpoints
		FROM "Dzierzgon"."StreamCenterlines" AS a, "Dzierzgon".riverclosestpoint2 AS b
        WHERE  a."ReachCode" = b."ReachCode"
        ORDER BY "ReachCode", "Station" ;
        
--- Update Lateral_Structure layer by dane from previous step basing on LateralStrID
UPDATE "Dzierzgon"."Lateral_Structures" AS a
SET "Station" = b."Station", "ReachCode" = b."ReachCode", "RiverCode" = b."RiverCode"
	FROM "Dzierzgon".tempstatclosestpoints as b
    WHERE a."LateralStrID" = b."LateralStrID";
DROP TABLE "Dzierzgon".riverclosestpoint1, "Dzierzgon".riverclosestpoint2, "Dzierzgon".tempstatclosestpoints;