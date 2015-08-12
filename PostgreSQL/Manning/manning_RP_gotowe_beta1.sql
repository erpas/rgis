
----------------------------------------------------------------
-- Stworzenie tabeli z atrybutami dla nowej warstwy wynikowej --
----------------------------------------------------------------

CREATE TABLE raf_manning.przekroje_inter (hydroid int, n_value varchar, lucode varchar, geom geometry(LINESTRING), line_length float);

------------------------------------------------------------------------------------------------
-- Intersect warstw uzytkowania z przekrojami i upload wynikow do wczesniej stworzonej tabeli --
------------------------------------------------------------------------------------------------

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

--------------------------------------------------------------
-- obliczanie calkowitej dlugosci poszczegolnych przekrojow --
--------------------------------------------------------------

CREATE VIEW raf_manning.dlugosc AS

SELECT hydroid, SUM(line_length) as line_sum
FROM raf_manning.przekroje_inter
GROUP BY hydroid
ORDER BY hydroid;

--------------------------------
-- wyliczenie ulamka dlugosci --
--------------------------------

CREATE VIEW raf_manning.ulamek AS

SELECT r.hydroid, r.n_value , r.lucode, r.line_length, d.line_sum, ((100*r.line_length)/d.line_sum) as "Fraction" 
FROM raf_manning.przekroje_inter AS r
LEFT JOIN raf_manning.dlugosc AS d ON r.hydroid = d.hydroid
ORDER BY hydroid,geom;

SELECT * INTO raf_manning.roznica FROM raf_manning.ulamek;
ALTER TABLE raf_manning.roznica ADD COLUMN id serial PRIMARY KEY;


DROP VIEW raf_manning.ulamek;
DROP VIEW raf_manning.dlugosc;

---------------------------------------------------------------------------------------------------------------------------------------------------
-- tworzenie kaskad w ktorych zawarte sa wartosci procentowe informujace o zmianie wartosci wspolczynnika manninga dla poszczegolnych przekrojow.--
---------------------------------------------------------------------------------------------------------------------------------------------------

create view raf_manning.jeden as

select f.id, f.hydroid, f.n_value, f."Fraction", (f."Fraction" + f2."Fraction") as a  
	From raf_manning.roznica as f
	left join raf_manning.roznica as f2 On f.id = f2.id +1  and f.hydroid = f2.hydroid;

select * INTO raf_manning.tab1 from raf_manning.jeden;
drop view raf_manning.jeden;

create view raf_manning.dwa as
select f.id, f.hydroid, f.n_value, f."Fraction",f.a, (f.a + f2."Fraction") as b  
	From raf_manning.tab1 as f
	left join raf_manning.tab1 as f2 On f.id = f2.id+2  and f.hydroid = f2.hydroid;

select * INTO raf_manning.tab2 from raf_manning.dwa;
drop view raf_manning.dwa;
drop table raf_manning.tab1;

create view raf_manning.trzy as
select f.id, f.hydroid, f.n_value, f."Fraction",f.a,f.b, (f.b + f2."Fraction") as c  
	From raf_manning.tab2 as f
	left join raf_manning.tab2 as f2 On f.id = f2.id+3  and f.hydroid = f2.hydroid;

select * INTO raf_manning.tab3 from raf_manning.trzy;
drop view raf_manning.trzy;
drop table raf_manning.tab2;
	
create view raf_manning.cztery as
select f.id, f.hydroid, f.n_value, f."Fraction",f.a,f.b,f.c, (f.c + f2."Fraction") as d  
	From raf_manning.tab3 as f
	left join raf_manning.tab3 as f2 On f.id = f2.id+4  and f.hydroid = f2.hydroid;

select * INTO raf_manning.tab4 from raf_manning.cztery;
drop view raf_manning.cztery;
drop table raf_manning.tab3;

create view raf_manning.piec as
select f.id, f.hydroid, f.n_value, f."Fraction",f.a,f.b,f.c,f.d, (f.d + f2."Fraction") as e  
	From raf_manning.tab4 as f
	left join raf_manning.tab4 as f2 On f.id = f2.id+5  and f.hydroid = f2.hydroid;

select * INTO raf_manning.tab5 from raf_manning.piec;
drop view raf_manning.piec;
drop table raf_manning.tab4;

create view raf_manning.szesc as
select f.id, f.hydroid, f.n_value, f."Fraction",f.a,f.b,f.c,f.d,f.e, (f.e + f2."Fraction") as g  
	From raf_manning.tab5 as f
	left join raf_manning.tab5 as f2 On f.id = f2.id+6  and f.hydroid = f2.hydroid;

select * INTO raf_manning.tab6 from raf_manning.szesc;
drop view raf_manning.szesc;
drop table raf_manning.tab5; 

create view raf_manning.siedem as
select f.id, f.hydroid, f.n_value, f."Fraction",f.a,f.b,f.c,f.d,f.e,f.g, (f.g + f2."Fraction") as h  
	From raf_manning.tab6 as f
	left join raf_manning.tab6 as f2 On f.id = f2.id+7  and f.hydroid = f2.hydroid;

select * INTO raf_manning.tab7 from raf_manning.siedem;
drop view raf_manning.siedem;
drop table raf_manning.tab6; 

create view raf_manning.osiem as
select f.id, f.hydroid, f.n_value, f."Fraction",f.a,f.b,f.c,f.d,f.e,f.g,f.h, (f.h + f2."Fraction") as i  
	From raf_manning.tab7 as f
	left join raf_manning.tab7 as f2 On f.id = f2.id+8  and f.hydroid = f2.hydroid;

select * INTO raf_manning.tab8 from raf_manning.osiem;
drop view raf_manning.osiem;
drop table raf_manning.tab7; 

create view raf_manning.dziewiec as
select f.id, f.hydroid, f.n_value, f."Fraction",f.a,f.b,f.c,f.d,f.e,f.g,f.h,f.i, (f.i + f2."Fraction") as j  
	From raf_manning.tab8 as f
	left join raf_manning.tab8 as f2 On f.id = f2.id+9  and f.hydroid = f2.hydroid;

select * INTO raf_manning.tab9 from raf_manning.dziewiec;
drop view raf_manning.dziewiec;
drop table raf_manning.tab8;
 
create view raf_manning.dziesiec as
select f.id, f.hydroid, f.n_value, f."Fraction",f.a,f.b,f.c,f.d,f.e,f.g,f.h,f.i,f.j, (f.j + f2."Fraction") as k  
	From raf_manning.tab9 as f
	left join raf_manning.tab9 as f2 On f.id = f2.id+10  and f.hydroid = f2.hydroid;

select * INTO raf_manning.tab10 from raf_manning.dziesiec;
drop view raf_manning.dziesiec;
drop table raf_manning.tab9;

create view raf_manning.jedenascie as
select f.id, f.hydroid, f.n_value, f."Fraction",f.a,f.b,f.c,f.d,f.e,f.g,f.h,f.i,f.j,f.k, (f.k + f2."Fraction") as l  
	From raf_manning.tab10 as f
	left join raf_manning.tab10 as f2 On f.id = f2.id+11  and f.hydroid = f2.hydroid;

