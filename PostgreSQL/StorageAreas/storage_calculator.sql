CREATE OR REPLACE FUNCTION "Pasleka".storage_calculator ()
    RETURNS VOID AS
$BODY$
DECLARE
    lev double precision := 0;
    area double precision := 9;
    emax double precision := (SELECT MAX("Elevation") FROM "Pasleka".sa_points);
    emin double precision := (SELECT MIN("Elevation") FROM "Pasleka".sa_points);
    division integer := 5;
    h double precision := (emax - emin) / division;
BEGIN
    FOR i IN 1..division LOOP
        INSERT INTO "Pasleka".levels (start_level, end_level, volume)
        SELECT lev, lev + h, SUM("Elevation")*h FROM "Pasleka".sa_points WHERE "Elevation" BETWEEN lev AND lev + h;
        lev := lev + h;
    END LOOP;
END;
$BODY$
    LANGUAGE plpgsql;

DROP TABLE IF EXISTS "Pasleka".levels;
CREATE TABLE "Pasleka".levels(start_level double precision, end_level double precision, volume double precision);
SELECT "Pasleka".storage_calculator ();