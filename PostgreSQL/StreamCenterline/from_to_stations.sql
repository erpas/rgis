CREATE OR REPLACE FUNCTION from_to_stations ()
    RETURNS VOID AS
$BODY$
DECLARE
    c cursor FOR SELECT * FROM "Endpoints"
    r "Endpoints"%ROWTYPE;
    rec revord;
    river text;
    fromsta double precision := 0;
    tosta double precision :=0;
BEGIN
FOR r in c LOOP
    river := r."RiverCode";
    tosta := ST_Length(r.geom);
    FOR i in 1... COUNT(SELECT * FROM "SreamCenterLines" WHERE "StreamCenterlines"."ReachCode" = river) LOOP
    
    UPDATE "StreamCenterlines" SET
    "FromSta" = fromsta,
    "ToSta" = tosta
    WHERE CURRENT OF c;
END LOOP;
END;
$BODY$
    LANGUAGE plpgsql;

SELECT from_to_stations ()