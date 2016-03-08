SELECT row_to_json(fc)
FROM (
	SELECT 'FeatureCollection' As type, array_to_json(array_agg(f)) As features
	FROM (
		SELECT 'Feature' As type, ST_AsGeoJSON(lg.the_geom)::json As geometry, row_to_json(lp) As properties
		FROM pages AS lg
		JOIN (
			SELECT pages.page_id AS page_id, pages.page AS page, pages.the_geom AS the_geom -- fromid, "from", mentions -- it's curcial to have the toid in the output!
			FROM links, pages
			WHERE links.toid = 4346836
			AND links.line_geom IS NOT NULL
			AND pages.page_id = links.fromid
			ORDER BY links.mentions DESC
			LIMIT 10) As lp
		ON lg.page_id = lp.page_id) -- AND lg.toid = lp.toid  )
	As f )
As fc;
