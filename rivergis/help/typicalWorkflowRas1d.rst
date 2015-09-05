.. _typicalWorkflowRas1d:

--------------------------------------------------
Typical Workflow: Create 1d HEC-RAS Geometry Model
--------------------------------------------------

Utworzenie bądź import geometrii źródłowej
------------------------------------------

* Create empty river database tables for 1d HEC-RAS model or
* Import the model geometry from existing layers loaded into a QGIS project

Dalej będzie po polsku, bo to tylko dla nas:

Absolutnie konieczne jest włożenie geometrii do 2 tabel:

* ``RiverCenterlines`` (linestring) (a może zwyczajnie ``rivers``?)::

    ('"RiverId"', "serial primary key"), -- proponuję zastapić hydroid identyfikatorem rzeki
    ('"RiverCode"', "text"), -- wymagany z palca
    ('"ReachCode"', "text"), -- wymagany z palca
    ('"FromNode"', "integer"),
    ('"ToNode"', "integer"),
    ('"ReachLen"', "double precision"), -- długość odcinka
    ('"FromSta"', "double precision"), -- kilometraż początku: wymagany z palca
    ('"ToSta"', "double precision"), -- km końca: z palca
    ('"Notes"', "text")

* ``XsCutlines`` (linestring)::

    ('"XsecId"', "serial primary key"), -- proponuję zastapię hydroid identyfikatorem przekroju
    ('"RiverId"', "integer"),
    ('"Station"', "double precision"), -- kilometraż przekroju
    ('"LeftBank"', "double precision"),
    ('"RightBank"', "double precision"),
    ('"LeftLen"', "double precision"),
    ('"ChanLen"', "double precision"),
    ('"RightLen"', "double precision"),
    ('"Name"', "text"),
    ('"Description"', "text")

Inne dane są opcjonalne.

Topologia sieci
---------------

* wypełnienie tabeli ``NodesTable``, punktów początku (FromNode) i końca rzeki (ToNode) z nadanym identyfikatorem
* nadać stacje początkom i końcom odcinków rzek --- należy przypomnieć użytkownikowi, że trzeba to zrobić z palca?

Tabela ``NodesTable`` (point)::

    ('"NodeId"', "serial primary key"),
    ('"X"', "double precision"), -- wspólrzędna geodezyjna x
    ('"Y"', "double precision") -- wspólrzędna geodezyjna y


Dane przekrojów poprzecznych
----------------------------

Następnie wypełniamy atrybuty tabeli ``XsCutlines``:

* ``RiverId`` poleceniem ``River/Reach Names`` --- z warunku przecięcia się linii rzeki z przekrojem
* ``Station`` poleceniem ``Stationing``::

    Station = FromSta + m * ReachLen

    gdzie:
    m = frakcja długości odcinka rzeki w punkcie przecięcia z XsCutline

* ``LeftBank``, ``RightBank`` poleceniem ``Bank Stations`` - znajdujemy punkty przecięcia XsCutline z  liniami brzegów i odczytujemy odpowiadające im frakcje odległości wzdłuż XsCutline

* ``LeftLen``, ``ChanLen``, ``RightLen`` poleceniem ``Downstream Reach Lengths``. Znaleźć ``XsecId`` przekroju poniżej. Obliczyć frakcje punktów przecięcia przekroju i odpowiednich linii przepływu i na ich podstawie obliczyć odległości między przekrojami

Próbkowanie DEM w przekroju
***************************

W `Issues pisałem <http://sr101537.imgw.ad:81/rpasiok/rgroup/issues/12>`_  o próbkowaniu DEMa wzdłuż przekroju i że jest to jedna z kosztowniejszych czasowo analiz, więc warto byłoby zachować jej wynik w tabeli. Zaproponowałem następującą strukturę::

    ('"PtId"', 'bigserial primary key'), -- id punktu
    ('"XsecId"', 'integer'), -- identyfikator przekroju, do którego punkt należy
    ('"Station"', 'double precision'), -- odległość punktu od początku przekroju [m]
    ('"Elevation"', 'double precision'), -- wysokość [mnpm]
    ('"CoverCode"', 'text'), -- kod pokrycia terenu
    ('"SrcId"', 'integer'), -- kod źródła danych (gid)
    ('"Notes"', 'text'), -- miejsce na inne uwagi
    ('"geom"', 'geometry(Point, SRID)') -- położenie punktu we współrzędnych geodezyjnych

