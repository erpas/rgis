CREATE OR REPLACE FUNCTION makegrid(geometry, integer)
RETURNS geometry AS
    'SELECT 
        ST_Collect(ST_SetSRID(ST_POINT(x, y), ST_SRID($1)))
    FROM 
        generate_series(floor(ST_Xmin($1))::int, ceiling(ST_Xmax($1))::int, $2) as x,
        generate_series(floor(ST_Ymin($1))::int, ceiling(ST_Ymax($1))::int, $2) as y
    WHERE
        ST_Intersects($1, ST_SetSRID(ST_POINT(x, y), ST_SRID($1)))'
LANGUAGE sql;

DROP TABLE IF EXISTS "Pasleka"."SASurface";
SELECT (ST_Dump(makegrid(geom, 1))).geom::geometry(POINT, 2180) AS geom
INTO "Pasleka"."SASurface"
FROM "Pasleka"."StorageAreas";
ALTER TABLE "Pasleka"."SASurface" ADD COLUMN id SERIAL PRIMARY KEY;