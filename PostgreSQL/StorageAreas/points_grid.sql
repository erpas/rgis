CREATE OR REPLACE FUNCTION "Pasleka".points_grid ()
    RETURNS VOID AS
$BODY$
DECLARE
    c cursor FOR SELECT * FROM "Pasleka"."StorageAreas";
    r "Pasleka"."StorageAreas"%ROWTYPE;
    x double precision;
    y double precision;
    pnt geometry;
    inside boolean;
    said integer;
    row_nr integer;
    col_nr integer;
    step double precision := 10;
    min_x double precision;
    max_x double precision;
    min_y double precision;
    max_y double precision;
BEGIN
    FOR r IN c LOOP
        min_x := ST_Xmin(ST_Extent(r.geom));
        max_x := ST_Xmax(ST_Extent(r.geom));
        min_y := ST_Ymin(ST_Extent(r.geom));
        max_y := ST_Ymax(ST_Extent(r.geom));
        row_nr := ceiling((max_x - min_x) / step);
        col_nr := ceiling((max_y - min_y) / step);
        x := min_x;
        FOR i IN 1..row_nr LOOP
            y := min_y;
            FOR j IN 1..col_nr LOOP
                pnt := (ST_SetSRID(ST_Point(x, y), 2180));
                SELECT ST_Within(pnt, r.geom), r."StorageID" INTO inside, said WHERE ST_Within(pnt, r.geom) IS True;
                IF inside IS True THEN
                    INSERT INTO "Pasleka"."SASurface"(geom, "StorageID")
                    VALUES (pnt, said);
                END IF;
                y := y + step;
            END LOOP;
            x := x + step;
        END LOOP;
    END LOOP;
END;
$BODY$
    LANGUAGE plpgsql;


DROP TABLE IF EXISTS "Pasleka"."SASurface";
CREATE TABLE "Pasleka"."SASurface"(geom geometry(POINT, 2180), "StorageID" integer, "Elevation" double precision);
SELECT "Pasleka".points_grid ();
ALTER TABLE "Pasleka"."SASurface" ADD COLUMN "PtID" bigserial primary key;
