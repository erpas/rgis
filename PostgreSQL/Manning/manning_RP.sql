--Stworzenie tabeli z atrybutami dla nowej warstwy wynikowej 

CREATE TABLE raf_manning.przekroje_inter (hydroid int, n_value varchar, lucode varchar, geom geometry(LINESTRING), line_length float);

--Intersect warstw uzytkowania z przekrojami i upload wynikow do wczesniej stworzonej tabeli

CREATE VIEW temp_tab AS

SELECT mann.hydroid, mann.n_value,mann.lucode, ST_AsText((ST_Dump(mann.geom)).geom) AS geom
FROM 
	(SELECT ST_AsText(ST_Intersection(uzytkowanie.geom, xscutlines.geom)) 
		AS geom,lucode,n_value, hydroid
		FROM raf_manning.uzytkowanie, raf_manning.xscutlines) 
AS mann 
WHERE geom <> 'GEOMETRYCOLLECTION EMPTY'
ORDER BY hydroid;

INSERT INTO raf_manning.przekroje_inter(hydroid, n_value , lucode, geom, line_length)
SELECT hydroid , n_value , lucode , geom , ST_Length(geom) AS line 
FROM temp_tab;

ALTER TABLE raf_manning.przekroje_inter
ALTER COLUMN geom 
TYPE geometry(LINESTRING,2180) 
USING ST_SetSRID(geom,2180);

DROP VIEW temp_tab;

-- obliczanie calkowitej dlugosci poszczegolnych przekrojow

CREATE VIEW dlugosc AS

SELECT hydroid, SUM(line_length) as line_sum
FROM raf_manning.przekroje_inter
GROUP BY hydroid
ORDER BY hydroid;

--wyliczenie ulamka dlugosci

SELECT r.hydroid, r.n_value , r.lucode, r.line_length, d.line_sum, ((100*r.line_length)/d.line_sum) as "Fraction"
FROM raf_manning.przekroje_inter AS r
LEFT JOIN dlugosc AS d ON r.hydroid = d.hydroid
ORDER BY hydroid,geom;



