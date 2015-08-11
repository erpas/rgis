--SELECT "RiverCode", ST_Accum(ST_StartPoint(geom)) ||  ST_Accum(ST_EndPoint(geom)) AS punkty_skrajne FROM "StreamCenterline" GROUP BY "RiverCode"
--DROP VIEW pnts2;
--DROP VIEW pnts1;

CREATE OR REPLACE VIEW pnts1 AS
SELECT "RiverCode", "ReachCode", ST_StartPoint(geom) AS geom, 'start' AS typ_punktu
FROM "StreamCenterline"
UNION ALL
SELECT "RiverCode", "ReachCode", ST_EndPoint(geom) AS geom, 'end' AS typ_punktu
FROM "StreamCenterline";

CREATE OR REPLACE VIEW pnts2 AS
SELECT "RiverCode", geom
FROM pnts1
GROUP BY "RiverCode", geom
HAVING COUNT(geom) = 1;

DROP TABLE IF EXISTS endpoints;
SELECT pnts1."RiverCode", pnts1."ReachCode", pnts1.geom::geometry(POINT, 2180) INTO endpoints
FROM pnts1, pnts2
WHERE pnts1."RiverCode" = pnts2."RiverCode" AND pnts1.geom = pnts2.geom AND pnts1.typ_punktu = 'end';

DROP VIEW pnts1 CASCADE;

SELECT * FROM "StreamCenterline"
WHERE "StreamCenterline"."ReachCode" = ANY((SELECT endpoints."ReachCode" FROM endpoints))