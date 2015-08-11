DROP VIEW IF EXISTS tmp;

CREATE VIEW tmp AS
SELECT 
geom,
banks_hydroid,
array_agg(banks) AS banki
FROM xs_cutlines_brzegi
GROUP BY geom, banks_hydroid;

SELECT
geom,
banks_hydroid,
banki,
CASE WHEN banki[1] < banki[2] THEN banki[1]
ELSE banki[2]
END AS "LeftBank",
CASE WHEN banki[1] > banki[2] THEN banki[1]
ELSE banki[2]
END AS "RightBank"
FROM tmp;