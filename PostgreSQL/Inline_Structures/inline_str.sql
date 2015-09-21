-- RiverCode and RiverReach update from StreamCenterline layer
UPDATE "Dzierzgon"."Inline_Structures" AS a
SET "RiverCode" = b."RiverCode" , "ReachCode" = b."ReachCode"
	FROM "Dzierzgon"."StreamCenterlines" AS b
    WHERE  a.geom && b.geom AND ST_Intersects(a.geom,b.geom);

-- Generating of points needed for Inline_Structures Stationing calculation
DROP TABLE IF EXISTS "Dzierzgon".pointsinlinestr;
SELECT DISTINCT (ST_Dump(ST_Intersection(a.geom,b.geom))).geom AS geom,b."RiverCode", b."ReachCode", b."InlineStrID"
	INTO "Dzierzgon".pointsinlinestr
		FROM "Dzierzgon"."StreamCenterlines" AS a, "Dzierzgon"."Inline_Structures" as b
		WHERE a.geom && b.geom;

-- Calculation of Inline_Structures Stationing
DROP TABLE IF EXISTS "Dzierzgon".tempstatinlinestr;
SELECT b."InlineStrID", b."RiverCode",b."ReachCode", (a."ToSta" - a."FromSta")*(1-ST_Line_Locate_Point(a.geom,b.geom)) AS "Station"
	INTO "Dzierzgon".tempstatinlinestr
		FROM "Dzierzgon"."StreamCenterlines" AS a, "Dzierzgon".pointsinlinestr AS b
        WHERE a."ReachCode" = b."ReachCode"
        ORDER BY "ReachCode", "Station" ;

-- Update of Inline_Structures layer by Stationing values
UPDATE "Dzierzgon"."Inline_Structures" AS a
SET "Station" = b."Station"
	FROM "Dzierzgon".tempstatinlinestr as b
    WHERE a."InlineStrID" = b."InlineStrID";
DROP TABLE "Dzierzgon".pointsinlinestr, "Dzierzgon".tempstatinlinestr;