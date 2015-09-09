DROP TABLE start."StreamCenterlines";

CREATE TABLE start."StreamCenterlines"
(
  "RiverId" serial primary key,
  "RiverCode" text,
  "ReachCode" text,
  "FromNode" integer,
  "ToNode" integer,
  "ReachLen" double precision,
  "FromSta" double precision,
  "ToSta" double precision,
  "Notes" text,
  geom geometry(LineString,2180)
);

CREATE INDEX "sidx_RiverCenterlines_geom"
  ON start."StreamCenterlines"
  USING gist
  (geom);

-- utworz przykładowe obiekty StreamCenterlines

INSERT INTO
  start."StreamCenterlines" ("RiverCode", "ReachCode", geom)
VALUES
    ('Odra', 'testowy', ST_GeomFromText('LINESTRING(324411 392195.305535,324239 392416,324058 392628,324006 392795,323997 392993,323992 393221)',2180)),
    ('Doplyw A', 'dolna część', ST_GeomFromText('LINESTRING(324539 392790,324022 392743)',2180)),
    ('Doplyw A', 'górna część', ST_GeomFromText('LINESTRING(325014 392216,324887 392383,324772 392378,324711 392493,324673 392635,324577 392731,324539 392790)',2180)),
    ('Doplyw B', 'testowy', ST_GeomFromText('LINESTRING(325337 393195,325222 393136,325022 393082,324831 393049,324709 393021,324645 392964,324589 392858,324539 392790)',2180));

-- XsCutline Table
DROP TABLE start."XsCutlines";

CREATE TABLE start."XsCutlines"
(
  "XsecId" serial primary key,
  "RiverId" integer,
  "Station" double precision,
  "Nr" integer,
  "LeftBank" double precision,
  "RightBank" double precision,
  "LeftLen" double precision,
  "ChanLen" double precision,
  "RightLen" double precision,
  "Name" text,
  "Description" text,
  geom geometry(LineString,2180)
);

CREATE INDEX "sidx_XsCutlines_geom"
  ON start."XsCutlines"
  USING gist
  (geom);

-- utwórz kilka przykładowych obiektów XsCutline

INSERT INTO
  start."XsCutlines" (geom)
VALUES
  (ST_GeomFromText('LINESTRING(323889 393184,324455 393217)', 2180)),
  (ST_GeomFromText('LINESTRING(323325 392863,324468 392966)', 2180)),
  (ST_GeomFromText('LINESTRING(323305 392364,324486 392721)', 2180)),
  (ST_GeomFromText('LINESTRING(324424 392734,324419 392832)', 2180)),
  (ST_GeomFromText('LINESTRING(324499 392736,324497 392835)', 2180)),
  (ST_GeomFromText('LINESTRING(324540 392695,324628 392760)', 2180)),
  (ST_GeomFromText('LINESTRING(324502 392496,325037 392677)', 2180)),
  (ST_GeomFromText('LINESTRING(324561 392214,325130 392393)', 2180)),
  (ST_GeomFromText('LINESTRING(324637 392813,324516 392892)', 2180)),
  (ST_GeomFromText('LINESTRING(324759 392945,324690 393101)', 2180)),
  (ST_GeomFromText('LINESTRING(323338 392165,324207 392230,324416 392390,324571 392434)', 2180));


-- Linie brzegów (BankLines)
DROP TABLE start."BankLines";

CREATE TABLE start."BankLines"
(
  "BankId" SERIAL PRIMARY KEY,
  "Type"   TEXT,
  geom     GEOMETRY(LINESTRING, 2180)
);

INSERT INTO
  start."BankLines" ("Type", geom)
VALUES
  ('Right', ST_GeomFromText('LINESTRING(324453 392252,324342 392419,324238 392509,324130 392620,324057 392812,324039 393021,324057 393226)', 2180)),
  ('Left', ST_GeomFromText('LINESTRING(324307 392227,324165 392387,324092 392485,324008 392586,323918 392808,323900 393021,323911 393233)', 2180)),
  ('Left', ST_GeomFromText('LINESTRING(324972 392245,324888 392312,324821 392340,324744 392373,324707 392434,324671 392532,324605 392652,324551 392700,324527 392737,324480 392756,324422 392753)', 2180)),
  ('Right', ST_GeomFromText('LINESTRING(325005 392300,324908 392396,324788 392443,324728 392558,324688 392650,324622 392728,324579 392770,324546 392799,324500 392810,324415 392814)', 2180)),
  ('Left', ST_GeomFromText('LINESTRING(324584 392817,324754 392991,324841 393007)', 2180)),
  ('Right', ST_GeomFromText('LINESTRING(324817 393121,324690 393068,324549 392923,324530 392845)', 2180));


