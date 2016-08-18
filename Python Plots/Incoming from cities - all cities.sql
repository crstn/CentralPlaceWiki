COPY (

	SELECT p.page_id, p.page, p.incoming_from_cities
	FROM pages p
	WHERE p.type = 'city'

	)

TO '/Users/carsten/Dropbox/Code/CentralPlaceWiki/Python Plots/Incoming from cities - all cities.csv' WITH CSV HEADER;
