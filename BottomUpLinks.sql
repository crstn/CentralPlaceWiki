SELECT DISTINCT ON (l.from)
       l.linkid, l.from, l.to, l.mentions, l.line_geom
FROM links l, pages p1, pages p2, (
	SELECT s.to
	FROM (
		SELECT DISTINCT ON (l.from)
		       l.from, l.to, l.mentions, p2.the_geom, p2.page_id
		FROM links l, pages p1, pages p2
		WHERE l.from = p1.page
		AND p1.type = 'city'
		AND p1.country = 'DE'
		AND l.to = p2.page
		AND p2.type = 'city'
		AND p2.country = 'DE'
		ORDER BY l.from, l.mentions DESC ) s
	GROUP BY s.to, s.page_id, s.the_geom
	ORDER BY SUM(s.mentions) DESC
	LIMIT 1000) x1, (
	SELECT s.to
	FROM (
		SELECT DISTINCT ON (l.from)
		       l.from, l.to, l.mentions, p2.the_geom, p2.page_id
		FROM links l, pages p1, pages p2
		WHERE l.from = p1.page
		AND p1.type = 'city'
		AND p1.country = 'DE'
		AND l.to = p2.page
		AND p2.type = 'city'
		AND p2.country = 'DE'
		ORDER BY l.from, l.mentions DESC ) s
	GROUP BY s.to, s.page_id, s.the_geom
	ORDER BY SUM(s.mentions) DESC
	LIMIT 1000) x2
WHERE l.from = p1.page
AND p1.type = 'city'
AND p1.country = 'DE'
AND l.to = p2.page
AND p2.type = 'city'
AND p2.country = 'DE'
AND x1.to = l.to
AND x2.to = l.from
ORDER BY l.from, l.mentions DESC ;
