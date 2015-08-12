------------------------------------------------------------------------------------------------------------------------
# Tworzenie linii M - Create LINESTRINGM

CREATE TABLE karolz.streamcenterline_m(
    id serial PRIMARY KEY,
    RiverCode VARCHAR(16),
    ReachCode VARCHAR(16),
    dlugosc real,
    geom geometry(LINESTRINGM,2180));

INSERT INTO karolz.streamcenterline_m(RiverCode, ReachCode, dlugosc, geom)
SELECT RiverCode, ReachCode, ST_AddMeasure(drogi.geom, 0.0, (SELECT ST_Length(drogi.geom))), ST_Length(streamcenterline_m.geom)::real AS dlugosc
FROM karolz.drogi
------------------------------------------------------------------------------------------------------------------------
# Tworzenie miejsc przecięcia linii cieków i przekrojów

CREATE TABLE karolz.punkty_int(
id serial PRIMARY KEY,
geom geometry(POINT),
RiverCode VARCHAR (16),
ReachCode VARCHAR(16));

INSERT INTO karolz.punkty_int(geom, RiverCode, ReachCode)
SELECT
tab.geom,
tab.RiverCode,
tab.ReachCode
FROM (
    SELECT ST_AsText(ST_Intersection(streamcenterline_m.geom, crosssections.geom)) as geom, RiverCode, ReachCode
    FROM karolz.streamcenterline_m, karolz.crosssections) AS tab
WHERE geom <> 'GEOMETRYCOLLECTION EMPTY';

ALTER TABLE karolz.punkty_int
  ALTER COLUMN geom TYPE geometry(POINT, 2180)
    USING ST_SetSRID(geom,2180);
------------------------------------------------------------------------------------------------------------------------
# Nadawanie kilometrażu

CREATE TABLE karolz.punkty_km(
id serial PRIMARY KEY,
nazwa VARCHAR,
geom geometry(POINT),
test VARCHAR,
km REAL);

INSERT INTO karolz.punkty_km(nazwa, geom,test,km)
SELECT *
FROM (
    SELECT
    drogi_m.nazwa,
    punkty_int.geom,
    ST_Intersects(ST_Buffer(drogi_m.geom,0.01),punkty_int.geom) AS test,
    ST_InterpolatePoint(drogi_m.geom,punkty_int.geom) AS km
    FROM karolz.drogi_m, karolz.punkty_int) AS tabela
WHERE test <> 'False'
------------------------------------------------------------------------------------------------------------------------
SELECT id,
    CASE WHEN ST_StartPoint(geom) IN (SELECT ST_EndPoint(geom) FROM public."StreamCenterline") THEN id::text
        ELSE 'unikat'
   END
FROM public."StreamCenterline"
------------------------------------------------------------------------------------------------------------------------
SELECT *
FROM (
    SELECT ST_Intersects(my_linestrings.geom, drogi.geom) AS typ
    FROM karolz.my_linestrings, karolz.drogi)  AS tabela
WHERE tabela.typ IS True
------------------------------------------------------------------------------------------------------------------------
SELECT typ
FROM (
    SELECT ST_Intersects(my_linestrings.geom, drogi.geom) AS typ
    FROM karolz.my_linestrings, karolz.drogi) AS tabela
WHERE typ IS True
------------------------------------------------------------------------------------------------------------------------
WITH tabela AS (
    SELECT ST_Intersects(my_linestrings.geom, drogi.geom) AS typ
    FROM karolz.my_linestrings, karolz.drogi)
SELECT typ FROM tabela
WHERE typ IS True
------------------------------------------------------------------------------------------------------------------------
SELECT sel.id, sel.nazwa, sel.wsp
FROM (
    SELECT my_linestrings.id, drogi.nazwa, ST_AsText(ST_Intersection(drogi.geom, my_linestrings.geom)) AS wsp
    FROM karolz.drogi, karolz.my_linestrings) AS sel
WHERE wsp <> 'GEOMETRYCOLLECTION EMPTY'
------------------------------------------------------------------------------------------------------------------------
CREATE OR REPLACE FUNCTION public.start_in_ends_pg (s GEOMETRY, e GEOMETRY[]) RETURNS text AS $$
BEGIN
    IF s = ANY(e) THEN
        RETURN 'punkt początkowy istnieje w zbiorze punktów końcowych';
    ELSE
        RETURN 'punkt początkowy jest unikalny';
    END IF;
END;
$$ LANGUAGE plpgsql;

