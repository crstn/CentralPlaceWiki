SELECT row_to_json(fc)
FROM (
	SELECT 'FeatureCollection' As type, array_to_json(array_agg(f)) As features
	FROM (
		SELECT 'Feature' As type, ST_AsGeoJSON(lg.line_geom)::json As geometry, row_to_json(lp) As properties
		FROM links As lg
		JOIN (
			SELECT toid, fromid, "from", mentions -- it's curcial to have the toid in the output!
			FROM links
			WHERE toid = 4346836
			AND line_geom IS NOT NULL
			ORDER BY mentions DESC
			LIMIT 10) As lp
		ON lg.fromid = lp.fromid AND lg.toid = lp.toid  )
	As f )
As fc;
