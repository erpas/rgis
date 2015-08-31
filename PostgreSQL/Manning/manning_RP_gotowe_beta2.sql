
----------------------------------------------------------------
-- Stworzenie tabeli z atrybutami dla nowej warstwy wynikowej --
----------------------------------------------------------------

CREATE TABLE raf_manning2.przekroje_inter (hydroid int, n_value varchar, lucode varchar, geom geometry(LINESTRING), line_length float);

------------------------------------------------------------------------------------------------
-- Intersect warstw uzytkowania z przekrojami i upload wynikow do wczesniej stworzonej tabeli --
------------------------------------------------------------------------------------------------

WITH
  temp_tab AS
    SELECT
    	mann.hydroid, mann.n_value,mann.lucode, ST_AsText((ST_Dump(mann.geom)).geom) AS geom
    FROM
			(SELECT ST_AsText(ST_Intersection(uzytkowanie.geom, xscutlines.geom)) AS geom,lucode,n_value, hydroid
		FROM raf_manning2.uzytkowanie, raf_manning2.xscutlines) 
AS mann 
WHERE geom <> 'GEOMETRYCOLLECTION EMPTY'
ORDER BY hydroid;

INSERT INTO raf_manning2.przekroje_inter(hydroid, n_value , lucode, geom, line_length)
SELECT hydroid , n_value , lucode , geom , ST_Length(geom) AS line 
FROM temp_tab;

ALTER TABLE raf_manning2.przekroje_inter
ALTER COLUMN geom 
TYPE geometry(LINESTRING,2180) 
USING ST_SetSRID(geom,2180);

DROP VIEW temp_tab;
------------------------------------------------------------------------------------------------
-- Multilinestring to line string --
------------------------------------------------------------------------------------------------
CREATE VIEW raf_manning2.multiline2line AS

SELECT hydroid, ST_AsText((ST_Dump(xscutlines.geom)).geom) AS geom FROM raf_manning2.xscutlines;


SELECT * INTO raf_manning2.single_line FROM raf_manning2.multiline2line ORDER BY hydroid;

 	 
ALTER TABLE raf_manning2.single_line 
 	ALTER COLUMN geom TYPE geometry(LINESTRING,2180)
  	USING ST_SetSRID(geom,2180);
 
CREATE INDEX idx_single_line 
 	ON raf_manning2.single_line
 	 	USING gist(geom);

DROP VIEW raf_manning2.multiline2line;
------------------------------------------------------------------------------------------------
-- Stworzenie punktów na poczatku linii przesunietych o 5 mm wzdluz lini celem odpowiedniego sczytania wartosci N_Value  --
------------------------------------------------------------------------------------------------

CREATE VIEW raf_manning2.linp AS

SELECT hydroid, n_value,  ST_Line_Interpolate_Point(przekroje_inter.geom,0.00005) as geom FROM raf_manning2.przekroje_inter;

SELECT * INTO raf_manning2.lininp FROM raf_manning2.linp ORDER BY hydroid;

ALTER TABLE raf_manning2.lininp 
ALTER COLUMN geom TYPE geometry(POINT,2180)
USING ST_SetSRID(geom,2180);

CREATE INDEX idx_lininp 
 	ON raf_manning2.lininp
 	 	USING gist(geom);

DROP VIEW raf_manning2.linp;

------------------------------------------------------------------------------------------------
-- Wyliczenie ulamka odleglosci punktow wzdluz linii przekroju  --
------------------------------------------------------------------------------------------------

CREATE VIEW raf_manning2.tabsort AS
SELECT  b.hydroid,b.n_value, ST_LineLocatePoint(a.geom,b.geom) AS "Fraction"
	FROM raf_manning2.single_line AS a, raf_manning2.lininp AS b WHERE a.hydroid = b.hydroid ORDER BY hydroid, "Fraction"; 
SELECT * INTO raf_manning2.tempmann FROM raf_manning2.tabsort;
DROP VIEW raf_manning2.tabsort;
------------------------------------------------------------------------------------------------
-- Stworzenie docelowej tabeli z wartosciami wspolczynnikow Manninga  --
------------------------------------------------------------------------------------------------

CREATE VIEW raf_manning2.manngot AS
SELECT hydroid AS "XS2DID", CASE WHEN "Fraction" < 0.0001 THEN "Fraction" * 0 ELSE "Fraction" END AS "Fraction", n_value AS "N_Value"
FROM raf_manning2.tempmann;

SELECT * INTO raf_manning2."Manning" FROM raf_manning2.manngot;
DROP VIEW raf_manning2.manngot;

DROP TABLE raf_manning2.przekroje_inter,raf_manning2.single_line, raf_manning2.lininp,raf_manning2.tempmann