select * INTO raf_manning.tab11 from raf_manning.jedenascie;
drop view raf_manning.jedenascie;
drop table raf_manning.tab10;

create view raf_manning.dwanascie as
select f.id, f.hydroid, f.n_value, f."Fraction",f.a,f.b,f.c,f.d,f.e,f.g,f.h,f.i,f.j,f.k,f.l, (f.l + f2."Fraction") as m  
	From raf_manning.tab11 as f
	left join raf_manning.tab11 as f2 On f.id = f2.id+12  and f.hydroid = f2.hydroid;
 
select * INTO raf_manning.tab12 from raf_manning.dwanascie;
drop view raf_manning.dwanascie;
drop table raf_manning.tab11;

create view raf_manning.trzynascie as
select f.id, f.hydroid, f.n_value, f."Fraction",f.a,f.b,f.c,f.d,f.e,f.g,f.h,f.i,f.j,f.k,f.l,f.m, (f.m + f2."Fraction") as n  
	From raf_manning.tab12 as f
	left join raf_manning.tab12 as f2 On f.id = f2.id+13  and f.hydroid = f2.hydroid;

select * INTO raf_manning.tab13 from raf_manning.trzynascie;
drop view raf_manning.trzynascie;
drop table raf_manning.tab12;

create view raf_manning.czternascie as
select f.id, f.hydroid, f.n_value, f."Fraction",f.a,f.b,f.c,f.d,f.e,f.g,f.h,f.i,f.j,f.k,f.l,f.m,f.n, (f.n + f2."Fraction") as o  
	From raf_manning.tab13 as f
	left join raf_manning.tab13 as f2 On f.id = f2.id+14  and f.hydroid = f2.hydroid;

select * INTO raf_manning.tab14 from raf_manning.czternascie;
drop view raf_manning.czternascie;
drop table raf_manning.tab13;

create view raf_manning.pietnascie as
select f.id, f.hydroid, f.n_value, f."Fraction",f.a,f.b,f.c,f.d,f.e,f.g,f.h,f.i,f.j,f.k,f.l,f.m,f.n,f.o, (f.o + f2."Fraction") as p  
	From raf_manning.tab14 as f
	left join raf_manning.tab14 as f2 On f.id = f2.id+15  and f.hydroid = f2.hydroid;

select * INTO raf_manning.tab15 from raf_manning.pietnascie;
drop view raf_manning.pietnascie;
drop table raf_manning.tab14;

create view raf_manning.szesnascie as
select f.id, f.hydroid, f.n_value, f."Fraction",f.a,f.b,f.c,f.d,f.e,f.g,f.h,f.i,f.j,f.k,f.l,f.m,f.n,f.o,f.p, (f.p + f2."Fraction") as r  
	From raf_manning.tab15 as f
	left join raf_manning.tab15 as f2 On f.id = f2.id+16  and f.hydroid = f2.hydroid;

select * INTO raf_manning.tab16 from raf_manning.szesnascie;
drop view raf_manning.szesnascie;
drop table raf_manning.tab15;
 
create view raf_manning.siedemnascie as
select f.id, f.hydroid, f.n_value, f."Fraction",f.a,f.b,f.c,f.d,f.e,f.g,f.h,f.i,f.j,f.k,f.l,f.m,f.n,f.o,f.p,f.r, (f.r + f2."Fraction") as s  
	From raf_manning.tab16 as f
	left join raf_manning.tab16 as f2 On f.id = f2.id+17  and f.hydroid = f2.hydroid;

select * INTO raf_manning.tab17 from raf_manning.siedemnascie;
drop view raf_manning.siedemnascie;
drop table raf_manning.tab16;

create view raf_manning.osiemnascie as
select f.id, f.hydroid, f.n_value, f."Fraction",f.a,f.b,f.c,f.d,f.e,f.g,f.h,f.i,f.j,f.k,f.l,f.m,f.n,f.o,f.p,f.r,f.s, (f.s + f2."Fraction") as t  
	From raf_manning.tab17 as f
	left join raf_manning.tab17 as f2 On f.id = f2.id+18  and f.hydroid = f2.hydroid;

select * INTO raf_manning.tab18 from raf_manning.osiemnascie;
drop view raf_manning.osiemnascie;
drop table raf_manning.tab17;
 
create view raf_manning.dziewietnascie as
select f.id, f.hydroid, f.n_value, f."Fraction",f.a,f.b,f.c,f.d,f.e,f.g,f.h,f.i,f.j,f.k,f.l,f.m,f.n,f.o,f.p,f.r,f.s,f.t, (f.t + f2."Fraction") as u  
	From raf_manning.tab18 as f
	left join raf_manning.tab18 as f2 On f.id = f2.id+19  and f.hydroid = f2.hydroid;

select * INTO raf_manning.tab19 from raf_manning.dziewietnascie;
drop view raf_manning.dziewietnascie;
drop table raf_manning.tab18;
 
create view raf_manning.dwadziescia as
select f.id, f.hydroid, f.n_value, f."Fraction",f.a,f.b,f.c,f.d,f.e,f.g,f.h,f.i,f.j,f.k,f.l,f.m,f.n,f.o,f.p,f.r,f.s,f.t,f.u, (f.u + f2."Fraction") as w  
	From raf_manning.tab19 as f
	left join raf_manning.tab19 as f2 On f.id = f2.id+20  and f.hydroid = f2.hydroid;

select * INTO raf_manning.tab20 from raf_manning.dwadziescia;
drop view raf_manning.dwadziescia;
drop table raf_manning.tab19;

create view raf_manning.dwajed as
select f.id, f.hydroid, f.n_value, f."Fraction",f.a,f.b,f.c,f.d,f.e,f.g,f.h,f.i,f.j,f.k,f.l,f.m,f.n,f.o,f.p,f.r,f.s,f.t,f.u,f.w, (f.w + f2."Fraction") as y  
	From raf_manning.tab20 as f
	left join raf_manning.tab20 as f2 On f.id = f2.id+21  and f.hydroid = f2.hydroid;

select * INTO raf_manning.tab21 from raf_manning.dwajed;
drop view raf_manning.dwajed;
drop table raf_manning.tab20;

create view raf_manning.dwadwa as
select f.id, f.hydroid, f.n_value, f."Fraction",f.a,f.b,f.c,f.d,f.e,f.g,f.h,f.i,f.j,f.k,f.l,f.m,f.n,f.o,f.p,f.r,f.s,f.t,f.u,f.w,f.y, (f.y + f2."Fraction") as x  
	From raf_manning.tab21 as f
	left join raf_manning.tab21 as f2 On f.id = f2.id+22  and f.hydroid = f2.hydroid;

select * INTO raf_manning.tab22 from raf_manning.dwadwa;
drop view raf_manning.dwadwa;
drop table raf_manning.tab21;

