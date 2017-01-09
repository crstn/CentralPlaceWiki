COPY (

	SELECT page_id, page, incoming_from_cities
	FROM pages
	WHERE type = 'city'
	AND incoming_from_cities > 0
	AND country = 'DE';

	)

TO '/Users/carsten/Dropbox/Code/CentralPlaceWiki/Python Plots/Incoming from cities - all cities.csv' WITH CSV HEADER;
