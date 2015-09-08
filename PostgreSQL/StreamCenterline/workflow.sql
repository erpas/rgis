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

-- XsCutline Table

CREATE TABLE start."XsCutlines"
(
  "XsecId" serial primary key,
  "RiverId" integer,
  "Station" double precision,
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

-- NodesTable

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
  ST_Intersects(xs.geom, riv.geom)

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
  riv."FromSta" is NULL

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
  xspts."XsecId" = xs."XsecId"

  