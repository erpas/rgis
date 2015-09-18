
------------------------------------------------------------------------------------------------
-- Intersect of landuse layer with cross section layer  --
------------------------------------------------------------------------------------------------

SELECT "LUID", "LUCode", "N_Value",ST_AsText((ST_Dump(geom)).geom) AS geom INTO "Dzierzgon".uzytkowanie5
FROM  "Dzierzgon"."LanduseAreas";

ALTER TABLE "Dzierzgon".uzytkowanie5
	ALTER COLUMN geom TYPE geometry(POLYGON,2180)
	USING ST_SetSRID(geom,2180);
CREATE INDEX idx_uzytkowanie5
 	ON "Dzierzgon".uzytkowanie5
 	 	USING gist(geom);


SELECT "XSCutLines"."XsecID", uzytkowanie5."N_Value", uzytkowanie5."LUCode", ST_Intersection(uzytkowanie5.geom, "XSCutLines".geom) AS geom INTO "Dzierzgon".przekpkt
	FROM "Dzierzgon".uzytkowanie5, "Dzierzgon"."XSCutLines" 
		WHERE uzytkowanie5.geom && "XSCutLines".geom AND ST_Intersects(uzytkowanie5.geom, "XSCutLines".geom) ORDER BY "XSCutLines"."XsecID";

SELECT "XsecID","N_Value","LUCode" ,ST_AsText((ST_Dump(geom)).geom) AS geom INTO "Dzierzgon".przekpkt2 
	FROM "Dzierzgon".przekpkt;


ALTER TABLE "Dzierzgon".przekpkt2
	ALTER COLUMN geom TYPE geometry(LINESTRING,2180)
	USING ST_SetSRID(geom,2180);
CREATE INDEX idx_przekpkt2
 	ON "Dzierzgon".przekpkt2
 	 	USING gist(geom);


------------------------------------------------------------------------------------------------
-- Multilinestring to line string --
------------------------------------------------------------------------------------------------

SELECT "XsecID", ST_AsText((ST_Dump("XSCutLines".geom)).geom) AS geom INTO "Dzierzgon".single_line
	FROM "Dzierzgon"."XSCutLines" ORDER BY "XsecID";

ALTER TABLE "Dzierzgon".single_line
 	ALTER COLUMN geom TYPE geometry(LINESTRING,2180)
  	USING ST_SetSRID(geom,2180);

CREATE INDEX idx_single_line
 	ON "Dzierzgon".single_line
 	 	USING gist(geom);

----------------------------------------------------------------------------------------------------------
-- Creation of points on the line start points, 5 mm shifting for appropriate "N_Value" application    --
----------------------------------------------------------------------------------------------------------

SELECT "XsecID", "N_Value", "LUCode", ST_Line_Interpolate_Point(przekpkt2.geom,0.00005) as geom INTO "Dzierzgon".lininp
	FROM "Dzierzgon".przekpkt2 ORDER BY "XsecID";

ALTER TABLE "Dzierzgon".lininp
	ALTER COLUMN geom TYPE geometry(POINT,2180)
	USING ST_SetSRID(geom,2180);

CREATE INDEX idx_lininp
 	ON "Dzierzgon".lininp
 	 	USING gist(geom);

------------------------------------------------------------------------------------------------
-- Calculation of fraction along line cross sections  --
------------------------------------------------------------------------------------------------

SELECT  b."XsecID", b."N_Value", b."LUCode", ST_LineLocatePoint(a.geom,b.geom) AS "Fraction" INTO "Dzierzgon".tempmann
	FROM "Dzierzgon".single_line AS a, "Dzierzgon".lininp AS b
		WHERE a."XsecID" = b."XsecID" ORDER BY "XsecID", "Fraction";

------------------------------------------------------------------------------------------------
-- Creation of table with Manning's coeficients  --
------------------------------------------------------------------------------------------------

SELECT "XsecID", CASE WHEN "Fraction" < 0.0001 THEN "Fraction" * 0 ELSE "Fraction" END AS "Fraction", "N_Value", "LUCode" INTO "Dzierzgon"."Manning"
FROM "Dzierzgon".tempmann;

DROP TABLE "Dzierzgon".przekpkt,"Dzierzgon".przekpkt2, "Dzierzgon".single_line, "Dzierzgon".lininp,"Dzierzgon".tempmann,"Dzierzgon".uzytkowanie5
