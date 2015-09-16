"""Looking closest point to the lateral structure on stream centerline layer and  
calculating distance between lateral structure and stream centerline layer. 
As a result we obtain number of points which intersects not only closest river line but all lines in naighborhood """
DROP TABLE IF EXISTS mosty.pkt3;
SELECT ST_ClosestPoint(a.geom,ST_StartPoint(b.geom)) AS geom, ST_Distance(a.geom,ST_StartPoint(b.geom)) AS dist, a."RiverCode", a."ReachCode", b."LateralStrID"
	INTO mosty.pkt3
		FROM mosty."StreamCenterlines" AS a, mosty."Lateral_Structures" AS b
		WHERE a.geom && b.geom ORDER BY b."LateralStrID";

ALTER TABLE mosty.pkt3
    ALTER COLUMN geom TYPE geometry(POINT,2180)
 	USING ST_SetSRID(geom,2180);

CREATE INDEX idx_pkt3
  	ON mosty.pkt3
  	 	USING gist(geom);

"""Selection of points which have the smalest distance to the river"""
DROP TABLE IF EXISTS mosty.pkt4;
SELECT "LateralStrID","RiverCode", "ReachCode", dist, geom INTO mosty.pkt4
FROM (
  SELECT "LateralStrID","RiverCode", "ReachCode", dist, geom, RANK() OVER (PARTITION BY "LateralStrID"  ORDER BY dist) AS rnk
  FROM mosty.pkt3) AS sub
WHERE rnk = 1;

ALTER TABLE mosty.pkt4
    ALTER COLUMN geom TYPE geometry(POINT,2180)
 	USING ST_SetSRID(geom,2180);

CREATE INDEX idx_pkt4
  	ON mosty.pkt4
  	 	USING gist(geom);

"""Calculation of Stationing for those points"""
SELECT b."LateralStrID", b."RiverCode",b."ReachCode", (a."ToSta" - a."FromSta")*(1-ST_Line_Locate_Point(a.geom,b.geom)) AS "Station"
	INTO mosty.lokalizacja3
		FROM mosty."StreamCenterlines" AS a, mosty.pkt4 AS b
        WHERE  a."ReachCode" = b."ReachCode"
        ORDER BY "ReachCode", "Station" ;
        
"""Update Lateral_Structure layer by dane from previos step basing on LateralStrID """
UPDATE mosty."Lateral_Structures" AS a
SET "Station" = b."Station", "ReachCode" = b."ReachCode", "RiverCode" = b."RiverCode"
	FROM mosty.lokalizacja3 as b
    WHERE a."LateralStrID" = b."LateralStrID";
DROP TABLE mosty.pkt3, mosty.pkt4, mosty.lokalizacja3;