SELECT *, start_in_ends(ST_StartPoint(geom), array(SELECT ST_EndPoint(geom) FROM public."StreamCenterline"))
FROM public."StreamCenterline"
------------------------------------------------------------------------------------------------------------------------
CREATE OR REPLACE FUNCTION public.s_in_e (s GEOMETRY, e GEOMETRY[])
    RETURNS text
AS $$
    if s in e:
        return 'punkt początkowy istnieje w zbiorze punktów końcowych'
    else:
        return 'punkt początkowy jest unikalny'
$$ LANGUAGE plpython3u;

SELECT *, start_in_ends(array(SELECT ST_StartPoint(geom) FROM public."StreamCenterline"),array(SELECT ST_EndPoint(geom) FROM public."StreamCenterline"))
FROM public."StreamCenterline"
------------------------------------------------------------------------------------------------------------------------
CREATE TYPE nodes AS (
start_node integer,
end_node integer);

CREATE OR REPLACE FUNCTION from_to_node_py (startpoint GEOMETRY, endpoint GEOMETRY)
    RETURNS nodes
AS $$
try:
    if startpoint in pnts:
        start_node = pnts[startpoint]
    else:
        nr += 1
        start_node = nr
        pnts[startpoint] = start_node
    if endpoint in pnts:
        end_node = pnts[endpoint]
    else:
        nr += 1
        end_node = nr
        pnts[endpoint] = end_node
except NameError:
    global nr
    global pnts
    global start_node
    global end_node
    start_node = 1
    end_node = 2
    nr = 2
    pnts = {startpoint:start_node, endpoint:end_node}
finally:
    return (start_node, end_node)
$$ LANGUAGE plpython3u;

SELECT from_to_node_py (ST_StartPoint(geom), ST_EndPoint(geom)) FROM public."StreamCenterline"
------------------------------------------------------------------------------------------------------------------------
# Rejestracja plpython3u jako języka zaufanego (ostrożnie z tym)

UPDATE pg_language SET lanpltrusted = true WHERE lanname = 'plpython3u'
------------------------------------------------------------------------------------------------------------------------
# Przyznawanie uprawnień do wykonywania funkcji napisanych w plpython3u

GRANT USAGE ON LANGUAGE plpython3u TO kzielinski
------------------------------------------------------------------------------------------------------------------------
CREATE OR REPLACE FUNCTION kursorek(raf text) RETURNS refcursor AS $$
DECLARE
c refcursor := raf;
BEGIN
OPEN c FOR SELECT hydroid FROM raf_manning.roznica;
RETURN c;
END;
$$ LANGUAGE 'plpgsql';

BEGIN;
SELECT kursorek('my_cursor');
FETCH ALL IN my_cursor;
COMMIT;
------------------------------------------------------------------------------------------------------------------------
CREATE OR REPLACE FUNCTION from_to_node ()
    RETURNS VOID AS
$BODY$
DECLARE
    c refcursor;
    r record;
    start_node integer := 0;
    end_node integer := 0;
    nr integer := 0;
BEGIN
CREATE TABLE pnts(
    startpoint text,
    endpoint text,
    sn integer,
    en integer);
OPEN c FOR SELECT * FROM public."StreamCenterline";
FOR r in SELECT ST_AsText(ST_StartPoint(geom)) AS s, ST_AsText(ST_EndPoint(geom)) AS e FROM public."StreamCenterline" LOOP
    IF (SELECT exists (SELECT 1 FROM pnts WHERE startpoint = r.s LIMIT 1)) THEN
        start_node := (SELECT sn FROM pnts WHERE startpoint = r.s LIMIT 1);
    ELSEIF (SELECT exists (SELECT 1 FROM pnts WHERE endpoint = r.s LIMIT 1)) THEN
        start_node := (SELECT en FROM pnts WHERE endpoint = r.s LIMIT 1);
    ELSE
        nr := nr + 1;
        start_node := nr;
    END IF;
    IF (SELECT exists (SELECT 1 FROM pnts WHERE startpoint = r.e LIMIT 1)) THEN
        end_node := (SELECT sn FROM pnts WHERE startpoint = r.e LIMIT 1);
    ELSEIF (SELECT exists (SELECT 1 FROM pnts WHERE endpoint = r.e LIMIT 1)) THEN
        end_node := (SELECT en FROM pnts WHERE endpoint = r.e LIMIT 1);
    ELSE
        nr := nr + 1;
        end_node := nr;
    END IF;
    INSERT INTO pnts VALUES (r.s, r.e, start_node, end_node);
    MOVE c;
    UPDATE public."StreamCenterline" SET
    "FromNode" = start_node,
    "ToNode" = end_node
    WHERE CURRENT OF c;
