-- współczynniki szorstkości Manninga

DROP TABLE IF EXISTS start."LanduseAreas";

CREATE TABLE start."LanduseAreas"
(
  "LUID" serial primary key,
  "LUCode" character varying(32),
  "N_Value" double precision,
  geom geometry(Polygon,2180) -- UWAGA: geometria prosta a NIE multi
);

CREATE INDEX sidx_landuse_geom ON
    start."LanduseAreas"
USING gist (geom);

-- dodaj jakies obiekty do powyzszych tabel i uruchom zapytania ponizej

INSERT INTO
  start."LanduseAreas" ("LUCode", "N_Value", geom)
VALUES
  ('a', 0.01, ST_GeomFromText('POLYGON((323284 393262,323271 392115,324238 392126,324090 393255,323284 393262))',2180)),
  ('b', 0.02, ST_GeomFromText('POLYGON((324090 393255,324275 393270,324403 392149,324238 392126,324090 393255))',2180)),
  ('c', 0.03, ST_GeomFromText('POLYGON((324275 393270,324433 393279,324462 392776,324530 392165,324403 392149,324275 393270))',2180)),
  ('d', 0.04, ST_GeomFromText('POLYGON((324433 393279,324786 393283,324787 393080,324532 392777,324462 392776,324433 393279))',2180)),
  ('e', 0.05, ST_GeomFromText('POLYGON((324815 392196,324530 392165,324462 392776,324532 392777,324687 392593,324815 392196))',2180)),
  ('f', 0.06, ST_GeomFromText('POLYGON((324532 392777,324787 393080,324786 393283,325222 392320,324815 392196,324687 392593,324532 392777))',2180));

-- tabela punktow zmiany szorstkosci

DROP TABLE IF EXISTS start."Manning";
create table start."Manning" (
    "MannID" bigserial primary key,
    "XsecID" integer,
    "Fraction" double precision, -- wzgledne polozenie na linii przekroju
    "LUCode" text, -- kod pokrycia
    "N_Value" double precision, -- wsp szorstkosci
    geom geometry(point, 2180) -- geometria
);

CREATE INDEX sidx_luchangelocations_geom ON
    start."Manning"
USING gist (geom);


-- znajdz punkty zmiany szorstkosci

with linie_z_poligonow as ( -- tymczasowe granice poligonow uzytkowania
SELECT
    (ST_Dump(ST_Boundary(geom))).geom
FROM start."LandUse"
)
insert into start."Manning"
    ("XsecID", geom)
select distinct
    xs."XsecID", -- zeby wiedziec na jakim przekroju lezy punkt
    (ST_Dump(ST_Intersection(l.geom, xs.geom))).geom as geom
from
    linie_z_poligonow l,
    start."XSCutLines" xs
where
    l.geom && xs.geom;


-- dodaj do pktow zmiany poczatki przekrojow
insert into start."Manning"
    ("XsecID", geom)
select
    xs."XsecID",
    ST_LineInterpolatePoint(xs.geom, 0.0)
from
    start."XSCutLines" xs;


-- ustal polozenie pktow zmiany wzdluz przekrojow

update
    start."Manning" as p
set
    "Fraction" = ST_LineLocatePoint(xs.geom, p.geom)
from
    start."XSCutLines" as xs
where
    xs."XsecID" = p."XsecID";


-- probkuj kod uzytkowania z poligonow

update
    start."Manning" as p
set
    "LUCode" = u."LUCode",
    "N_Value" = u."N_Value"
from
    start."LandUse" as u,
    start."XSCutLines" as xs
where
    xs."XsecID" = p."XsecID" AND
    ST_LineInterpolatePoint(xs.geom, p."Fraction"+0.001) && u.geom AND
    ST_Intersects(ST_LineInterpolatePoint(xs.geom, p."Fraction"+0.001), u.geom);
