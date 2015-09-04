.. _typicalWorkflowRas1d:

--------------------------------------------------
Typical Workflow: Create 1d HEC-RAS Geometry Model
--------------------------------------------------

1. Create source geometry of the model:
---------------------------------------

* Create empty river database tables for 1d HEC-RAS model or
* Import the model geometry from existing layers loaded into a QGIS project

Dalej będzie po polsku, bo to tylko dla nas:

Absolutnie konieczne jest włożenie geometrii do 2 tabel:

* ``riverCenterlines`` (linestring) (a może zwyczajnie ``rivers``?)::

    ("rivid", "serial primary key"), -- proponuję zastapić hydroid identyfikatorem rzeki
    ("rivercode", "text"), -- wymagany z palca
    ("reachcode", "text"), -- wymagany z palca
    ("fromnode", "integer"),
    ("tonode", "integer"),
    ("reachlen", "double precision"), -- długość odcinka
    ("fromsta", "double precision"), -- kilometraż początku: wymagany z palca
    ("tosta", "double precision"), -- km końca: z palca
    ("notes", "text")

* ``xscutlines`` (linestring)::

    ("xsid", "serial primary key"), -- proponuję zastapię hydroid identyfikatorem przekroju
    ("rivid", "integer"),
    ("station", "double precision"),
    ("leftbank", "double precision"),
    ("rightbank", "double precision"),
    ("leftlen", "double precision"),
    ("chanlen", "double precision"),
    ("rightlen", "double precision"),
    ("name", "text"),
    ("description", "text")


Topologia sieci
---------------

* wypełnienie tabeli ``nodes`` (NodesTable) --- punktu początku i końca rzeki z nadanym identyfikatorem
* nadać stacje początkom i końcm odcinków rzek --- z palca?

Dane przekrojów poprzecznych
----------------------------

Następnie wypełniamy atrybuty tabeli ``xscutlines``:

* ``rivid`` poleceniem ``River/Reach Names`` --- z warunku przecięcia się linii rzeki z przekrojem
* ``station`` poleceniem ``Stationing``::

    stationing = fromsta + m * reachlen

    gdzie:
    m = frakcja długości odcinka rzeki w punkcie przecięcia z xscutline

* ``leftbank``, ``rightbank`` poleceniem ``Bank Stations`` - znajdujemy punkty przecięcia xscutline z  liniami brzegów i odczytujemy ich odpowiadające im frakcje odległości wzdłuż xscutline

* ``leftlen``, ``chanlen``, ``rightlen`` poleceniem ``Downstream Reach Lengths``. Znaleźć xsid przekroju poniżej. Obliczyć frakcje punktów przecięcia przekroju i odpowiednich linii przepływu i na ich podstawie obliczyć odległości między przekrojami




