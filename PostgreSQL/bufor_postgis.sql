##################################################
CREATE TABLE test.bufor33 AS 
    SELECT ST_Buffer(geom, 33) AS geom
    FROM test.streamcenterline

##################################################

CREATE TABLE test.bufor(opis varchar(32));
SELECT AddGeometryColumn('test', 'bufor', 'geom', -1, 'POLYGON', 2);
INSERT INTO test.bufor (opis, geom)
    VALUES ('niezle bufory ;-)',  (SELECT ST_Buffer(test.streamcenterline.geom, 10) FROM test.streamcenterline))

##################################################
Layer is not valid: The layer dbname='CMPiS_Gdynia' host=pzrpgeosrv.imgw.ad port=5432 user='ldebek' sslmode=disable srid=4326 type=POLYGON table="test"."bufor" (geom) sql= is not a valid layer and can not be added to the map
##################################################
setlocal
SET PGPORT=5432
SET PGHOST=pzrpgeosrv.imgw.ad
SET PGUSER=ldebek


raster2pgsql -s 2180 -I -C  D:\OBROBKA_WYNIKOW\Pasleka_MORZE\Pasleka_Morze_bez_falowania\nmt\nmt_N-34-52-C-d-4-2.tif -F -t 128x128 public.nmt_pasleka | psql -d CMPiS_Gdynia

##################################################
CREATE TABLE hecras_projekty.bufor(
    id serial PRIMARY KEY,
    opis varchar(32),
    geom geometry(POLYGON, 2180)
    );
INSERT INTO hecras_projekty.bufor (opis, geom)
VALUES
	('niezle bufory!',  (SELECT ST_Buffer(hecras_projekty.przeszkoda.geom, 100) FROM hecras_projekty.przeszkoda))

##################################################
CREATE TABLE hecras_projekty.bufor_union(
    id serial PRIMARY KEY,
    opis varchar(32),
    geom geometry(POLYGON, 2180)
    );
INSERT INTO hecras_projekty.bufor_union (geom)
VALUES
	((SELECT ST_Union(ST_Buffer(hecras_projekty.przeszkody.geom, 100)) FROM hecras_projekty.przeszkody))

##################################################
CREATE TABLE hecras_projekty.bufory(
    id serial PRIMARY KEY,
    opis varchar(32),
    geom geometry(POLYGON, 2180)
    );
INSERT INTO hecras_projekty.bufory (geom)
SELECT ST_Buffer(hecras_projekty.przeszkody.geom, 100) FROM hecras_projekty.przeszkody

##################################################
ogr2ogr.exe -progress --config PG_USE_COPY YES -f PostgreSQL PG:"host=pzrpgeosrv.imgw.ad port=5432 dbname=CMPiS_Gdynia user=ldebek" -lco DIM=2 X:/TEMP/LD/TEST_POSTGIS/Wezel_Gdanski_W0/Wezel_Gdanski_W0_500_ZASIEG.shp Wezel_Gdanski_W0_500_ZASIEG -overwrite -nlt MULTIPOLYGON -lco SCHEMA=public -lco GEOMETRY_NAME=geom -lco FID=id -a_srs EPSG:2180 -spat 474238.9846 708415.288 482373.07 721558.21 -nlt PROMOTE_TO_MULTI
