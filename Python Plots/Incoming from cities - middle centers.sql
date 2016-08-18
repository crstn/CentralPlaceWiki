COPY (

	SELECT p.page_id, p.page, p.incoming_from_cities
	FROM pages p,
	     centers_de c
	WHERE p.type = 'city'
	AND   p.page = c.city
	AND   c.type > 1
	GROUP BY (p.page_id, p.page)

	)

TO '/Users/carsten/Dropbox/Code/CentralPlaceWiki/Python Plots/Incoming from cities - middle centers.csv' WITH CSV HEADER;
