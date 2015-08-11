-- create view raf_manning.first as
-- select  hydroid, n_value, 
-- 	first_value(a) over (partition by hydroid, a is null order by id) as a,
-- 	first_value(b) over (partition by hydroid, b is null order by id) as b,
-- 	first_value(c) over (partition by hydroid, c is null order by id) as c,
-- 	first_value(d) over (partition by hydroid, d is null order by id) as d,
-- 	first_value(e) over (partition by hydroid, e is null order by id) as e,
-- 	first_value(g) over (partition by hydroid, g is null order by id) as g,
-- 	first_value(h) over (partition by hydroid, h is null order by id) as h,
-- 	first_value(i) over (partition by hydroid, i is null order by id) as i,
-- 	first_value(j) over (partition by hydroid, j is null order by id) as j,
-- 	first_value(k) over (partition by hydroid, k is null order by id) as k,
-- 	first_value(l) over (partition by hydroid, l is null order by id) as l,
-- 	first_value(m) over (partition by hydroid, m is null order by id) as m,
-- 	first_value(n) over (partition by hydroid, n is null order by id) as n,
-- 	first_value(o) over (partition by hydroid, o is null order by id) as o,
-- 	first_value(p) over (partition by hydroid, p is null order by id) as p,
-- 	first_value(r) over (partition by hydroid, r is null order by id) as r,
-- 	first_value(s) over (partition by hydroid, s is null order by id) as s,
-- 	first_value(t) over (partition by hydroid, t is null order by id) as t,
-- 	first_value(u) over (partition by hydroid, u is null order by id) as u,
-- 	first_value(w) over (partition by hydroid, w is null order by id) as w,
-- 	first_value(y) over (partition by hydroid, y is null order by id) as y,
-- 	first_value(x) over (partition by hydroid, x is null order by id) as x,
-- 	first_value(z) over (partition by hydroid, z is null order by id) as z,
-- 	first_value(aa) over (partition by hydroid, aa is null order by id) as aa,
-- 	first_value(ab) over (partition by hydroid, ab is null order by id) as ab,
-- 	first_value(ac) over (partition by hydroid, ac is null order by id) as ac,
-- 	first_value(ad) over (partition by hydroid, ad is null order by id) as ad,
-- 	first_value(ae) over (partition by hydroid, ae is null order by id) as ae,
-- 	first_value(af) over (partition by hydroid, af is null order by id) as af,
-- 	first_value(ag) over (partition by hydroid, ag is null order by id) as ag
-- from raf_manning.tab30 order by id;
-- 
-- select * INTO raf_manning.tab_f1 from raf_manning.first;
-- drop view raf_manning.first;

-- create view raf_manning.tab2 as
-- select hydroid, n_value, hydroid * 0 as zero, 
-- 	last_value(a) over (partition by hydroid) as a,
-- 	last_value(b) over (partition by hydroid) as b,
-- 	last_value(c) over (partition by hydroid) as c 
-- from raf_manning.tab_f1;

create view raf_manning.tab3 as
select * from raf_manning.tab2
group by hydroid,n_value, zero, a,b,c
order by hydroid

-- create view raf_manning.tab4 as
-- SELECT hydroid,
--        unnest(array[zero,a, b, c]) AS "Fraction"
-- FROM raf_manning.tab3 
-- ORDER BY hydroid;

--select * from raf_manning.got where "Fraction" < 99.99