create view raf_manning.dwatrzy as
select f.id, f.hydroid, f.n_value, f."Fraction",f.a,f.b,f.c,f.d,f.e,f.g,f.h,f.i,f.j,f.k,f.l,f.m,f.n,f.o,f.p,f.r,f.s,f.t,f.u,f.w,f.y,f.x, (f.x + f2."Fraction") as z  
	From raf_manning.tab22 as f
	left join raf_manning.tab22 as f2 On f.id = f2.id+23  and f.hydroid = f2.hydroid;

select * INTO raf_manning.tab23 from raf_manning.dwatrzy;
drop view raf_manning.dwatrzy;
drop table raf_manning.tab22;

create view raf_manning.dwacztery as
select f.id, f.hydroid, f.n_value, f."Fraction",f.a,f.b,f.c,f.d,f.e,f.g,f.h,f.i,f.j,f.k,f.l,f.m,f.n,f.o,f.p,f.r,f.s,f.t,f.u,f.w,f.y,f.x,f.z, (f.z + f2."Fraction") as aa  
	From raf_manning.tab23 as f
	left join raf_manning.tab23 as f2 On f.id = f2.id+24  and f.hydroid = f2.hydroid;

select * INTO raf_manning.tab24 from raf_manning.dwacztery;
drop view raf_manning.dwacztery;
drop table raf_manning.tab23;

create view raf_manning.dwapiec as
select f.id, f.hydroid, f.n_value, f."Fraction",f.a,f.b,f.c,f.d,f.e,f.g,f.h,f.i,f.j,f.k,f.l,f.m,f.n,f.o,f.p,f.r,f.s,f.t,f.u,f.w,f.y,f.x,f.z,f.aa, (f.aa + f2."Fraction") as ab  
	From raf_manning.tab24 as f
	left join raf_manning.tab24 as f2 On f.id = f2.id+25  and f.hydroid = f2.hydroid;

select * INTO raf_manning.tab25 from raf_manning.dwapiec;
drop view raf_manning.dwapiec;
drop table raf_manning.tab24;

create view raf_manning.dwaszesc as
select f.id, f.hydroid, f.n_value, f."Fraction",f.a,f.b,f.c,f.d,f.e,f.g,f.h,f.i,f.j,f.k,f.l,f.m,f.n,f.o,f.p,f.r,f.s,f.t,f.u,f.w,f.y,f.x,f.z,f.aa,f.ab, (f.ab + f2."Fraction") as ac  
	From raf_manning.tab25 as f
	left join raf_manning.tab25 as f2 On f.id = f2.id+26  and f.hydroid = f2.hydroid;

select * INTO raf_manning.tab26 from raf_manning.dwaszesc;
drop view raf_manning.dwaszesc;
drop table raf_manning.tab25;

create view raf_manning.dwasiedem as
select f.id, f.hydroid, f.n_value, f."Fraction",f.a,f.b,f.c,f.d,f.e,f.g,f.h,f.i,f.j,f.k,f.l,f.m,f.n,f.o,f.p,f.r,f.s,f.t,f.u,f.w,f.y,f.x,f.z,f.aa,f.ab,f.ac, (f.ac + f2."Fraction") as ad  
	From raf_manning.tab26 as f
	left join raf_manning.tab26 as f2 On f.id = f2.id+27  and f.hydroid = f2.hydroid;

select * INTO raf_manning.tab27 from raf_manning.dwasiedem;
drop view raf_manning.dwasiedem;
drop table raf_manning.tab26;

create view raf_manning.dwaosiem as
select f.id, f.hydroid, f.n_value, f."Fraction",f.a,f.b,f.c,f.d,f.e,f.g,f.h,f.i,f.j,f.k,f.l,f.m,f.n,f.o,f.p,f.r,f.s,f.t,f.u,f.w,f.y,f.x,f.z,f.aa,f.ab,f.ac,f.ad, (f.ad + f2."Fraction") as ae  
	From raf_manning.tab27 as f
	left join raf_manning.tab27 as f2 On f.id = f2.id+28  and f.hydroid = f2.hydroid;

select * INTO raf_manning.tab28 from raf_manning.dwaosiem;
drop view raf_manning.dwaosiem;
drop table raf_manning.tab27;

create view raf_manning.dwadziewiec as
select f.id, f.hydroid, f.n_value, f."Fraction",f.a,f.b,f.c,f.d,f.e,f.g,f.h,f.i,f.j,f.k,f.l,f.m,f.n,f.o,f.p,f.r,f.s,f.t,f.u,f.w,f.y,f.x,f.z,f.aa,f.ab,f.ac,f.ad,f.ae, (f.ae + f2."Fraction") as af  
	From raf_manning.tab28 as f
	left join raf_manning.tab28 as f2 On f.id = f2.id+29  and f.hydroid = f2.hydroid;

select * INTO raf_manning.tab29 from raf_manning.dwadziewiec;
drop view raf_manning.dwadziewiec;
drop table raf_manning.tab28;

create view raf_manning.trzydziesci as
select f.id, f.hydroid, f.n_value, f."Fraction",f.a,f.b,f.c,f.d,f.e,f.g,f.h,f.i,f.j,f.k,f.l,f.m,f.n,f.o,f.p,f.r,f.s,f.t,f.u,f.w,f.y,f.x,f.z,f.aa,f.ab,f.ac,f.ad,f.ae,f.af, (f.af + f2."Fraction") as ag  
	From raf_manning.tab29 as f
	left join raf_manning.tab29 as f2 On f.id = f2.id+30  and f.hydroid = f2.hydroid;

select * INTO raf_manning.tab30 from raf_manning.trzydziesci;
drop view raf_manning.trzydziesci;
drop table raf_manning.tab29;

create view raf_manning.trzydziescijed as
select f.id, f.hydroid, f.n_value, f."Fraction",f.a,f.b,f.c,f.d,f.e,f.g,f.h,f.i,f.j,f.k,f.l,f.m,f.n,f.o,f.p,f.r,f.s,f.t,f.u,f.w,f.y,f.x,f.z,f.aa,f.ab,f.ac,f.ad,f.ae,f.af,f.ag, (f.ag + f2."Fraction") as ah  
	From raf_manning.tab30 as f
	left join raf_manning.tab30 as f2 On f.id = f2.id+31  and f.hydroid = f2.hydroid;

select * INTO raf_manning.tab31 from raf_manning.trzydziescijed;
drop view raf_manning.trzydziescijed;
drop table raf_manning.tab30;

create view raf_manning.trzydziescidwa as
select f.id, f.hydroid, f.n_value, f."Fraction",f.a,f.b,f.c,f.d,f.e,f.g,f.h,f.i,f.j,f.k,f.l,f.m,f.n,f.o,f.p,f.r,f.s,f.t,f.u,f.w,f.y,f.x,f.z,f.aa,f.ab,f.ac,f.ad,f.ae,f.af,f.ag,f.ah, (f.ah + f2."Fraction") as ai  
	From raf_manning.tab31 as f
	left join raf_manning.tab31 as f2 On f.id = f2.id+32  and f.hydroid = f2.hydroid;

