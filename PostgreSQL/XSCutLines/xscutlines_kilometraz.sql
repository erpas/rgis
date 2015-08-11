----Laczenie linii ciekow do liczenia kilometrazu----
CREATE TABLE river(
"RiverCode" text,
geom geometry(LINESTRING)
);
INSERT INTO river("RiverCode", geom)
SELECT "RiverCode",ST_LineMerge(ST_Collect(tazyna_river.geom)) AS geom
FROM tazyna_river
GROUP BY "RiverCode"
;

ALTER TABLE river
  ALTER COLUMN geom TYPE geometry(LINESTRING, 2180) 
    USING ST_SetSRID(geom,2180)
;

----Tworzenie linii M----
CREATE TABLE tazyna_river_m(
"RiverCode" text,
geom geometry(LINESTRINGM,2180)
);

INSERT INTO tazyna_river_m("RiverCode", geom)
SELECT
"RiverCode" AS "RiverCode",
ST_AddMeasure(ST_Reverse(river.geom), 0.0, (SELECT ST_Length(river.geom))) AS geom
FROM public.river
;
----Tworzenie punktow przeciecia przebiegu rzeki oraz przekrojow----
CREATE TABLE tazyna_punkty_int(
"HydroID" integer,
geom geometry(POINT)
);

INSERT INTO tazyna_punkty_int("HydroID", geom)
SELECT
tab."HydroID",
tab.geom
FROM
	(SELECT ST_AsText(ST_Intersection(tazyna_river_m.geom, tazyna_xscutlines.geom)) as geom, tazyna_xscutlines."HydroID"
		FROM public.tazyna_river_m, public.tazyna_xscutlines) AS tab
WHERE geom <> 'GEOMETRYCOLLECTION EMPTY'
;
ALTER TABLE tazyna_punkty_int 
  ALTER COLUMN geom TYPE geometry(POINT, 2180) 
    USING ST_SetSRID(geom,2180)
;

----Nadanie kilometrazu punktom przeciecia----

CREATE TABLE public.tazyna_punkty_km(
"HydroID" integer,
km real,
test VARCHAR,
geom geometry(POINT)
);
INSERT INTO public.tazyna_punkty_km("HydroID", km, test, geom)
SELECT*
FROM
(SELECT
tazyna_punkty_int."HydroID" AS "HydroID",
ST_InterpolatePoint(tazyna_river_m.geom,tazyna_punkty_int.geom) AS km,
ST_Intersects(ST_Buffer(tazyna_river_m.geom,0.01),tazyna_punkty_int.geom) AS test,
tazyna_punkty_int.geom AS geom
FROM public.tazyna_punkty_int, public.tazyna_river_m) AS tabela
WHERE test<>False
;
ALTER TABLE tazyna_punkty_km 
  ALTER COLUMN geom TYPE geometry(POINT, 2180) 
    USING ST_SetSRID(geom,2180)
;

----Akutalizacja tabeli----
UPDATE tazyna_xscutlines
SET "ProfileM"= round(tazyna_punkty_km.km::numeric,2)
FROM tazyna_punkty_km
WHERE tazyna_xscutlines."HydroID" = tazyna_punkty_km."HydroID"
;

----Kasowanie tabel----
DROP TABLE tazyna_punkty_int, tazyna_punkty_km, tazyna_river_m, river