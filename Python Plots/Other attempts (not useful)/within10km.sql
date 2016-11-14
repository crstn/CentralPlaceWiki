Copy (

SELECT 	q1.page, 
	q1.type, 
	q1.incoming, 
	q1.avg AS avg_within_10k, 
	q1.count AS linking_places_within_10k, 
	q2.sum AS incoming_within_10k 
FROM

	(SELECT p1.page, c.type, p1.incoming, AVG(p2.incoming), COUNT(*)
	FROM pages AS p1,
	     pages AS p2,
	     centers_de AS c
	WHERE st_dwithin(p1.the_geom, p2.the_geom, 10000)
	AND p1.page != p2.page
	AND p1.page = c.city
	GROUP BY p1.page, p1.incoming, c.type) AS q1,

	(SELECT links.to, SUM(links.links+links.mentions)
	FROM links, centers_de
	WHERE links.dist_sphere_meters < 10000
	AND links.to = centers_de.city
	GROUP BY links.to) AS q2

WHERE q1.page = q2.to
ORDER BY q1.incoming DESC

)
To '/Users/Carsten/Dropbox/Code/CentralPlaceWiki/Python Plots/within-10km.csv' With CSV HEADER;