-- RiverCode and RiverReach update from StreamCenterline layer
UPDATE "Dzierzgon"."Bridges" AS a
SET
    "RiverCode" = b."RiverCode",
    "ReachCode" = b."ReachCode"
FROM
    "Dzierzgon"."StreamCenterlines" AS b
WHERE
    a.geom && b.geom AND
    ST_Intersects(a.geom, b.geom);

-- Generating of points needed for bridges Stationing calculation
DROP TABLE IF EXISTS "Dzierzgon".pointsbridges;
SELECT DISTINCT
    (ST_Dump(ST_Intersection(a.geom,b.geom))).geom AS geom,
    b."RiverCode",
    b."ReachCode",
    b."BridgeID"
INTO
    "Dzierzgon".pointsbridges
FROM
    "Dzierzgon"."StreamCenterlines" AS a,
    "Dzierzgon"."Bridges" AS b
WHERE
    a.geom && b.geom AND
    ST_Intersects(a.geom, b.geom);

-- Calculation of bridges Stationing
DROP TABLE IF EXISTS "Dzierzgon".tempstatbridges;
SELECT
    b."BridgeID",
    b."RiverCode",
    b."ReachCode",
    (a."ToSta" - a."FromSta")*(1-ST_Line_Locate_Point(a.geom, b.geom)) AS "Station"
INTO
    "Dzierzgon".tempstatbridges
FROM
    "Dzierzgon"."StreamCenterlines" AS a,
    "Dzierzgon".pointsbridges AS b
WHERE
    a."ReachCode" = b."ReachCode"
ORDER BY
    "ReachCode",
    "Station";

-- Update of Bridges layer by Stationing values
UPDATE "Dzierzgon"."Bridges" AS a
SET
    "Station" = b."Station"
FROM
    "Dzierzgon".tempstatbridges as b
WHERE
    a."BridgeID" = b."BridgeID";

DROP TABLE
    "Dzierzgon".pointsbridges,
    "Dzierzgon".tempstatbridges;
