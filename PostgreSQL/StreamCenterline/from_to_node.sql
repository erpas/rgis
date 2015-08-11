CREATE OR REPLACE FUNCTION from_to_node ()
    RETURNS VOID AS
$BODY$
DECLARE
    c cursor FOR SELECT * FROM "StreamCenterline";
    r "StreamCenterline"%ROWTYPE;
    start_geom geometry;
    end_geom geometry;
    start_node integer := 0;
    end_node integer := 0;
    nr integer := 0;
BEGIN
DROP TABLE IF EXISTS "NodesTable";
CREATE TABLE "NodesTable"(
    geom geometry(POINT, 2180),
    "NodeID" integer,
    "X" real,
    "Y" real);
FOR r in c LOOP
    start_geom := ST_StartPoint(r.geom);
    end_geom := ST_EndPoint(r.geom);
    IF (SELECT exists (SELECT 1 FROM "NodesTable" WHERE geom = start_geom LIMIT 1)) THEN
        start_node := (SELECT "NodeID" FROM "NodesTable" WHERE geom = start_geom LIMIT 1);
    ELSE
        nr := nr + 1;
        start_node := nr;
        INSERT INTO "NodesTable" VALUES (start_geom, nr, ST_X(start_geom), ST_Y(start_geom));
    END IF;
    IF (SELECT exists (SELECT 1 FROM "NodesTable" WHERE geom = end_geom LIMIT 1)) THEN
        end_node := (SELECT "NodeID" FROM "NodesTable" WHERE geom = end_geom LIMIT 1);
    ELSE
        nr := nr + 1;
        end_node := nr;
        INSERT INTO "NodesTable" VALUES (end_geom, nr, ST_X(end_geom), ST_Y(end_geom));
    END IF;
    UPDATE "StreamCenterline" SET
    "FromNode" = start_node,
    "ToNode" = end_node
    WHERE CURRENT OF c;
END LOOP;
END;
$BODY$
    LANGUAGE plpgsql;

SELECT from_to_node ()