CREATE OR REPLACE FUNCTION "Pasleka".points_grid ()
    RETURNS VOID AS
$BODY$
DECLARE
    x double precision;
    y double precision;
    rows integer;
    cols integer;
    step double precision := 10;
    min_x double precision := (SELECT ST_Xmin(geom) FROM "Pasleka"."StorageAreas");
    max_x double precision := (SELECT ST_Xmax(geom) FROM "Pasleka"."StorageAreas");
    min_y double precision := (SELECT ST_Ymin(geom) FROM "Pasleka"."StorageAreas");
    max_y double precision := (SELECT ST_Ymax(geom) FROM "Pasleka"."StorageAreas");
BEGIN
    rows := ceiling((max_x - min_x) / step);
    cols := ceiling((max_y - min_y) / step);
    x := min_x;
    FOR i IN 1..rows LOOP
        y := min_y;
        FOR j in 1..cols LOOP
            INSERT INTO "Pasleka"."SASurface"(geom) VALUES (ST_SetSRID(ST_Point(x, y), 2180));
            y := y + step;
        END LOOP;
        x := x + step;
    END LOOP;
END;
$BODY$
    LANGUAGE plpgsql;

DROP TABLE IF EXISTS "Pasleka"."SASurface";
CREATE TABLE "Pasleka"."SASurface"(geom geometry(POINT, 2180), id bigserial primary key);
SELECT "Pasleka".points_grid ();