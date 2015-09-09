
------------------------------------------------------------------------------------------------
-- Intersect warstw uzytkowania z przekrojami  --
------------------------------------------------------------------------------------------------

SELECT mann.hydroid, mann.n_value, mann.lucode, ST_AsText((ST_Dump(mann.geom)).geom) AS geom INTO raf_manning2.przekroje_inter
	FROM
		(SELECT ST_AsText(ST_Intersection(uzytkowanie3.geom, xcutlines3single.geom))
			AS geom,lucode,n_value, hydroid
			FROM raf_manning2.uzytkowanie3, raf_manning2.xcutlines3single) AS mann
				WHERE geom <> 'GEOMETRYCOLLECTION EMPTY' ORDER BY hydroid;

ALTER TABLE raf_manning2.przekroje_inter
	ALTER COLUMN geom TYPE geometry(LINESTRING,2180)
	USING ST_SetSRID(geom,2180);

------------------------------------------------------------------------------------------------
-- Multilinestring to line string --
------------------------------------------------------------------------------------------------

SELECT hydroid, ST_AsText((ST_Dump(xcutlines3single.geom)).geom) AS geom INTO raf_manning2.single_line
	FROM raf_manning2.xcutlines3single ORDER BY hydroid;

ALTER TABLE raf_manning2.single_line
 	ALTER COLUMN geom TYPE geometry(LINESTRING,2180)
  	USING ST_SetSRID(geom,2180);

CREATE INDEX idx_single_line
 	ON raf_manning2.single_line
 	 	USING gist(geom);

------------------------------------------------------------------------------------------------
-- Stworzenie punktów na poczatku linii przesunietych o 5 mm wzdluz lini celem odpowiedniego sczytania wartosci N_Value  --
------------------------------------------------------------------------------------------------

SELECT hydroid, n_value, lucode, ST_Line_Interpolate_Point(przekroje_inter.geom,0.00005) as geom INTO raf_manning2.lininp
	FROM raf_manning2.przekroje_inter ORDER BY hydroid;

ALTER TABLE raf_manning2.lininp
	ALTER COLUMN geom TYPE geometry(POINT,2180)
	USING ST_SetSRID(geom,2180);

CREATE INDEX idx_lininp
 	ON raf_manning2.lininp
 	 	USING gist(geom);

------------------------------------------------------------------------------------------------
-- Wyliczenie ulamka odleglosci punktow wzdluz linii przekroju  --
------------------------------------------------------------------------------------------------

SELECT  b.hydroid, b.n_value, b.lucode, ST_LineLocatePoint(a.geom,b.geom) AS "Fraction" INTO raf_manning2.tempmann
	FROM raf_manning2.single_line AS a, raf_manning2.lininp AS b
		WHERE a.hydroid = b.hydroid ORDER BY hydroid, "Fraction";

------------------------------------------------------------------------------------------------
-- Stworzenie docelowej tabeli z wartosciami wspolczynnikow Manninga  --
------------------------------------------------------------------------------------------------

SELECT hydroid AS "XS2DID", CASE WHEN "Fraction" < 0.0001 THEN "Fraction" * 0 ELSE "Fraction" END AS "Fraction", n_value AS "N_Value", lucode INTO raf_manning2."Manning"
FROM raf_manning2.tempmann;

DROP TABLE raf_manning2.przekroje_inter, raf_manning2.single_line, raf_manning2.lininp,raf_manning2.tempmann