Proponuję, aby gęstość próbkowania rastra DEM przyjąć jako równą rozdzielczości DEM. Dla dużych rzek będziemy mieli wówczas mnóstwo punktów w każdym przekroju i należałoby pomyśleć o odfiltrowaniu punktów nieznaczących (zob. `Issues <http://sr101537.imgw.ad:81/rpasiok/rgroup/issues/16>`_). Jest kwestia, kiedy to robić. Ja skłaniam się do tego, aby robić to od razu po próbkowaniu DEMa, ale wiąże się z tym kilka dalszych spraw.

Sprawdziłem możliwości importu do HEC-RAS większej ilości punktów niż 500. Próba się powiodła i jest możliwość filtrowania przekrojów później w samych HEC-RASie. Możemy się zastanowić, czy chcemy wyposażyć wtyczkę w filtrowanie czy nie.

Jeśli będziemy filtrować, to po odfiltrowaniu punktów nieznaczących może się okazać, że wyleciał nam np. punkt brzegu. Nie wszystkie elementy przekroju muszą byc przypisane do konkretnego istniejącego punktu przekroju, ale brzegi akurat muszą (w Mike'u jest podobnie: marker stawiamy w punkcie przekroju). Poza tym, użytkownik zawsze może zmienić położenie linii brzegu po wykonaniu innych analiz i wówczas musimy mieć możliwość dołożenia do przekroju punktu w określonym x (Station) - jego wysokość byłaby interpolowana na podstawie sąsiadów.

Oto tabela danych przekroju z informacją, czy muszą być umieszczone w istniejącym punkcie:

==================      ==============      ==================
rodzaj danych           HEC-RAS wymaga      Mike wymaga
==================      ==============      ==================
brzeg/marker 4 i 5      tak                 tak
wał/marker 1 i 3        nie                 tak
zmiana Manninga         tak                 tak
pole jałowe             nie                 brak odpowiednika
przeszkoda              nie                 brak odpowiednika
==================      ==============      ==================



Inne dane geometryczne
----------------------

Blocked Obstructions
********************

.. figure:: img/temp_normal_blocked_obstructions.png
   :align: right

.. figure:: img/temp_multiple_blocked_obstructions.png
   :align: right

Mamy dwa typy przeszkód:

* normalne: podajemy strone po której znajduje się przeszkoda, do (od) jakiej odległości x przekrój jest zablokowany i do jakiej wysokości (górny rysunek)
* multiple: podajemy dowolną ilość bloków opisanych: xstart, xend i wysokość (dolny rysunek)

Proponuję przecinać poligony przeszkód przekrojami i wypełniać następującą tabelę ``BlockedPositions`` (bez geometrii)

    ('"id"', "serial primary key"),
    ('"XsecId"', "integer"), -- którego przekroju dotyczy
    ('"BegFrac"', "double precision"), -- frakcja długosci przekroju dla początku przeszkody
    ('"EndFrac"', "double precision"), -- frakcja końca przeszkody
    ('"Elevation"', "double precision"), -- wysokość przeszkody (rzędna npm)


Ineffective Flow Areas
**********************

Podobnie jak w przypadku blocked obstructions mamy dwa typy pól jałowego przepływu, czyli takich obszarów, które są zalewane, ale prędkość przepływu wzdłuż głównego kierunku przepływu jest zbliżona do zera:

* normalne: podajemy strone po której znajduje się pole jałowe, do (od) jakiej odległości x przekrój jest jałowy i do jakiej wysokości
* multiple: podajemy dowolną ilość bloków opisanych: xstart, xend i wysokość

Tabela pól jałowych ``IneffectivePositions`` (bez geometrii)::

    ('"id"', "serial primary key"),
    ('"XsecId"', "integer"), -- którego przekroju dotyczy
    ('"BegFrac"', "double precision"), -- frakcja długosci przekroju dla początku pola
    ('"EndFrac"', "double precision"), -- frakcja końca pola
    ('"Elevation"', "double precision"), -- wysokość pola (rzędna npm)


Manning's n
***********

Tabela zmian użytkowania i szorstkości ``Manning`` (bez geometrii)::

    ('"id"', "serial primary key"),
    ('"XsecId"', "integer"), -- którego przekroju dotyczy
    ('"Fraction"', "double precision"), -- frakcja długosci przekroju dla początku pola
    ('"N_Value"', "double precision"), -- współczynnik Manninga


Wały
****

Tabela wałów ``LeveePositions`` (bez geometrii)::

    ('"LeveeId"', "serial primary key"),
    ('"XsecId"', "integer"), -- którego przekroju dotyczy
    ('"Fraction"', "double precision"), -- frakcja długosci przekroju dla początku pola
    ('"Elevation"', "double precision"), -- wysokość wału