select * INTO raf_manning.tab32 from raf_manning.trzydziescidwa;
drop view raf_manning.trzydziescidwa;
drop table raf_manning.tab31;

create view raf_manning.trzydziescitrzy as
select f.id, f.hydroid, f.n_value, f."Fraction",f.a,f.b,f.c,f.d,f.e,f.g,f.h,f.i,f.j,f.k,f.l,f.m,f.n,f.o,f.p,f.r,f.s,f.t,f.u,f.w,f.y,f.x,f.z,f.aa,f.ab,f.ac,f.ad,f.ae,f.af,f.ag,f.ah,f.ai, (f.ai + f2."Fraction") as aj  
	From raf_manning.tab32 as f
	left join raf_manning.tab32 as f2 On f.id = f2.id+33  and f.hydroid = f2.hydroid;

select * INTO raf_manning.tab33 from raf_manning.trzydziescitrzy;
drop view raf_manning.trzydziescitrzy;
drop table raf_manning.tab32;

create view raf_manning.trzydziescicztery as
select f.id, f.hydroid, f.n_value, f."Fraction",f.a,f.b,f.c,f.d,f.e,f.g,f.h,f.i,f.j,f.k,f.l,f.m,f.n,f.o,f.p,f.r,f.s,f.t,f.u,f.w,f.y,f.x,f.z,f.aa,f.ab,f.ac,f.ad,f.ae,f.af,f.ag,f.ah,f.ai,f.aj, (f.aj + f2."Fraction") as ak  
	From raf_manning.tab33 as f
	left join raf_manning.tab33 as f2 On f.id = f2.id+34  and f.hydroid = f2.hydroid;

select * INTO raf_manning.tab34 from raf_manning.trzydziescicztery;
drop view raf_manning.trzydziescicztery;
drop table raf_manning.tab33;

create view raf_manning.trzydziescipiec as
select f.id, f.hydroid, f.n_value, f."Fraction",f.a,f.b,f.c,f.d,f.e,f.g,f.h,f.i,f.j,f.k,f.l,f.m,f.n,f.o,f.p,f.r,f.s,f.t,f.u,f.w,f.y,f.x,f.z,f.aa,f.ab,f.ac,f.ad,f.ae,f.af,f.ag,f.ah,f.ai,f.aj,f.ak, (f.ak + f2."Fraction") as al  
	From raf_manning.tab34 as f
	left join raf_manning.tab34 as f2 On f.id = f2.id+35  and f.hydroid = f2.hydroid;

select * INTO raf_manning.tab35 from raf_manning.trzydziescipiec;
drop view raf_manning.trzydziescipiec;
drop table raf_manning.tab34;

create view raf_manning.trzydziesciszesc as
select f.id, f.hydroid, f.n_value, f."Fraction",f.a,f.b,f.c,f.d,f.e,f.g,f.h,f.i,f.j,f.k,f.l,f.m,f.n,f.o,f.p,f.r,f.s,f.t,f.u,f.w,f.y,f.x,f.z,f.aa,f.ab,f.ac,f.ad,f.ae,f.af,f.ag,f.ah,f.ai,f.aj,f.ak,f.al, (f.al + f2."Fraction") as am  
	From raf_manning.tab35 as f
	left join raf_manning.tab35 as f2 On f.id = f2.id+36  and f.hydroid = f2.hydroid;

select * INTO raf_manning.tab36 from raf_manning.trzydziesciszesc;
drop view raf_manning.trzydziesciszesc;
drop table raf_manning.tab35;

create view raf_manning.trzydziescisiedem as
select f.id, f.hydroid, f.n_value, f."Fraction",f.a,f.b,f.c,f.d,f.e,f.g,f.h,f.i,f.j,f.k,f.l,f.m,f.n,f.o,f.p,f.r,f.s,f.t,f.u,f.w,f.y,f.x,f.z,f.aa,f.ab,f.ac,f.ad,f.ae,f.af,f.ag,f.ah,f.ai,f.aj,f.ak,f.al,f.am, (f.am + f2."Fraction") as an  
	From raf_manning.tab36 as f
	left join raf_manning.tab36 as f2 On f.id = f2.id+37  and f.hydroid = f2.hydroid;

select * INTO raf_manning.tab37 from raf_manning.trzydziescisiedem;
drop view raf_manning.trzydziescisiedem;
drop table raf_manning.tab36;

create view raf_manning.trzydziesciosiem as
select f.id, f.hydroid, f.n_value, f."Fraction",f.a,f.b,f.c,f.d,f.e,f.g,f.h,f.i,f.j,f.k,f.l,f.m,f.n,f.o,f.p,f.r,f.s,f.t,f.u,f.w,f.y,f.x,f.z,f.aa,f.ab,f.ac,f.ad,f.ae,f.af,f.ag,f.ah,f.ai,f.aj,f.ak,f.al,f.am,f.an, (f.an + f2."Fraction") as ao  
	From raf_manning.tab37 as f
	left join raf_manning.tab37 as f2 On f.id = f2.id+38  and f.hydroid = f2.hydroid;

select * INTO raf_manning.tab38 from raf_manning.trzydziesciosiem;
drop view raf_manning.trzydziesciosiem;
drop table raf_manning.tab37;

create view raf_manning.trzydziescidziew as
select f.id, f.hydroid, f.n_value, f."Fraction",f.a,f.b,f.c,f.d,f.e,f.g,f.h,f.i,f.j,f.k,f.l,f.m,f.n,f.o,f.p,f.r,f.s,f.t,f.u,f.w,f.y,f.x,f.z,f.aa,f.ab,f.ac,f.ad,f.ae,f.af,f.ag,f.ah,f.ai,f.aj,f.ak,f.al,f.am,f.an,f.ao, (f.ao + f2."Fraction") as ap  
	From raf_manning.tab38 as f
	left join raf_manning.tab38 as f2 On f.id = f2.id+39  and f.hydroid = f2.hydroid;

select * INTO raf_manning.tab39 from raf_manning.trzydziescidziew;
drop view raf_manning.trzydziescidziew;
drop table raf_manning.tab38;


create view raf_manning.czterdziesci as
select f.id, f.hydroid, f.n_value, f."Fraction",f.a,f.b,f.c,f.d,f.e,f.g,f.h,f.i,f.j,f.k,f.l,f.m,f.n,f.o,f.p,f.r,f.s,f.t,f.u,f.w,f.y,f.x,f.z,f.aa,f.ab,f.ac,f.ad,f.ae,f.af,f.ag,f.ah,f.ai,f.aj,f.ak,f.al,f.am,f.an,f.ao,f.ap, (f.ap + f2."Fraction") as ar  
	From raf_manning.tab39 as f
	left join raf_manning.tab39 as f2 On f.id = f2.id+40  and f.hydroid = f2.hydroid;

select * INTO raf_manning.tab40 from raf_manning.czterdziesci;
drop view raf_manning.czterdziesci;
drop table raf_manning.tab39;

