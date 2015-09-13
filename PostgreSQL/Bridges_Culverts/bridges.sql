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


-- UPDATE mosty.bridges AS a
-- SET "River" = "RiverCode" , "Reach" = "ReachCode" FROM mosty."StreamCenterlines" as b
-- WHERE ST_Intersects(a.geom,b.geom);

-- UPDATE mosty.bridges AS a
-- SET "Station" = ST_Line_Locate_Point(b.geom,) FROM mosty.river as b
-- WHERE ST_Intersects(a.geom,b.geom);

-- Create or replace view mosty.punkty as

-- select distinct (ST_Dump(ST_Intersection(a.geom,b.geom))).geom as geom,b."River", a."ReachCode"  into mosty.pkt From mosty."StreamCenterlines" as a, mosty.bridges as b;
-- ALTER TABLE mosty.pkt
-- 	ALTER COLUMN geom TYPE geometry(POINT,2180)
-- 	USING ST_SetSRID(geom,2180);

-- select "Shape_Leng","HydroID","RiverCode","ReachCode","FromNode","ToNode","ArcLength","FromSta","ToSta",(ST_Dump(geom)).geom as geom into mosty.riverd From mosty."StreamCenterlines" ;
-- ALTER TABLE mosty.riverd
-- 	ALTER COLUMN geom TYPE geometry(LINESTRING,2180)
-- 	USING ST_SetSRID(geom,2180);

-- Create or replace view mosty.lokalizacja as
-- Select a."RiverCode",a."ReachCode", (a."ToSta" - a."FromSta")*(1-ST_Line_Locate_Point(a.geom,b.geom)) as "Station" From mosty.riverd as a, mosty.pkt as b WHERE a."ReachCode" = b."ReachCode" ORDER BY "ReachCode", "Station" ;

-- select * from mosty.lokalizacja

