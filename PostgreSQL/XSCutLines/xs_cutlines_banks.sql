CREATE TABLE xs_banks_points AS
SELECT*
FROM
	(SELECT
	tazyna_xscutlines."HydroID",
	ST_Intersection(tazyna_xscutlines.geom,tazyna_banks.geom) AS geom 
	FROM public.tazyna_xscutlines, public.tazyna_banks) AS wynik
WHERE geom <> '01070000208408000000000000';

CREATE TABLE xs_banks_points2 AS
SELECT*
FROM
	(SELECT tazyna_xscutlines."HydroID" AS "HydroID",
	xs_banks_points."HydroID" AS id,
	ST_LineLocatePoint(tazyna_xscutlines.geom, xs_banks_points.geom) AS banks
	FROM tazyna_xscutlines, xs_banks_points) AS test
WHERE banks<1 AND banks>0;

CREATE TABLE brzegi(
banks_hydroid integer,
banks real);

INSERT INTO brzegi (banks_hydroid, banks)
SELECT
"HydroID",
banks
FROM xs_banks_points2
WHERE xs_banks_points2."HydroID" = xs_banks_points2.id
ORDER BY "HydroID";

SELECT* INTO xs_cutlines_brzegi
FROM brzegi AS b INNER JOIN tazyna_xscutlines AS xs ON b.banks_hydroid = xs."HydroID";

SELECT
banks_hydroid,
array_agg(banks) AS tablica_brzegow
INTO banks_tmp
FROM xs_cutlines_brzegi
GROUP BY banks_hydroid;

CREATE OR REPLACE VIEW tmp AS 
SELECT
banks_hydroid,
tablica_brzegow,
CASE WHEN tablica_brzegow[1]<tablica_brzegow[2] THEN tablica_brzegow[1]
ELSE tablica_brzegow[2]
END AS "LeftBank",
CASE WHEN tablica_brzegow[1]>tablica_brzegow[2] THEN tablica_brzegow[1]
ELSE tablica_brzegow[2]
END AS "RightBank"
FROM banks_tmp;

UPDATE tazyna_xscutlines
SET "LeftBank" = tmp."LeftBank",
    "RightBank" = tmp."RightBank"
FROM tmp
WHERE "HydroID" = banks_hydroid;

DROP TABLE xs_banks_points, xs_banks_points2, brzegi, xs_cutlines_brzegi;

DROP TABLE banks_tmp CASCADE;