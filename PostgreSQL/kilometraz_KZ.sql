------------------------------------------------------------------------------------------------------------------------
#Tworzenie linii M - Create LINESTRINGM

CREATE TABLE karolz.streamcenterline_m(
	id serial PRIMARY KEY,
	RiverCode VARCHAR(16),
	ReachCode VARCHAR(16),
	dlugosc real,
	geom geometry(LINESTRINGM,2180));
INSERT INTO karolz.streamcenterline_m(RiverCode, ReachCode, dlugosc, geom)
SELECT RiverCode, ReachCode, ST_AddMeasure(drogi.geom, 0.0, (SELECT ST_Length(drogi.geom))), ST_Length(streamcenterline_m.geom)::real AS dlugosc
FROM karolz.drogi
------------------------------------------------------------------------------------------------------------------------
#Tworzenie miejsc przeciêcia linii cieków i przekrojów

CREATE TABLE karolz.punkty_int(
id serial PRIMARY KEY,
geom geometry(POINT),
RiverCode VARCHAR (16),
ReachCode VARCHAR(16)
);
INSERT INTO karolz.punkty_int(geom, RiverCode, ReachCode)
SELECT
tab.geom,
tab.RiverCode,
tab.ReachCode
FROM
	(SELECT ST_AsText(ST_Intersection(streamcenterline_m.geom, crosssections.geom)) as geom, RiverCode, ReachCode
		FROM karolz.streamcenterline_m, karolz.crosssections) AS tab
WHERE geom <> 'GEOMETRYCOLLECTION EMPTY';
ALTER TABLE karolz.punkty_int 
  ALTER COLUMN geom TYPE geometry(POINT, 2180) 
    USING ST_SetSRID(geom,2180);
------------------------------------------------------------------------------------------------------------------------
#Nadawanie kilometra¿u 
CREATE TABLE karolz.punkty_km(
id serial PRIMARY KEY,
nazwa VARCHAR,
geom geometry(POINT),
test VARCHAR,
km REAL
);
INSERT INTO karolz.punkty_km(nazwa, geom,test,km)
SELECT*
FROM
(SELECT
drogi_m.nazwa,
punkty_int.geom,
ST_Intersects(ST_Buffer(drogi_m.geom,0.01),punkty_int.geom) AS test,
ST_InterpolatePoint(drogi_m.geom,punkty_int.geom) AS km
FROM karolz.drogi_m, karolz.punkty_int) AS tabela
WHERE test<>'False
------------------------------------------------------------------------------------------------------------------------