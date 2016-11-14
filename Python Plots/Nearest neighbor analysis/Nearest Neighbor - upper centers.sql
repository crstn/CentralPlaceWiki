COPY ( 

	SELECT p.page_id, p.page, MIN(p.the_geom<->neighbor.the_geom)
	FROM pages p, 
	     pages neighbor,
	     centers_de c
	WHERE neighbor.type = 'city'
	  AND p.type = 'city'
	  AND p.page_id != neighbor.page_id
	  AND st_dwithin(p.the_geom, neighbor.the_geom, 10000)
	  AND p.page = c.city
	  AND c.type = 1
	GROUP BY (p.page_id, p.page)
	ORDER BY MIN )

TO '/Users/carsten/Dropbox/Code/CentralPlaceWiki/Python Plots/Nearest Neighbor - upper centers.csv' WITH CSV HEADER;


