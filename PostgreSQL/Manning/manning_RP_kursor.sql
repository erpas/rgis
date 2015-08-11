create or replace function kursor() returns refcursor as $$
declare
kur refcursor := 'xxx';
begin 
open kur for select * from raf_manning.tab20;
return kur;
end;
$$ language 'plpgsql';

begin;
select kursor();
fetch all xxx; 


