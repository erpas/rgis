CREATE OR REPLACE FUNCTION "Pasleka".storage_calculator (slices integer)
    RETURNS VOID AS
$BODY$
DECLARE
    c cursor FOR SELECT * FROM "Pasleka"."StorageAreas";
    r "Pasleka"."StorageAreas"%ROWTYPE;
    area double precision;
    emin double precision;
    emax double precision;
    lev double precision;
    h double precision;
BEGIN
    FOR r IN c LOOP
        area := (SELECT dtm."CellSize" FROM "Pasleka"."DTMs" AS dtm WHERE dtm."DtmID" = r."DtmID")^2;
        emin := (SELECT MIN("Elevation") FROM "Pasleka"."SASurface" WHERE "StorageID" = r."StorageID");
        emax := (SELECT MAX("Elevation") FROM "Pasleka"."SASurface" WHERE "StorageID" = r."StorageID");
        lev := emin;
        h := (emax-emin)/slices;
        FOR i IN 1..slices LOOP
            INSERT INTO "Pasleka"."SAVolume" ("StorageID", start_level, end_level, volume)
            SELECT r."StorageID", lev, lev+h, COUNT("Elevation")*area*h FROM "Pasleka"."SASurface" WHERE "StorageID" = r."StorageID" AND "Elevation" BETWEEN lev AND lev+h;
            lev := lev+h;
        END LOOP;
    END LOOP;
END;
$BODY$
    LANGUAGE plpgsql;


DROP TABLE IF EXISTS "Pasleka"."SAVolume";
CREATE TABLE "Pasleka"."SAVolume"("StorageID" integer, start_level double precision, end_level double precision, volume double precision);
SELECT "Pasleka".storage_calculator (5);
