WITH distances AS
    (SELECT
        "StorageID",
        ST_Distance(sa.geom, ST_StartPoint(sac.geom)) AS usdist,
        ST_Distance(sa.geom, ST_EndPoint(sac.geom)) AS dsdist
    FROM
        "Pasleka"."StorageAreas" AS sa,
        "Pasleka"."SAConnections" AS sac)
UPDATE "Pasleka"."SAConnections"
SET
    "USSA" = (SELECT "StorageID" FROM distances ORDER BY usdist LIMIT 1),
    "DSSA" = (SELECT "StorageID" FROM distances ORDER BY dsdist LIMIT 1)