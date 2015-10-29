------------------------------------------------------------------------------------------------------------------------
-- Intersect of land use layer with cross section layer  --
------------------------------------------------------------------------------------------------------------------------
SELECT
    "LUID",
    "LUCode",
    "N_Value",
    (ST_Dump(geom)).geom::geometry(POLYGON, 2180) AS geom
INTO
    "Dzierzgon".ludump
FROM
    "Dzierzgon"."LanduseAreas";

CREATE INDEX idx_ludump ON "Dzierzgon".ludump USING gist(geom);
------------------------------------------------------------------------------------------------------------------------
WITH inter_xs_dump AS
    (SELECT
        xs."XsecID",
        lud."N_Value",
        lud."LUCode",
        (ST_Dump(ST_Intersection(lud.geom, xs.geom))).geom::geometry(LINESTRING, 2180) AS geom
    FROM
        "Dzierzgon".ludump AS lud,
        "Dzierzgon"."XSCutLines" AS xs
    WHERE
        ST_Intersects(lud.geom, xs.geom)),
    single_line AS
    (SELECT
        "XsecID",
        (ST_Dump(xs.geom)).geom::geometry(LINESTRING, 2180) AS geom
    FROM
        "Dzierzgon"."XSCutLines" AS xs),
    shiftpoints AS
    (SELECT
        "XsecID",
        "N_Value",
        "LUCode",
        ST_Line_Interpolate_Point(inter_xs_dump.geom, 0.00005)::geometry(POINT, 2180) AS geom
    FROM
        inter_xs_dump),
    tmpman AS
    (SELECT
         sp."XsecID",
         sp."N_Value",
         sp."LUCode",
         ST_LineLocatePoint(sl.geom, sp.geom) AS "Fraction"
    FROM
        single_line AS sl,
        shiftpoints AS sp
    WHERE
        sl."XsecID" = sp."XsecID")
------------------------------------------------------------------------------------------------------------------------
-- Creation of table with Manning's coefficients  --
------------------------------------------------------------------------------------------------------------------------
INSERT INTO "Dzierzgon"."Manning" ("XsecID", "Fraction", "N_Value", "LUCode")
SELECT
    "XsecID",
    CASE WHEN
        "Fraction" < 0.0001 THEN 0
    ELSE
        "Fraction"
    END AS "Fraction",
    "N_Value",
    "LUCode"
FROM
    tmpman
ORDER BY
    "XsecID",
    "Fraction";
------------------------------------------------------------------------------------------------------------------------
DROP TABLE "Dzierzgon".ludump;
------------------------------------------------------------------------------------------------------------------------