-- drogi przepływu (flow paths)
DROP TABLE start."Flowpaths";

CREATE TABLE start."Flowpaths"
(
  "PathId" SERIAL PRIMARY KEY,
  "Type"   TEXT,
  geom     GEOMETRY(LINESTRING, 2180)
);

-- dodanie przykładowych dróg przepływu
INSERT INTO
  start."Flowpaths" ("Type", geom)
VALUES
  ('Channel', ST_GeomFromText('LINESTRING(324411 392195.305535,324239 392416,324058 392628,324006 392795,323997 392993,323992 393221)', 2180)),
('Channel', ST_GeomFromText('LINESTRING(325337 393195,325222 393136,325022 393082,324831 393049,324709 393021,324645 392964,324589 392858,324539 392790)', 2180)),
('Right', ST_GeomFromText('LINESTRING(324487 392297,324288 392787,324238 393068,324219 393243)', 2180)),
('Right', ST_GeomFromText('LINESTRING(324798 393101,324662 393052,324589 392965,324558 392885,324535 392841)', 2180)),
('Channel', ST_GeomFromText('LINESTRING(325014 392216,324887 392383,324772 392378,324711 392493,324673 392635,324577 392731,324539 392790,324022 392743)', 2180)),
('Left', ST_GeomFromText('LINESTRING(323812 392179,323709 392398,323700 392626,323763 392913,323932 393210)', 2180)),
('Left', ST_GeomFromText('LINESTRING(324770 392180,324654 392410,324562 392650,324525 392734,324507 392758,324481 392763,324415 392761)', 2180)),
('Right', ST_GeomFromText('LINESTRING(325075 392267,324876 392594,324734 392703,324617 392757,324525 392807,324408 392810)', 2180)),
('Left', ST_GeomFromText('LINESTRING(324815 393013,324600 392817)', 2180));

-- NodesTable
-- Tabela wypełniana za pomocą funkcji from_to_node
DROP TABLE IF EXISTS start."NodesTable";

CREATE TABLE start."NodesTable"
(
  "NodeId" serial primary key,
  "X" double precision,
  "Y" double precision
  );



-- Nadanie RiverId przekrojom

UPDATE start."XsCutlines" as xs
SET 
  "RiverId" = riv."RiverId"
FROM
  start."StreamCenterlines" as riv
WHERE
  xs.geom && riv.geom AND
  ST_Intersects(xs.geom, riv.geom);

-- Nadanie stacji (kilometraza) przekrojom

-- UWAGA: Pola FromSta i ToSta rzek nie moga byc puste!
-- trzeba sprawdzic i jesli sa puste, nalezy je uzupelnic na 
-- podstawie faktyczne dlugosci rzeki, przyjmuja ToSta = 0
-- poniewaz rzeki rysujemy od zrodel do ujscia, to ToSta
-- jest stacja ujscia

UPDATE
  start."StreamCenterlines" as riv
SET
  "FromSta" = ST_Length(riv.geom),
  "ToSta" = 0
WHERE
  riv."FromSta" is NULL;

WITH xspts as (
  SELECT 
    xs."XsecId" as "XsecId",
    riv."RiverId" as "RiverId",
    ST_LineLocatePoint(riv.geom, ST_Intersection(xs.geom, riv.geom)) as "Fraction"
  FROM
    start."StreamCenterlines" as riv,
    start."XsCutlines" as xs
  WHERE
    xs.geom && riv.geom AND
    ST_Intersects(xs.geom, riv.geom)
)
UPDATE start."XsCutlines" as xs
SET
  "Station" = riv."FromSta" + xspts."Fraction" * (riv."ToSta" - riv."FromSta")
FROM
  xspts,
  start."StreamCenterlines" as riv
WHERE
  xspts."RiverId" = riv."RiverId" AND
  xspts."XsecId" = xs."XsecId";

-- nadaj przekrojom kolejny numer na odcinku idac od gory

WITH orderedXsecs as (
  SELECT
    "XsecId",
    "RiverId",
    rank() OVER (PARTITION BY "RiverId" ORDER BY "Station" ASC) as rank
  FROM
    start."XsCutlines"
)
UPDATE start."XsCutlines" as xs
  SET
    "Nr" = rank
  FROM
    orderedXsecs as ox
  WHERE
    xs."XsecId" = ox."XsecId";



-- brzegi rzeki (banks) - w Mike'u 11 markery 4 i 5

WITH bankpts as (
  SELECT
    xs."XsecId" as "XsecId",
    ST_LineLocatePoint(xs.geom, ST_Intersection(xs.geom, bl.geom)) as "Fraction"
  FROM
    start."BankLines" as bl,
    start."XsCutlines" as xs
  WHERE
    xs.geom && bl.geom AND
    ST_Intersects(xs.geom, bl.geom)
)
UPDATE start."XsCutlines" as xs
SET
  "LeftBank" = minmax."minFrac",
  "RightBank" = minmax."maxFrac"
