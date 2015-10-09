CREATE OR REPLACE FUNCTION "Pasleka".points_grid ()
    RETURNS VOID AS
$BODY$
DECLARE
    x double precision;
    y double precision;
    pnt geometry;
    inside boolean;
    said integer;
    rows integer;
    cols integer;
    step double precision := 3;
    min_x double precision := (SELECT ST_Xmin(ST_Extent(geom)) FROM "Pasleka"."StorageAreas");
    max_x double precision := (SELECT ST_Xmax(ST_Extent(geom)) FROM "Pasleka"."StorageAreas");
    min_y double precision := (SELECT ST_Ymin(ST_Extent(geom)) FROM "Pasleka"."StorageAreas");
    max_y double precision := (SELECT ST_Ymax(ST_Extent(geom)) FROM "Pasleka"."StorageAreas");
BEGIN
    rows := ceiling((max_x - min_x) / step);
    cols := ceiling((max_y - min_y) / step);
    x := min_x;
    FOR i IN 1..rows LOOP
        y := min_y;
        FOR j in 1..cols LOOP
            pnt := (ST_SetSRID(ST_Point(x, y), 2180));
	    SELECT ST_Within(pnt, geom), "StorageID" INTO inside, said FROM "Pasleka"."StorageAreas" WHERE ST_Within(pnt, geom) IS True;
            IF inside is True THEN
		INSERT INTO "Pasleka"."SASurface"(geom, "StorageID")
		VALUES (pnt, said);
	    END IF;
            y := y + step;
        END LOOP;
        x := x + step;
    END LOOP;
END;
$BODY$
    LANGUAGE plpgsql;


DROP TABLE IF EXISTS "Pasleka"."SASurface";
CREATE TABLE "Pasleka"."SASurface"(geom geometry(POINT, 2180), id bigserial primary key, "StorageID" integer, "Elevation" double precision);
SELECT "Pasleka".points_grid ();
