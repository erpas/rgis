UPDATE tazyna_xscutlines
SET
"RiverCode" = tazyna_xscutlines2.rivercode,
"ReachCode" = tazyna_xscutlines2.reachcode
FROM tazyna_xscutlines2
WHERE tazyna_xscutlines."HydroID" = tazyna_xscutlines2.hydroid