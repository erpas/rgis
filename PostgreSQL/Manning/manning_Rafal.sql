
------------------------------------------------------------------------------------------------
-- Intersect of land use layer with cross section layer  --
------------------------------------------------------------------------------------------------

SELECT "LUID", "LUCode", "N_Value",ST_AsText((ST_Dump(geom)).geom) AS geom INTO "Dzierzgon".ludump
FROM  "Dzierzgon"."LanduseAreas";

ALTER TABLE "Dzierzgon".ludump
	ALTER COLUMN geom TYPE geometry(POLYGON,2180)
	USING ST_SetSRID(geom,2180);
CREATE INDEX idx_ludump
 	ON "Dzierzgon".ludump
 	 	USING gist(geom);


SELECT "XSCutLines"."XsecID", ludump."N_Value", ludump."LUCode", ST_Intersection(ludump.geom, "XSCutLines".geom) AS geom INTO "Dzierzgon".intercrossection
	FROM "Dzierzgon".ludump, "Dzierzgon"."XSCutLines" 
		WHERE ludump.geom && "XSCutLines".geom AND ST_Intersects(ludump.geom, "XSCutLines".geom) ORDER BY "XSCutLines"."XsecID";

SELECT "XsecID","N_Value","LUCode" ,ST_AsText((ST_Dump(geom)).geom) AS geom INTO "Dzierzgon".intercrossectiondump 
	FROM "Dzierzgon".intercrossection;


ALTER TABLE "Dzierzgon".intercrossectiondump
	ALTER COLUMN geom TYPE geometry(LINESTRING,2180)
	USING ST_SetSRID(geom,2180);
CREATE INDEX idx_intercrossectiondump
 	ON "Dzierzgon".intercrossectiondump
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

SELECT "XsecID", "N_Value", "LUCode", ST_Line_Interpolate_Point(intercrossectiondump.geom,0.00005) as geom INTO "Dzierzgon".shiftpoints
	FROM "Dzierzgon".intercrossectiondump ORDER BY "XsecID";

ALTER TABLE "Dzierzgon".shiftpoints
	ALTER COLUMN geom TYPE geometry(POINT,2180)
	USING ST_SetSRID(geom,2180);

CREATE INDEX idx_shiftpoints
 	ON "Dzierzgon".shiftpoints
 	 	USING gist(geom);

------------------------------------------------------------------------------------------------
-- Calculation of fraction along line cross sections  --
------------------------------------------------------------------------------------------------

SELECT  b."XsecID", b."N_Value", b."LUCode", ST_LineLocatePoint(a.geom,b.geom) AS "Fraction" INTO "Dzierzgon".tempmann
	FROM "Dzierzgon".single_line AS a, "Dzierzgon".shiftpoints AS b
		WHERE a."XsecID" = b."XsecID" ORDER BY "XsecID", "Fraction";

------------------------------------------------------------------------------------------------
-- Creation of table with Manning's coefficients  --
------------------------------------------------------------------------------------------------

SELECT "XsecID", CASE WHEN "Fraction" < 0.0001 THEN "Fraction" * 0 ELSE "Fraction" END AS "Fraction", "N_Value", "LUCode" INTO "Dzierzgon"."Manning"
FROM "Dzierzgon".tempmann;

DROP TABLE "Dzierzgon".intercrossection,"Dzierzgon".intercrossectiondump, "Dzierzgon".single_line, "Dzierzgon".shiftpoints,"Dzierzgon".tempmann,"Dzierzgon".ludump
