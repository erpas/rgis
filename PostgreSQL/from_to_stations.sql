CREATE OR REPLACE FUNCTION from_to_stations ()
    RETURNS VOID AS
$BODY$
DECLARE
    c cursor FOR SELECT * FROM "Endpoints";
    r "Endpoints"%ROWTYPE;
    river text;
    tonode_id integer;
    fromnode_id integer;
    length double precision;
    fromsta double precision;
    tosta double precision;
BEGIN
FOR r in c LOOP
    river := r."RiverCode";
    tonode_id := r."NodeID";
    fromsta := 0;
    tosta := 0;
    FOR i in 1..(SELECT COUNT(*) FROM "StreamCenterlines" WHERE "StreamCenterlines"."RiverCode" = river) LOOP
        SELECT "FromNode", ST_Length(geom) INTO fromnode_id, length FROM "StreamCenterlines" WHERE "RiverCode" = river AND "ToNode" = tonode_id;
        tosta := fromsta + length;
        UPDATE "StreamCenterlines" SET
        "FromSta" = fromsta,
        "ToSta" = tosta
        WHERE "RiverCode" = river AND "ToNode" = tonode_id;
        tonode_id = fromnode_id;
        fromsta := tosta;
    END LOOP;
END LOOP;
END;
$BODY$
    LANGUAGE plpgsql;

SELECT from_to_stations ();
DROP FUNCTION IF EXISTS from_to_stations ()