create view raf_manning.czterdziescijeden as
select f.id, f.hydroid, f.n_value, f."Fraction",f.a,f.b,f.c,f.d,f.e,f.g,f.h,f.i,f.j,f.k,f.l,f.m,f.n,f.o,f.p,f.r,f.s,f.t,f.u,f.w,f.y,f.x,f.z,f.aa,f.ab,f.ac,f.ad,f.ae,f.af,f.ag,f.ah,f.ai,f.aj,f.ak,f.al,f.am,f.an,f.ao,f.ap,f.ar, (f.ar + f2."Fraction") as au  
	From raf_manning.tab40 as f
	left join raf_manning.tab40 as f2 On f.id = f2.id+41  and f.hydroid = f2.hydroid;

select * INTO raf_manning.tab41 from raf_manning.czterdziescijeden;
drop view raf_manning.czterdziescijeden;
drop table raf_manning.tab40;

create view raf_manning.czterdziescidwa as
select f.id, f.hydroid, f.n_value, f."Fraction",f.a,f.b,f.c,f.d,f.e,f.g,f.h,f.i,f.j,f.k,f.l,f.m,f.n,f.o,f.p,f.r,f.s,f.t,f.u,f.w,f.y,f.x,f.z,f.aa,f.ab,f.ac,f.ad,f.ae,f.af,f.ag,f.ah,f.ai,f.aj,f.ak,f.al,f.am,f.an,f.ao,f.ap,f.ar,f.au, (f.au + f2."Fraction") as aw  
	From raf_manning.tab41 as f
	left join raf_manning.tab41 as f2 On f.id = f2.id+42  and f.hydroid = f2.hydroid;

select * INTO raf_manning.tab42 from raf_manning.czterdziescidwa;
drop view raf_manning.czterdziescidwa;
drop table raf_manning.tab41;

create view raf_manning.czterdziescitrzy as
select f.id, f.hydroid, f.n_value, f."Fraction",f.a,f.b,f.c,f.d,f.e,f.g,f.h,f.i,f.j,f.k,f.l,f.m,f.n,f.o,f.p,f.r,f.s,f.t,f.u,f.w,f.y,f.x,f.z,f.aa,f.ab,f.ac,f.ad,f.ae,f.af,f.ag,f.ah,f.ai,f.aj,f.ak,f.al,f.am,f.an,f.ao,f.ap,f.ar,f.au,f.aw, (f.aw + f2."Fraction") as ay  
	From raf_manning.tab42 as f
	left join raf_manning.tab42 as f2 On f.id = f2.id+43  and f.hydroid = f2.hydroid;

select * INTO raf_manning.tab43 from raf_manning.czterdziescitrzy;
drop view raf_manning.czterdziescitrzy;
drop table raf_manning.tab42;

create view raf_manning.czterdziescicztery as
select f.id, f.hydroid, f.n_value, f."Fraction",f.a,f.b,f.c,f.d,f.e,f.g,f.h,f.i,f.j,f.k,f.l,f.m,f.n,f.o,f.p,f.r,f.s,f.t,f.u,f.w,f.y,f.x,f.z,f.aa,f.ab,f.ac,f.ad,f.ae,f.af,f.ag,f.ah,f.ai,f.aj,f.ak,f.al,f.am,f.an,f.ao,f.ap,f.ar,f.au,f.aw,f.ay, (f.ay + f2."Fraction") as ax  
	From raf_manning.tab43 as f
	left join raf_manning.tab43 as f2 On f.id = f2.id+44  and f.hydroid = f2.hydroid;

select * INTO raf_manning.tab44 from raf_manning.czterdziescicztery;
drop view raf_manning.czterdziescicztery;
drop table raf_manning.tab43;

create view raf_manning.czterdziescipiec as
select f.id, f.hydroid, f.n_value, f."Fraction",f.a,f.b,f.c,f.d,f.e,f.g,f.h,f.i,f.j,f.k,f.l,f.m,f.n,f.o,f.p,f.r,f.s,f.t,f.u,f.w,f.y,f.x,f.z,f.aa,f.ab,f.ac,f.ad,f.ae,f.af,f.ag,f.ah,f.ai,f.aj,f.ak,f.al,f.am,f.an,f.ao,f.ap,f.ar,f.au,f.aw,f.ay,f.ax, (f.ax + f2."Fraction") as az  
	From raf_manning.tab44 as f
	left join raf_manning.tab44 as f2 On f.id = f2.id+45  and f.hydroid = f2.hydroid;

select * INTO raf_manning.tab45 from raf_manning.czterdziescipiec;
drop view raf_manning.czterdziescipiec;
drop table raf_manning.tab44;

create view raf_manning.czterdziesciszesc as
select f.id, f.hydroid, f.n_value, f."Fraction",f.a,f.b,f.c,f.d,f.e,f.g,f.h,f.i,f.j,f.k,f.l,f.m,f.n,f.o,f.p,f.r,f.s,f.t,f.u,f.w,f.y,f.x,f.z,f.aa,f.ab,f.ac,f.ad,f.ae,f.af,f.ag,f.ah,f.ai,f.aj,f.ak,f.al,f.am,f.an,f.ao,f.ap,f.ar,f.au,f.aw,f.ay,f.ax,f.az, (f.az + f2."Fraction") as ba  
	From raf_manning.tab45 as f
	left join raf_manning.tab45 as f2 On f.id = f2.id+46  and f.hydroid = f2.hydroid;

select * INTO raf_manning.tab46 from raf_manning.czterdziesciszesc;
drop view raf_manning.czterdziesciszesc;
drop table raf_manning.tab45;

create view raf_manning.czterdziescisiedem as
select f.id, f.hydroid, f.n_value, f."Fraction",f.a,f.b,f.c,f.d,f.e,f.g,f.h,f.i,f.j,f.k,f.l,f.m,f.n,f.o,f.p,f.r,f.s,f.t,f.u,f.w,f.y,f.x,f.z,f.aa,f.ab,f.ac,f.ad,f.ae,f.af,f.ag,f.ah,f.ai,f.aj,f.ak,f.al,f.am,f.an,f.ao,f.ap,f.ar,f.au,f.aw,f.ay,f.ax,f.az,f.ba, (f.ba + f2."Fraction") as bb  
	From raf_manning.tab46 as f
	left join raf_manning.tab46 as f2 On f.id = f2.id+47  and f.hydroid = f2.hydroid;

select * INTO raf_manning.tab47 from raf_manning.czterdziescisiedem;
drop view raf_manning.czterdziescisiedem;
drop table raf_manning.tab46;

