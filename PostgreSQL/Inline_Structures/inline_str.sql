"""RiverCode and RiverReach update from StreamCenterline layer"""
UPDATE mosty."Inline_Structures" AS a
SET "RiverCode" = b."RiverCode" , "ReachCode" = b."ReachCode"
	FROM mosty."StreamCenterlines" AS b
    WHERE  a.geom && b.geom AND ST_Intersects(a.geom,b.geom);

"""Generating of points needed for Inline_Structures Stationing calculation"""
SELECT DISTINCT (ST_Dump(ST_Intersection(a.geom,b.geom))).geom AS geom,b."RiverCode", b."ReachCode", b."InlineStrID"
	INTO mosty.pkt2
		FROM mosty."StreamCenterlines" AS a, mosty."Inline_Structures" as b
		WHERE a.geom && b.geom;

"""Calculation of Inline_Structures Stationing"""
SELECT b."InlineStrID", b."RiverCode",b."ReachCode", (a."ToSta" - a."FromSta")*(1-ST_Line_Locate_Point(a.geom,b.geom)) AS "Station"
	INTO mosty.lokalizacja2
		FROM mosty."StreamCenterlines" AS a, mosty.pkt2 AS b
        WHERE a."ReachCode" = b."ReachCode"
        ORDER BY "ReachCode", "Station" ;

"""Update of Inline_Structures layer by Stationing values"""
UPDATE mosty."Inline_Structures" AS a
SET "Station" = b."Station"
	FROM mosty.lokalizacja2 as b
    WHERE a."InlineStrID" = b."InlineStrID";
DROP TABLE mosty.pkt2, mosty.lokalizacja2;