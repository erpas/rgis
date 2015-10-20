SELECT
    geom,
    "LateralSID"
FROM
    (SELECT
        ST_ClosestPoint(sc.geom, ST_StartPoint(ls.geom))::geometry(POINT, 2180) AS geom,
        ls."LateralSID",
        RANK() OVER (PARTITION BY ls."LateralSID" ORDER BY ST_Distance(sc.geom, ST_StartPoint(ls.geom))) AS rnk
    FROM
        "Dzierzgon"."StreamCenterlines" AS sc,
        "Dzierzgon"."LateralStructures" AS ls
    ORDER BY
        ls."LateralSID") AS cp
WHERE
    rnk = 1;