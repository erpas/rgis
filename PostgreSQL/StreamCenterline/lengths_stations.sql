--SELECT "RiverCode", ST_Accum(ST_StartPoint(geom)) ||  ST_Accum(ST_EndPoint(geom)) AS punkty_skrajne FROM "StreamCenterline" GROUP BY "RiverCode"
--DROP VIEW pnts2;
--DROP VIEW pnts1;

CREATE TABLE pnts1 AS
SELECT "RiverCode", "ReachCode", ST_StartPoint(geom) AS geom, 'start' AS typ_punktu
FROM "StreamCenterline"
UNION ALL
SELECT "RiverCode", "ReachCode", ST_EndPoint(geom) AS geom, 'end' AS typ_punktu
FROM "StreamCenterline";

CREATE TABLE pnts2 AS
SELECT "RiverCode", geom
FROM pnts1
GROUP BY "RiverCode", geom
HAVING COUNT(geom) = 1;

DROP TABLE IF EXISTS "Endpoints";
SELECT pnts1.geom::geometry(POINT, 2180), pnts1."RiverCode", pnts1."ReachCode", "NodesTable"."NodeID" INTO "Endpoints"
FROM pnts1, pnts2, "NodesTable"
WHERE pnts1."RiverCode" = pnts2."RiverCode" AND pnts1.geom = pnts2.geom AND pnts1.typ_punktu = 'end' AND pnts1.geom = "NodesTable".geom;

DROP TABLE pnts1;
DROP TABLE pnts2;