------------------------------------------------------------------------------------------------------------------------
CREATE TABLE tmp1 AS
SELECT "RiverCode", "ReachCode", ST_StartPoint(geom) AS geom, 'start' AS typ_punktu
FROM "StreamCenterlines"
UNION ALL
SELECT "RiverCode", "ReachCode", ST_EndPoint(geom) AS geom, 'end' AS typ_punktu
FROM "StreamCenterlines";

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
------------------------------------------------------------------------------------------------------------------------
CREATE OR REPLACE FUNCTION from_to_stations ()
    RETURNS VOID AS
$BODY$
DECLARE
    c cursor FOR SELECT * FROM "Endpoints";
    r "Endpoints"%ROWTYPE;
    river text;
    tonode_id integer;
    fromnode_id integer;
    fromsta double precision;
    tosta double precision;
    len double precision;
BEGIN
FOR r IN c LOOP
    river := r."RiverCode";
    tonode_id := r."NodeID";
    fromsta := 0;
    tosta := 0;
    FOR i IN 1..(SELECT COUNT(*) FROM "StreamCenterlines" WHERE "StreamCenterlines"."RiverCode" = river) LOOP
        SELECT "FromNode", ST_Length(geom) INTO fromnode_id, len FROM "StreamCenterlines" WHERE "RiverCode" = river AND "ToNode" = tonode_id;
        tosta := fromsta + len;
        UPDATE "StreamCenterlines" SET
        "FromSta" = fromsta,
        "ToSta" = tosta
        WHERE "RiverCode" = river AND "ToNode" = tonode_id;
        tonode_id := fromnode_id;
        fromsta := tosta;
    END LOOP;
END LOOP;
END;
$BODY$
    LANGUAGE plpgsql;

------------------------------------------------------------------------------------------------------------------------
SELECT from_to_stations ();
DROP FUNCTION IF EXISTS from_to_stations ()
------------------------------------------------------------------------------------------------------------------------