create view raf_manning.czterdziesciosiem as
select f.id, f.hydroid, f.n_value, f."Fraction",f.a,f.b,f.c,f.d,f.e,f.g,f.h,f.i,f.j,f.k,f.l,f.m,f.n,f.o,f.p,f.r,f.s,f.t,f.u,f.w,f.y,f.x,f.z,f.aa,f.ab,f.ac,f.ad,f.ae,f.af,f.ag,f.ah,f.ai,f.aj,f.ak,f.al,f.am,f.an,f.ao,f.ap,f.ar,f.au,f.aw,f.ay,f.ax,f.az,f.ba,f.bb, (f.bb + f2."Fraction") as bc  
	From raf_manning.tab47 as f
	left join raf_manning.tab47 as f2 On f.id = f2.id+48  and f.hydroid = f2.hydroid;

select * INTO raf_manning.tab48 from raf_manning.czterdziesciosiem;
drop view raf_manning.czterdziesciosiem;
drop table raf_manning.tab47;

create view raf_manning.czterdziescidziew as
select f.id, f.hydroid, f.n_value, f."Fraction",f.a,f.b,f.c,f.d,f.e,f.g,f.h,f.i,f.j,f.k,f.l,f.m,f.n,f.o,f.p,f.r,f.s,f.t,f.u,f.w,f.y,f.x,f.z,f.aa,f.ab,f.ac,f.ad,f.ae,f.af,f.ag,f.ah,f.ai,f.aj,f.ak,f.al,f.am,f.an,f.ao,f.ap,f.ar,f.au,f.aw,f.ay,f.ax,f.az,f.ba,f.bb,f.bc, (f.bc + f2."Fraction") as bd  
	From raf_manning.tab48 as f
	left join raf_manning.tab48 as f2 On f.id = f2.id+49  and f.hydroid = f2.hydroid;

select * INTO raf_manning.tab49 from raf_manning.czterdziescidziew;
drop view raf_manning.czterdziescidziew;
drop table raf_manning.tab48;

create view raf_manning.pisiat as
select f.id, f.hydroid, f.n_value, f."Fraction",f.a,f.b,f.c,f.d,f.e,f.g,f.h,f.i,f.j,f.k,f.l,f.m,f.n,f.o,f.p,f.r,f.s,f.t,f.u,f.w,f.y,f.x,f.z,f.aa,f.ab,f.ac,f.ad,f.ae,f.af,f.ag,f.ah,f.ai,f.aj,f.ak,f.al,f.am,f.an,f.ao,f.ap,f.ar,f.au,f.aw,f.ay,f.ax,f.az,f.ba,f.bb,f.bc,f.bd, (f.bd + f2."Fraction") as be  
	From raf_manning.tab49 as f
	left join raf_manning.tab49 as f2 On f.id = f2.id+50  and f.hydroid = f2.hydroid;

select * INTO raf_manning.tab50 from raf_manning.pisiat;
drop view raf_manning.pisiat;
drop table raf_manning.tab49;

create view raf_manning.pisiatjeden as
select f.id, f.hydroid, f.n_value, f."Fraction",f.a,f.b,f.c,f.d,f.e,f.g,f.h,f.i,f.j,f.k,f.l,f.m,f.n,f.o,f.p,f.r,f.s,f.t,f.u,f.w,f.y,f.x,f.z,f.aa,f.ab,f.ac,f.ad,f.ae,f.af,f.ag,f.ah,f.ai,f.aj,f.ak,f.al,f.am,f.an,f.ao,f.ap,f.ar,f.au,f.aw,f.ay,f.ax,f.az,f.ba,f.bb,f.bc,f.bd,f.be, (f.be + f2."Fraction") as bf  
	From raf_manning.tab50 as f
	left join raf_manning.tab50 as f2 On f.id = f2.id+51  and f.hydroid = f2.hydroid;

select * INTO raf_manning.tab51 from raf_manning.pisiatjeden;
drop view raf_manning.pisiatjeden;
drop table raf_manning.tab50;

create view raf_manning.pisiatdwa as
select f.id, f.hydroid, f.n_value, f."Fraction",f.a,f.b,f.c,f.d,f.e,f.g,f.h,f.i,f.j,f.k,f.l,f.m,f.n,f.o,f.p,f.r,f.s,f.t,f.u,f.w,f.y,f.x,f.z,f.aa,f.ab,f.ac,f.ad,f.ae,f.af,f.ag,f.ah,f.ai,f.aj,f.ak,f.al,f.am,f.an,f.ao,f.ap,f.ar,f.au,f.aw,f.ay,f.ax,f.az,f.ba,f.bb,f.bc,f.bd,f.be,f.bf, (f.bf + f2."Fraction") as bg  
	From raf_manning.tab51 as f
	left join raf_manning.tab51 as f2 On f.id = f2.id+52  and f.hydroid = f2.hydroid;

select * INTO raf_manning.tab52 from raf_manning.pisiatdwa;
drop view raf_manning.pisiatdwa;
drop table raf_manning.tab51;

create view raf_manning.pisiattrzy as
select f.id, f.hydroid, f.n_value, f."Fraction",f.a,f.b,f.c,f.d,f.e,f.g,f.h,f.i,f.j,f.k,f.l,f.m,f.n,f.o,f.p,f.r,f.s,f.t,f.u,f.w,f.y,f.x,f.z,f.aa,f.ab,f.ac,f.ad,f.ae,f.af,f.ag,f.ah,f.ai,f.aj,f.ak,f.al,f.am,f.an,f.ao,f.ap,f.ar,f.au,f.aw,f.ay,f.ax,f.az,f.ba,f.bb,f.bc,f.bd,f.be,f.bf,f.bg, (f.bg + f2."Fraction") as bh  
	From raf_manning.tab52 as f
	left join raf_manning.tab52 as f2 On f.id = f2.id+53  and f.hydroid = f2.hydroid;

select * INTO raf_manning.tab53 from raf_manning.pisiattrzy;
drop view raf_manning.pisiattrzy;
drop table raf_manning.tab52;

create view raf_manning.pisiatcztery as
select f.id, f.hydroid, f.n_value, f."Fraction",f.a,f.b,f.c,f.d,f.e,f.g,f.h,f.i,f.j,f.k,f.l,f.m,f.n,f.o,f.p,f.r,f.s,f.t,f.u,f.w,f.y,f.x,f.z,f.aa,f.ab,f.ac,f.ad,f.ae,f.af,f.ag,f.ah,f.ai,f.aj,f.ak,f.al,f.am,f.an,f.ao,f.ap,f.ar,f.au,f.aw,f.ay,f.ax,f.az,f.ba,f.bb,f.bc,f.bd,f.be,f.bf,f.bg,f.bh, (f.bh + f2."Fraction") as bi  
	From raf_manning.tab53 as f
	left join raf_manning.tab53 as f2 On f.id = f2.id+54  and f.hydroid = f2.hydroid;

select * INTO raf_manning.tab54 from raf_manning.pisiatcztery;
drop view raf_manning.pisiatcztery;
drop table raf_manning.tab53;

