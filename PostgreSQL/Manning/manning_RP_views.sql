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