FROM
  (
  SELECT
    "XsecId",
    min("Fraction") as "minFrac",
    max("Fraction") as "maxFrac"
  FROM
    bankpts as bp
  GROUP BY "XsecId"
  ) minmax
WHERE
  xs."XsecId" = minmax."XsecId";



-- odleglosci wzdluż dróg przepływu

-- tworze tabele kilometrazu wzdluz 3 drog przeplywu
DROP TABLE start."FlowpathStations";

CREATE TABLE start."FlowpathStations" (
  "XsecId" integer primary key,
  "RiverId" integer,
  "Nr" integer,
  "LeftSta" double precision,
  "ChanSta" double precision,
  "RightSta" double precision
);

-- wkladam do tabeli wszystkie przekroje z ich identyfikatorami
INSERT INTO start."FlowpathStations"
  ("XsecId", "RiverId", "Nr")
SELECT
  "XsecId",
  "RiverId",
  "Nr"
FROM
  start."XsCutlines";

-- nadaje przekrojom kilometraz wzdluz linii typu Channel

WITH xspts as (
  SELECT
    xs."XsecId" as "XsecId",
    path."Type" as "Type",
    ST_LineLocatePoint(path.geom, ST_Intersection(xs.geom, path.geom))
      * ST_Length(path.geom) as "Station"
  FROM
    start."Flowpaths" as path,
    start."XsCutlines" as xs
  WHERE
    path."Type" = 'Channel' AND
    xs.geom && path.geom AND
    ST_Intersects(xs.geom, path.geom)
)
UPDATE start."FlowpathStations" as flowSta
SET
  "ChanSta" = xspts."Station"
FROM
  xspts
WHERE
  xspts."XsecId" = flowSta."XsecId";

-- nadaje przekrojom kilometraz wzdluz linii typu Left

WITH xspts as (
  SELECT
    xs."XsecId" as "XsecId",
    path."Type" as "Type",
    ST_LineLocatePoint(path.geom, ST_Intersection(xs.geom, path.geom))
      * ST_Length(path.geom) as "Station"
  FROM
    start."Flowpaths" as path,
    start."XsCutlines" as xs
  WHERE
    path."Type" = 'Left' AND
    xs.geom && path.geom AND
    ST_Intersects(xs.geom, path.geom)
)
UPDATE start."FlowpathStations" as flowSta
SET
  "LeftSta" = xspts."Station"
FROM
  xspts
WHERE
  xspts."XsecId" = flowSta."XsecId";

-- nadaje przekrojom kilometraz wzdluz linii typu Right

WITH xspts as (
  SELECT
    xs."XsecId" as "XsecId",
    path."Type" as "Type",
    ST_LineLocatePoint(path.geom, ST_Intersection(xs.geom, path.geom))
      * ST_Length(path.geom) as "Station"
  FROM
    start."Flowpaths" as path,
    start."XsCutlines" as xs
  WHERE
    path."Type" = 'Right' AND
    xs.geom && path.geom AND
    ST_Intersects(xs.geom, path.geom)
)
UPDATE start."FlowpathStations" as flowSta
SET
  "RightSta" = xspts."Station"
FROM
  xspts
WHERE
  xspts."XsecId" = flowSta."XsecId";

-- teraz trzeba sprawdzić czy wszystkie drogi przepływu przecinaja przekroje
-- jesli nie, to w tablicy "FlowpathStations" są braki i trzeba zmienic przebieg "Flowpaths"
-- a nastepnie uruchomic ponownie nadawanie stacji wzdluz drog przeplywu

-- wlasciwe obliczenie odleglosci wzdluz drog przeplywu

UPDATE start."XsCutlines" as xs
SET
  "LeftLen" = nfs."LeftSta" - fs."LeftSta",
  "ChanLen" = nfs."ChanSta" - fs."ChanSta",
  "RightLen" = nfs."RightSta" - fs."RightSta"
FROM
  start."FlowpathStations" as fs,
  start."FlowpathStations" as nfs
WHERE
  xs."Nr" > 1 AND
  xs."RiverId" = fs."RiverId" AND
  fs."RiverId" = nfs."RiverId" AND
  xs."XsecId" = fs."XsecId" AND
  xs."Nr" = fs."Nr" AND
  xs."Nr" = nfs."Nr" + 1;

-- nadaj zerowe odleglosci ostatnim przekrojom na odcinkach rzek (przy ujsciu)

UPDATE start."XsCutlines" as xs
SET
  "LeftLen" = 0,
  "ChanLen" = 0,
  "RightLen" = 0
WHERE
  xs."Nr" = 1;