create view raf_manning.pisiatpiec as
select f.id, f.hydroid, f.n_value, f."Fraction",f.a,f.b,f.c,f.d,f.e,f.g,f.h,f.i,f.j,f.k,f.l,f.m,f.n,f.o,f.p,f.r,f.s,f.t,f.u,f.w,f.y,f.x,f.z,f.aa,f.ab,f.ac,f.ad,f.ae,f.af,f.ag,f.ah,f.ai,f.aj,f.ak,f.al,f.am,f.an,f.ao,f.ap,f.ar,f.au,f.aw,f.ay,f.ax,f.az,f.ba,f.bb,f.bc,f.bd,f.be,f.bf,f.bg,f.bh,f.bi, (f.bi + f2."Fraction") as bj  
	From raf_manning.tab54 as f
	left join raf_manning.tab54 as f2 On f.id = f2.id+55  and f.hydroid = f2.hydroid;

select * INTO raf_manning.tab55 from raf_manning.pisiatpiec;
drop view raf_manning.pisiatpiec;
drop table raf_manning.tab54;

create view raf_manning.pisiatszesc as
select f.id, f.hydroid, f.n_value, f."Fraction",f.a,f.b,f.c,f.d,f.e,f.g,f.h,f.i,f.j,f.k,f.l,f.m,f.n,f.o,f.p,f.r,f.s,f.t,f.u,f.w,f.y,f.x,f.z,f.aa,f.ab,f.ac,f.ad,f.ae,f.af,f.ag,f.ah,f.ai,f.aj,f.ak,f.al,f.am,f.an,f.ao,f.ap,f.ar,f.au,f.aw,f.ay,f.ax,f.az,f.ba,f.bb,f.bc,f.bd,f.be,f.bf,f.bg,f.bh,f.bi,f.bj, (f.bj + f2."Fraction") as bk  
	From raf_manning.tab55 as f
	left join raf_manning.tab55 as f2 On f.id = f2.id+56  and f.hydroid = f2.hydroid;

select * INTO raf_manning.tab56 from raf_manning.pisiatszesc;
drop view raf_manning.pisiatszesc;
drop table raf_manning.tab55;

create view raf_manning.pisiatsiedem as
select f.id, f.hydroid, f.n_value, f."Fraction",f.a,f.b,f.c,f.d,f.e,f.g,f.h,f.i,f.j,f.k,f.l,f.m,f.n,f.o,f.p,f.r,f.s,f.t,f.u,f.w,f.y,f.x,f.z,f.aa,f.ab,f.ac,f.ad,f.ae,f.af,f.ag,f.ah,f.ai,f.aj,f.ak,f.al,f.am,f.an,f.ao,f.ap,f.ar,f.au,f.aw,f.ay,f.ax,f.az,f.ba,f.bb,f.bc,f.bd,f.be,f.bf,f.bg,f.bh,f.bi,f.bj,f.bk, (f.bk + f2."Fraction") as bl  
	From raf_manning.tab56 as f
	left join raf_manning.tab56 as f2 On f.id = f2.id+57  and f.hydroid = f2.hydroid;

select * INTO raf_manning.tab57 from raf_manning.pisiatsiedem;
drop view raf_manning.pisiatsiedem;
drop table raf_manning.tab56;

create view raf_manning.pisiatosiem as
select f.id, f.hydroid, f.n_value, f."Fraction",f.a,f.b,f.c,f.d,f.e,f.g,f.h,f.i,f.j,f.k,f.l,f.m,f.n,f.o,f.p,f.r,f.s,f.t,f.u,f.w,f.y,f.x,f.z,f.aa,f.ab,f.ac,f.ad,f.ae,f.af,f.ag,f.ah,f.ai,f.aj,f.ak,f.al,f.am,f.an,f.ao,f.ap,f.ar,f.au,f.aw,f.ay,f.ax,f.az,f.ba,f.bb,f.bc,f.bd,f.be,f.bf,f.bg,f.bh,f.bi,f.bj,f.bk,f.bl, (f.bl + f2."Fraction") as bm  
	From raf_manning.tab57 as f
	left join raf_manning.tab57 as f2 On f.id = f2.id+58  and f.hydroid = f2.hydroid;

select * INTO raf_manning.tab58 from raf_manning.pisiatosiem;
drop view raf_manning.pisiatosiem;
drop table raf_manning.tab57;

create view raf_manning.pisiatdziew as
select f.id, f.hydroid, f.n_value, f."Fraction",f.a,f.b,f.c,f.d,f.e,f.g,f.h,f.i,f.j,f.k,f.l,f.m,f.n,f.o,f.p,f.r,f.s,f.t,f.u,f.w,f.y,f.x,f.z,f.aa,f.ab,f.ac,f.ad,f.ae,f.af,f.ag,f.ah,f.ai,f.aj,f.ak,f.al,f.am,f.an,f.ao,f.ap,f.ar,f.au,f.aw,f.ay,f.ax,f.az,f.ba,f.bb,f.bc,f.bd,f.be,f.bf,f.bg,f.bh,f.bi,f.bj,f.bk,f.bl,f.bm, (f.bm + f2."Fraction") as bn  
	From raf_manning.tab58 as f
	left join raf_manning.tab58 as f2 On f.id = f2.id+59  and f.hydroid = f2.hydroid;

select * INTO raf_manning.tab59 from raf_manning.pisiatdziew;
drop view raf_manning.pisiatdziew;
drop table raf_manning.tab58;

create view raf_manning.szescdziesiat as
select f.id, f.hydroid, f.n_value, f."Fraction",f.a,f.b,f.c,f.d,f.e,f.g,f.h,f.i,f.j,f.k,f.l,f.m,f.n,f.o,f.p,f.r,f.s,f.t,f.u,f.w,f.y,f.x,f.z,f.aa,f.ab,f.ac,f.ad,f.ae,f.af,f.ag,f.ah,f.ai,f.aj,f.ak,f.al,f.am,f.an,f.ao,f.ap,f.ar,f.au,f.aw,f.ay,f.ax,f.az,f.ba,f.bb,f.bc,f.bd,f.be,f.bf,f.bg,f.bh,f.bi,f.bj,f.bk,f.bl,f.bm,f.bn, (f.bn + f2."Fraction") as bo  
	From raf_manning.tab59 as f
	left join raf_manning.tab59 as f2 On f.id = f2.id+60  and f.hydroid = f2.hydroid;

select * INTO raf_manning.tab60 from raf_manning.szescdziesiat;
drop view raf_manning.szescdziesiat;
drop table raf_manning.tab59;






