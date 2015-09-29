--DROP TABLE IF EXISTS "LeveesPoints";

--SELECT * INTO "LeveesPoints"
--FROM(
--SELECT ST_Intersection(lev.geom, xs.geom) AS geom, xs."XsecID", lev."LeveeID"
--FROM "Levees" as lev, "XSCutLines" AS xs) as lev2
--WHERE ST_AsText(lev2.geom)<>'GEOMETRYCOLLECTION EMPTY';

--SELECT
--"LeveesPoints"."XsecID",
--"LeveesPoints"."LeveeID",
--ST_LineLocatePoint("XSCutLines".geom, "LeveesPoints".geom)
--FROM "XSCutLines", "LeveesPoints"
--WHERE
--    "XSCutLines".geom && "LeveesPoints".geom;
--    ST_Intersects("XSCutLines".geom, ST_Buffer("LeveesPoints".geom,0.01));

--ALTER TABLE "LeveesPoints" ADD COLUMN "Elevation" real

------------------------------------------------------------------------------------------------------------------------
INSERT INTO "LeveesPoints"(geom, "LeveeID", "XsecID", "Fraction")
  SELECT
    ST_Intersection(lev.geom, xs.geom) AS geom,
    lev."LeveeID",
    xs."XsecID",
    ST_LineLocatePoint(xs.geom, ST_Intersection(lev.geom, xs.geom)) AS "Fraction"
  FROM
    "Levees" AS lev,
    "XSCutLines" AS xs
  WHERE
    xs.geom && lev.geom AND
    ST_Intersects(xs.geom, lev.geom);
------------------------------------------------------------------------------------------------------------------------
