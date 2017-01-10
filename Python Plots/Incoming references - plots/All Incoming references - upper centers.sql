COPY (

	SELECT p.page_id, p.page, p.incoming
	FROM pages p,
	     centers_de c
	WHERE p.type = 'city'
	AND   p.page = c.city
	AND   c.type = 1
	AND   p.incoming_from_cities > 0

	)

TO '/Users/carsten/Dropbox/Code/CentralPlaceWiki/Python Plots/Incoming references - plots/All Incoming references - upper centers.csv' WITH CSV HEADER;
