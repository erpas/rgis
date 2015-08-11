CREATE TABLE tazyna_xscutlines2(
hydroid integer,
profilem real,
rivercode text,
reachcode text,
leftbank real,
rightbank real,
llength real,
chlength real,
rlength real,
geom geometry (LINESTRING,2180)
);

INSERT INTO tazyna_xscutlines2(hydroid, profilem, rivercode, reachcode, leftbank, rightbank, llength, chlength, rlength, geom)
SELECT
wynik.hydroid,
wynik.profilem,
wynik.rivercode,
wynik.reachcode,
wynik.leftbank,
wynik.rightbank,
wynik.llength,
wynik.chlength,
wynik.rlength,
wynik.geom
FROM
	(SELECT
	tazyna_xscutlines."HydroID" AS hydroid,
	tazyna_xscutlines."ProfileM" AS profilem,
	tazyna_river."RiverCode" AS rivercode,
	tazyna_river."ReachCode" AS reachcode,
	tazyna_xscutlines."LeftBank" AS leftbank,
	tazyna_xscutlines."RightBank" AS rightbank,
	tazyna_xscutlines."LLength" AS llength,
	tazyna_xscutlines."ChLength" AS chlength,
	tazyna_xscutlines."RLength" AS rlength,
	tazyna_xscutlines.geom AS geom,
	ST_AsText(ST_Intersection(tazyna_xscutlines.geom,tazyna_river.geom)) AS p_geom
	FROM tazyna_xscutlines, tazyna_river) as wynik
	WHERE p_geom <> 'GEOMETRYCOLLECTION EMPTY'
;

UPDATE tazyna_xscutlines
SET "RiverCode"=tazyna_xscutlines2.rivercode,
    "ReachCode"=tazyna_xscutlines2.reachcode
FROM tazyna_xscutlines2
WHERE "HydroID" = tazyna_xscutlines2.hydroid
;

DROP TABLE tazyna_xscutlines2;



