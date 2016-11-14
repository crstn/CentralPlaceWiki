COPY (

	SELECT p.page_id, p.page, p.incoming_from_cities, p.incoming
	FROM pages p,
	     centers_de c
	WHERE p.type = 'city'
	AND   p.page = c.city
	AND   c.type > 1
	GROUP BY (p.page_id, p.page)

	)

TO '/Users/carsten/Dropbox/Code/CentralPlaceWiki/Python Plots/Both incoming links - all cities - scatterplot/Both incoming - middle centers.csv' WITH CSV HEADER;


COPY (

	SELECT p.page_id, p.page, p.incoming_from_cities, p.incoming
	FROM pages p,
	     centers_de c
	WHERE p.type = 'city'
	AND   p.page = c.city
	AND   c.type = 1
	GROUP BY (p.page_id, p.page)

	)

TO '/Users/carsten/Dropbox/Code/CentralPlaceWiki/Python Plots/Both incoming links - all cities - scatterplot/Both incoming - upper centers.csv' WITH CSV HEADER;



COPY (

	SELECT p.page_id, p.page, p.incoming_from_cities, p.incoming
	FROM pages p
	WHERE p.type = 'city'
	GROUP BY (p.page_id, p.page)

	)

TO '/Users/carsten/Dropbox/Code/CentralPlaceWiki/Python Plots/Both incoming links - all cities - scatterplot/Both incoming - all cities.csv' WITH CSV HEADER;
