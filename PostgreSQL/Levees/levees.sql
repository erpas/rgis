-- DROP TABLE IF EXISTS "Levees";
-- 
-- CREATE TABLE "Levees"(
-- "LeveeID" serial PRIMARY KEY,
-- geom geometry(LINESTRING, 2180)
-- );

DROP TABLE IF EXISTS "LeveesPoints";

SELECT * INTO "LeveesPoints"
FROM(
SELECT ST_Intersection(lev.geom, xs.geom) AS geom, xs."XsecID", lev."LeveeID"
FROM "Levees" as lev, "XSCutLines" AS xs) as lev2
WHERE ST_AsText(lev2.geom)<>'GEOMETRYCOLLECTION EMPTY';

SELECT
"LeveesPoints"."XsecID",
"LeveesPoints"."LeveeID",
ST_LineLocatePoint("XSCutLines".geom, "LeveesPoints".geom)
FROM "XSCutLines", "LeveesPoints"
WHERE
    ST_Intersects("XSCutLines".geom, ST_Buffer("LeveesPoints".geom,0.01))