-------------------------------------------------------------------------------------------------------------------------------------------------------------
-- wyciagniecie pierwszych wartosci z kaskady jako wartosci prawidlowej i przypisanie jej do każdego rekordu w danej kolumnie kaskady dla danego przekroju --
-------------------------------------------------------------------------------------------------------------------------------------------------------------
create view raf_manning.first as
select  id, hydroid, n_value, 
	first_value("Fraction") over (partition by hydroid, "Fraction" is null order by id) as poczatek,
	first_value(a) over (partition by hydroid, a is null order by id) as a,
	first_value(b) over (partition by hydroid, b is null order by id) as b,
	first_value(c) over (partition by hydroid, c is null order by id) as c,
	first_value(d) over (partition by hydroid, d is null order by id) as d,
	first_value(e) over (partition by hydroid, e is null order by id) as e,
	first_value(g) over (partition by hydroid, g is null order by id) as g,
	first_value(h) over (partition by hydroid, h is null order by id) as h,
	first_value(i) over (partition by hydroid, i is null order by id) as i,
	first_value(j) over (partition by hydroid, j is null order by id) as j,
	first_value(k) over (partition by hydroid, k is null order by id) as k,
	first_value(l) over (partition by hydroid, l is null order by id) as l,
	first_value(m) over (partition by hydroid, m is null order by id) as m,
	first_value(n) over (partition by hydroid, n is null order by id) as n,
	first_value(o) over (partition by hydroid, o is null order by id) as o,
	first_value(p) over (partition by hydroid, p is null order by id) as p,
	first_value(r) over (partition by hydroid, r is null order by id) as r,
	first_value(s) over (partition by hydroid, s is null order by id) as s,
	first_value(t) over (partition by hydroid, t is null order by id) as t,
	first_value(u) over (partition by hydroid, u is null order by id) as u,
	first_value(w) over (partition by hydroid, w is null order by id) as w,
	first_value(y) over (partition by hydroid, y is null order by id) as y,
	first_value(x) over (partition by hydroid, x is null order by id) as x,
	first_value(z) over (partition by hydroid, z is null order by id) as z,

	first_value(aa) over (partition by hydroid, aa is null order by id) as aa,
	first_value(ab) over (partition by hydroid, ab is null order by id) as ab,
	first_value(ac) over (partition by hydroid, ac is null order by id) as ac,
	first_value(ad) over (partition by hydroid, ad is null order by id) as ad,
	first_value(ae) over (partition by hydroid, ae is null order by id) as ae,
	first_value(af) over (partition by hydroid, af is null order by id) as af,
	first_value(ag) over (partition by hydroid, ag is null order by id) as ag,
	first_value(ah) over (partition by hydroid, ah is null order by id) as ah,
	first_value(ai) over (partition by hydroid, ai is null order by id) as ai,
	first_value(aj) over (partition by hydroid, aj is null order by id) as aj,
	first_value(ak) over (partition by hydroid, ak is null order by id) as ak,
	first_value(al) over (partition by hydroid, al is null order by id) as al,
	first_value(am) over (partition by hydroid, am is null order by id) as am,
	first_value(an) over (partition by hydroid, an is null order by id) as an,
	first_value(ao) over (partition by hydroid, ao is null order by id) as ao,
	first_value(ap) over (partition by hydroid, ap is null order by id) as ap,
	first_value(ar) over (partition by hydroid, ar is null order by id) as ar,
	first_value(au) over (partition by hydroid, au is null order by id) as au,
	first_value(aw) over (partition by hydroid, aw is null order by id) as aw,
	first_value(ay) over (partition by hydroid, ay is null order by id) as ay,
	first_value(ax) over (partition by hydroid, ax is null order by id) as ax,
	first_value(az) over (partition by hydroid, az is null order by id) as az,

	first_value(ba) over (partition by hydroid, ba is null order by id) as ba,
	first_value(bb) over (partition by hydroid, bb is null order by id) as bb,
	first_value(bc) over (partition by hydroid, bc is null order by id) as bc,
	first_value(bd) over (partition by hydroid, bd is null order by id) as bd,
	first_value(be) over (partition by hydroid, be is null order by id) as be,
	first_value(bf) over (partition by hydroid, bf is null order by id) as bf,
	first_value(bg) over (partition by hydroid, bg is null order by id) as bg,
	first_value(bh) over (partition by hydroid, bh is null order by id) as bh,
	first_value(bi) over (partition by hydroid, bi is null order by id) as bi,
	first_value(bj) over (partition by hydroid, bj is null order by id) as bj,
	first_value(bk) over (partition by hydroid, bk is null order by id) as bk,
	first_value(bl) over (partition by hydroid, bl is null order by id) as bl,
	first_value(bm) over (partition by hydroid, bm is null order by id) as bm,
	first_value(bn) over (partition by hydroid, bn is null order by id) as bn,
	first_value(bo) over (partition by hydroid, bo is null order by id) as bo
	

from raf_manning.tab60 order by id;

select * INTO raf_manning.tab_f1 from raf_manning.first;
drop view raf_manning.first;

-------------------------------------------------------------------------------------------------------------------------------------------------
-- wyciagniecie ostatniego wiersza kaskady i przypisanie go do kazdego wiersza w poszczegolnym przekroju oraz dodanie wartosci poczatkowej "0" --
-------------------------------------------------------------------------------------------------------------------------------------------------

create view raf_manning.tab2 as
select id, hydroid, n_value, hydroid * 0 as zero, 
	last_value(poczatek) over (partition by hydroid) as poczatek,
	last_value(a) over (partition by hydroid) as a,
	last_value(b) over (partition by hydroid) as b,
	last_value(c) over (partition by hydroid) as c,
	last_value(d) over (partition by hydroid) as d,
	last_value(e) over (partition by hydroid) as e,
	last_value(g) over (partition by hydroid) as g 
from raf_manning.tab_f1;

--------------------------------------
-- grupowanie przekrojow po hydroid --
--------------------------------------

create view raf_manning.tab3 as
select hydroid, zero, poczatek,a,b,c,d,e,g from raf_manning.tab2
group by hydroid, zero, poczatek,a,b,c,d,e,g
order by hydroid;

--------------------------
-- transpozycja wierszy --
--------------------------

create view raf_manning.tab4 as
SELECT hydroid,
       unnest(array[zero,poczatek, a, b, c, d, e, g]) AS "Fraction"
FROM raf_manning.tab3 
ORDER BY hydroid;

-----------------------------------------------------------------
-- wyeliminowanie ostatniej wartosci oraz dodanie kolumny "id" --
-----------------------------------------------------------------

select * INTO raf_manning.got from raf_manning.tab4 where "Fraction" < 99.99;
alter table raf_manning.got add column id serial PRIMARY KEY;

----------------------------------------------------------------------------------------------------------------------------------------
-- przeliczenie wartosci procentowej na dziesietna oraz join wartosci wspl. manninga. Stworzenie finalnej tabeli i zmiana nazw kolumn --
----------------------------------------------------------------------------------------------------------------------------------------

create view raf_manning.tab5 as 
select a.id, a.hydroid, a."Fraction"/100 as "Fraction" , b.n_value from raf_manning.got as a left join raf_manning.tab60 as b on a.id = b.id;
select * INTO raf_manning."Manning" from raf_manning.tab5;
Alter table raf_manning."Manning" rename column hydroid to "XS2DID"; 
alter table raf_manning."Manning" rename column n_value to "N_Value";

--------------------------------------------
-- usuniecie tabel i widokow tymczasowych --
--------------------------------------------

DROP TABLE raf_manning.got, raf_manning.przekroje_inter, raf_manning.roznica, raf_manning.tab_f1 CASCADE;
----------------------------