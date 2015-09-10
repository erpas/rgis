--SELECT "RiverCode", ST_Accum(ST_StartPoint(geom)) ||  ST_Accum(ST_EndPoint(geom)) AS punkty_skrajne FROM "StreamCenterline" GROUP BY "RiverCode"
--DROP VIEW tmp2;
--DROP VIEW tmp1;

CREATE TABLE tmp1 AS
SELECT "RiverCode", "ReachCode", ST_StartPoint(geom) AS geom, 'start' AS typ_punktu
FROM "StreamCenterline"
UNION ALL
SELECT "RiverCode", "ReachCode", ST_EndPoint(geom) AS geom, 'end' AS typ_punktu
FROM "StreamCenterline";

CREATE TABLE tmp2 AS
SELECT "RiverCode", geom
FROM tmp1
GROUP BY "RiverCode", geom
HAVING COUNT(geom) = 1;

DROP TABLE IF EXISTS "Endpoints";
SELECT tmp1.geom::geometry(POINT, 2180), tmp1."RiverCode", tmp1."ReachCode", "NodesTable"."NodeID" INTO "Endpoints"
FROM tmp1, tmp2, "NodesTable"
WHERE tmp1."RiverCode" = tmp2."RiverCode" AND tmp1.geom = tmp2.geom AND tmp1.typ_punktu = 'end' AND tmp1.geom = "NodesTable".geom;

DROP TABLE tmp1;
DROP TABLE tmp2;