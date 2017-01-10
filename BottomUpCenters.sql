SELECT s.page_id, s.to, SUM(s.mentions), s.the_geom
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
LIMIT 1000
