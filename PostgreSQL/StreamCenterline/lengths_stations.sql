------------------------------------------------------------------------------------------------------------------------
WITH all_nodes AS
    (SELECT
        "RiverCode",
        "ReachCode",
        ST_StartPoint(geom) AS geom,
        'start' AS point_type
    FROM
        "StreamCenterlines"
    UNION ALL
    SELECT
        "RiverCode",
        "ReachCode",
        ST_EndPoint(geom) AS geom,
        'end' AS point_type
    FROM
        "StreamCenterlines"),
    single_nodes AS
    (SELECT
        "RiverCode",
        geom
    FROM
        all_nodes
    GROUP BY
        "RiverCode",
        geom
    HAVING
        COUNT(geom) = 1)

    INSERT INTO "Endpoints"(geom, "RiverCode", "ReachCode", "NodeID")
    SELECT
        all_nodes.geom,
        all_nodes."RiverCode",
        all_nodes."ReachCode",
        "NodesTable"."NodeID"
    FROM
        all_nodes,
        single_nodes,
        "NodesTable"
    WHERE
        all_nodes."RiverCode" = single_nodes."RiverCode" AND
        all_nodes.geom = single_nodes.geom AND
        all_nodes.point_type = 'end' AND
        all_nodes.geom = "NodesTable".geom;

------------------------------------------------------------------------------------------------------------------------
CREATE OR REPLACE FUNCTION from_to_stations ()
    RETURNS VOID AS
$BODY$
DECLARE
    c cursor FOR SELECT * FROM "Endpoints";
    r "Endpoints"%ROWTYPE;
    river text;
    tonode_id integer;
    fromnode_id integer;
    fromsta double precision;
    tosta double precision;
    len double precision;
BEGIN
FOR r IN c LOOP
    river := r."RiverCode";
    tonode_id := r."NodeID";
    fromsta := 0;
    tosta := 0;
    FOR i IN 1..(SELECT COUNT(*) FROM "StreamCenterlines" WHERE "StreamCenterlines"."RiverCode" = river) LOOP
        SELECT "FromNode", ST_Length(geom) INTO fromnode_id, len FROM "StreamCenterlines" WHERE "RiverCode" = river AND "ToNode" = tonode_id;
        tosta := fromsta + len;
        UPDATE "StreamCenterlines" SET
        "ReachLen" = len,
        "FromSta" = fromsta,
        "ToSta" = tosta
        WHERE "RiverCode" = river AND "ToNode" = tonode_id;
        tonode_id := fromnode_id;
        fromsta := tosta;
    END LOOP;
END LOOP;
END;
$BODY$
    LANGUAGE plpgsql;

------------------------------------------------------------------------------------------------------------------------
SELECT from_to_stations ();
DROP FUNCTION IF EXISTS from_to_stations ()
------------------------------------------------------------------------------------------------------------------------