COPY (

	SELECT page_id, page, incoming
	FROM pages
	WHERE type = 'city'
	AND incoming_from_cities > 0
	AND country = 'DE'
	AND page NOT IN (
		SELECT city
		FROM centers_de
		)
	)

TO '/Users/carsten/Dropbox/Code/CentralPlaceWiki/Python Plots/Incoming references - plots/All Incoming references - all cities DE.csv' WITH CSV HEADER;
