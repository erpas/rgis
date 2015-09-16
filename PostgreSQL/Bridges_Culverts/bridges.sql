-- RiverCode and RiverReach update from StreamCenterline layer
UPDATE "Dzierzgon"."Bridges" AS a
SET "RiverCode" = b."RiverCode" , "ReachCode" = b."ReachCode"
	FROM "Dzierzgon"."StreamCenterlines" AS b
    WHERE  a.geom && b.geom AND ST_Intersects(a.geom,b.geom);

-- Generating of points needed for bridges Stationing calculation
SELECT DISTINCT (ST_Dump(ST_Intersection(a.geom,b.geom))).geom AS geom,b."RiverCode", b."ReachCode", b."BridgeID"
	INTO pkt
		FROM "Dzierzgon"."StreamCenterlines" AS a, "Dzierzgon"."Bridges" as b
		WHERE a.geom && b.geom;

-- Calculation of bridges Stationing
SELECT b."BridgeID", b."RiverCode",b."ReachCode", (a."ToSta" - a."FromSta")*(1-ST_Line_Locate_Point(a.geom,b.geom)) AS "Station"
	INTO lokalizacja
		FROM "Dzierzgon"."StreamCenterlines" AS a, pkt AS b
        WHERE a."ReachCode" = b."ReachCode"
        ORDER BY "ReachCode", "Station" ;

-- Update of Bridges layer by Stationing values
UPDATE "Dzierzgon"."Bridges" AS a
SET "Station" = b."Station"
	FROM lokalizacja as b
    WHERE a."BridgeID" = b."BridgeID";
DROP TABLE pkt, lokalizacja;
