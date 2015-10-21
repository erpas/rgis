WITH cpnt AS
    (SELECT
        geom,
        "LateralSID",
        "RiverCode",
        "ReachCode"
    FROM
        (SELECT
            ST_ClosestPoint(sc.geom, ST_StartPoint(ls.geom))::geometry(POINT, 2180) AS geom,
            ls."LateralSID",
            sc."RiverCode",
            sc."ReachCode",
            RANK() OVER (PARTITION BY ls."LateralSID" ORDER BY ST_Distance(sc.geom, ST_StartPoint(ls.geom))) AS rnk
        FROM
            "Dzierzgon"."StreamCenterlines" AS sc,
            "Dzierzgon"."LateralStructures" AS ls
        ORDER BY
            ls."LateralSID") AS pnt
    WHERE
        rnk = 1)

UPDATE "Dzierzgon"."LateralStructures" AS ls
SET
   "RiverCode" = cpnt."RiverCode",
   "ReachCode" = cpnt."ReachCode"
FROM
    cpnt
WHERE
   ls."LateralSID" = cpnt."LateralSID";



WITH cpnt AS
    (SELECT
        geom,
        "LateralSID",
        "ReachCode",
         ("ToSta"-"FromSta") AS "Length"
    FROM
        (SELECT
            ST_ClosestPoint(sc.geom, ST_StartPoint(ls.geom))::geometry(POINT, 2180) AS geom,
            ls."LateralSID",
            sc."ReachCode",
            sc."FromSta",
            sc."ToSta",
            RANK() OVER (PARTITION BY ls."LateralSID" ORDER BY ST_Distance(sc.geom, ST_StartPoint(ls.geom))) AS rnk
        FROM
            "Dzierzgon"."StreamCenterlines" AS sc,
            "Dzierzgon"."LateralStructures" AS ls
        ORDER BY
            ls."LateralSID") AS pnt
    WHERE
        rnk = 1)

UPDATE "Dzierzgon"."LateralStructures" AS ls
SET
   "Station" = cpnt."Length"*(1-ST_Line_Locate_Point(sc.geom, cpnt.geom))
FROM
    cpnt,
    "Dzierzgon"."StreamCenterlines" AS sc
WHERE
    ls."LateralSID" = cpnt."LateralSID" AND
    sc."ReachCode" = cpnt."ReachCode";