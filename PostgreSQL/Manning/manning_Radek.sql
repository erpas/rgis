
-- tabela przekrojow
CREATE TABLE start.xscutlines
(
  gid serial NOT NULL,
  hydroid integer,
  geom geometry(LineString,2180), -- UWAGA: geometria prosta a NIE multi
  CONSTRAINT xscutlines_pkey PRIMARY KEY (gid)
);

CREATE INDEX sidx_xscutlines_geom ON
    start.xscutlines
USING gist (geom);

-- tabela uzytkowania
CREATE TABLE start.uzytkowanie
(
  gid serial primary key,
  lucode character varying(32),
  n_value double precision,
  geom geometry(Polygon,2180), -- UWAGA: geometria prosta a NIE multi
);

CREATE INDEX sidx_uzytkowanie_geom ON
    start.uzytkowanie
USING gist (geom);

-- dodaj jakies obiekty do powyzszych tabel i uruchom zapytania ponizej

-- tabela punktow zmiany szorstkosci
create table start.pkty_zmiany (
    gid bigserial primary key,
    xs_hid integer,
    m double precision, -- wzgledne polozenie na linii przekroju
    code text, -- kod pokrycia
    n double precision, -- wsp szorstkosci
	geom geometry(point, 2180) -- geometria
);

CREATE INDEX sidx_pkty_zmiany_geom ON
    start.pkty_zmiany
USING gist (geom);


-- znajdz punkty zmiany szorstkosci

with linie_z_poligonow as ( -- tymczasowe granice poligonow uzytkowania
SELECT
    (ST_Dump(ST_Boundary(geom))).geom
FROM start.uzytkowanie
)
insert into start.pkty_zmiany
    (xs_hid, geom)
select distinct
    xs.hydroid, -- zeby wiedziec na jakim przekroju lezy punkt
    (ST_Dump(ST_Intersection(l.geom, xs.geom))).geom as geom
from
    linie_z_poligonow l,
    start.xscutlines xs
where
    l.geom && xs.geom;


-- dodaj do pktow zmiany poczatki przekrojow
insert into start.pkty_zmiany
    (xs_hid, geom)
select
    xs.hydroid,
    ST_LineInterpolatePoint(xs.geom, 0.0)
from
    start.xscutlines xs;


-- ustal polozenie pktow zmiany wzdluz przekrojow

update
    start.pkty_zmiany as p
set
    m = ST_LineLocatePoint(xs.geom, p.geom) + 0.001
from
    start.xscutlines as xs
where
    xs.hydroid = p.xs_hid;


-- probkuj kod uzytkowania z poligonow

update
    start.pkty_zmiany as p
set
    code = u.lucode
from
    start.uzytkowanie as u
where
    p.geom && u.geom and
    ST_Intersects(p.geom, u.geom);
