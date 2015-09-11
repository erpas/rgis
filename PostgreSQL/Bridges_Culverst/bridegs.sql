-- stworzenie tabeli dla warstwy z mostami

CREATE TABLE mosty.bridges ("HydroID" int, "River" varchar, "Reach" varchar, "Station" float, "USDistance" float, "TopWidth" float, "NodeName" varchar, geom geometry);

ALTER TABLE mosty.bridges
	ALTER COLUMN geom TYPE geometry(LINESTRING,2180)
	USING ST_SetSRID(geom,2180);

CREATE INDEX idx_bridges
 	ON mosty.bridges
 	 	USING gist(geom);

UPDATE mosty.bridges AS a
SET "River" = rivercode , "Reach" = reachcode FROM mosty.river AS b
WHERE ST_Intersects(a.geom,b.geom);