END LOOP;
CLOSE c;
DROP TABLE pnts;
END;
$BODY$
    LANGUAGE plpgsql;

SELECT from_to_node ()
------------------------------------------------------------------------------------------------------------------------
CREATE OR REPLACE FUNCTION from_to_node ()
    RETURNS VOID AS
$BODY$
DECLARE
    c cursor FOR SELECT * FROM public."StreamCenterline";
    r public."StreamCenterline"%ROWTYPE;
    start_geom text;
    end_geom text;
    start_node integer := 0;
    end_node integer := 0;
    nr integer := 0;
BEGIN
CREATE TABLE pnts(
    startpoint text,
    endpoint text,
    sn integer,
    en integer);
FOR r in c LOOP
    start_geom := ST_AsText(ST_StartPoint(r.geom));
    end_geom := ST_AsText(ST_EndPoint(r.geom));
    IF (SELECT exists (SELECT 1 FROM pnts WHERE startpoint = start_geom LIMIT 1)) THEN
        start_node := (SELECT sn FROM pnts WHERE startpoint = start_geom LIMIT 1);
    ELSEIF (SELECT exists (SELECT 1 FROM pnts WHERE endpoint = start_geom LIMIT 1)) THEN
        start_node := (SELECT en FROM pnts WHERE endpoint = start_geom LIMIT 1);
    ELSE
        nr := nr + 1;
        start_node := nr;
    END IF;
    IF (SELECT exists (SELECT 1 FROM pnts WHERE startpoint = end_geom LIMIT 1)) THEN
        end_node := (SELECT sn FROM pnts WHERE startpoint = end_geom LIMIT 1);
    ELSEIF (SELECT exists (SELECT 1 FROM pnts WHERE endpoint = end_geom LIMIT 1)) THEN
        end_node := (SELECT en FROM pnts WHERE endpoint = end_geom LIMIT 1);
    ELSE
        nr := nr + 1;
        end_node := nr;
    END IF;
    INSERT INTO pnts VALUES (start_geom, end_geom, start_node, end_node);
    UPDATE public."StreamCenterline" SET
    "FromNode" = start_node,
    "ToNode" = end_node
    WHERE CURRENT OF c;
END LOOP;
DROP TABLE pnts;
END;
$BODY$
    LANGUAGE plpgsql;

SELECT from_to_node ()
------------------------------------------------------------------------------------------------------------------------
CREATE OR REPLACE FUNCTION from_to_node ()
    RETURNS VOID AS
$BODY$
DECLARE
    c cursor FOR SELECT * FROM "StreamCenterline";
    r "StreamCenterline"%ROWTYPE;
    start_geom geometry;
    end_geom geometry;
    start_node integer := 0;
    end_node integer := 0;
    nr integer := 0;
BEGIN
DROP TABLE IF EXISTS "NodesTable";
CREATE TABLE "NodesTable"(
    geom geometry(POINT, 2180),
    "NodeID" integer,
    "X" real,
    "Y" real);
FOR r in c LOOP
    start_geom := ST_StartPoint(r.geom);
    end_geom := ST_EndPoint(r.geom);
    IF (SELECT exists (SELECT 1 FROM "NodesTable" WHERE geom = start_geom LIMIT 1)) THEN
        start_node := (SELECT "NodeID" FROM "NodesTable" WHERE geom = start_geom LIMIT 1);
    ELSE
        nr := nr + 1;
        start_node := nr;
        INSERT INTO "NodesTable" VALUES (start_geom, nr, ST_X(start_geom), ST_Y(start_geom));
    END IF;
    IF (SELECT exists (SELECT 1 FROM "NodesTable" WHERE geom = end_geom LIMIT 1)) THEN
        end_node := (SELECT "NodeID" FROM "NodesTable" WHERE geom = end_geom LIMIT 1);
    ELSE
        nr := nr + 1;
        end_node := nr;
        INSERT INTO "NodesTable" VALUES (end_geom, nr, ST_X(end_geom), ST_Y(end_geom));
    END IF;
    UPDATE "StreamCenterline" SET
    "FromNode" = start_node,
    "ToNode" = end_node
    WHERE CURRENT OF c;
END LOOP;
END;
$BODY$
    LANGUAGE plpgsql;

SELECT from_to_node ()
------------------------------------------------------------------------------------------------------------------------
testest