-- Calculate distance between two linked places
SELECT links."from", links."to", ST_Distance_Spheroid(p1.the_geom, p2.the_geom, 'SPHEROID["GRS_1980",6378137,298.257222]') AS distance
FROM pages AS p1, pages AS p2, links
WHERE links."from" = p1.page
AND links."to" = p2.page
LIMIT 50;

-- Calculate top 100 places based on number of incoming references that link to NYC
-- WITHOUT distance stored in links table!
-- this one runs forever, super slow...
SELECT 	 fromp.id, 
		 fromp.page, 
		 fromp.the_geom,
		 incoming.incoming, 
		 ST_Distance_Spheroid(fromp.the_geom, top.the_geom, 'SPHEROID["GRS_1980",6378137,298.257222]') AS distance,
		 (incoming.incoming / ST_Distance_Spheroid(fromp.the_geom, top.the_geom, 'SPHEROID["GRS_1980",6378137,298.257222]')) AS weight
FROM 	 incoming, pages AS fromp, pages as top, links
WHERE 	 top.page = incoming.page
AND 	 links."from" = fromp.page
AND      links."to" = 'New York City'
AND	 	 ST_Distance_Spheroid(fromp.the_geom, top.the_geom, 'SPHEROID["GRS_1980",6378137,298.257222]') > 0
ORDER BY weight DESC
LIMIT 	 100;


-- Calculate top 100 places based on number of incoming references that link to NYC
-- WITH distance pre-calculated in links table (see CREATE-TABLE-incoming.sql):
SELECT 	pages.id, 
	pages.page, 
	pages.the_geom,
	incoming.incoming, 
	links.w_dist
FROM 	 incoming, pages, links
WHERE 	 links."to" = 'New York City'
AND 	 links."from" = pages.page
AND      pages.page = incoming.page
ORDER BY w_dist ASC
LIMIT 	 100;

-- Calculate top 100 places based on number of incoming references that link to NYC
-- WITH distance pre-calculated in links table (see CREATE-TABLE-incoming.sql),
-- AND create lines between NYC and the other (linking) places
SELECT 	pages.id, 
	pages.page, 
	ST_MakeLine(pages.the_geom, nyc.the_geom) AS linegeom,
	incoming.incoming, 
	links.w_dist
FROM 	 incoming, pages, links, pages AS nyc
WHERE 	 links."to" = 'New York City'
AND       nyc.page = links."to"
AND 	 links."from" = pages.page
AND      pages.page = incoming.page
ORDER BY w_dist ASC
LIMIT 	 100;


-- calculate distance and weighted distance between all linked pages with coordinates
SELECT 	 fromp.page, 
         top.page,
		 incoming.incoming, 
		 ST_Distance_Spheroid(fromp.the_geom, top.the_geom, 'SPHEROID["GRS_1980",6378137,298.257222]') AS distance,
		 (incoming.incoming / ST_Distance_Spheroid(fromp.the_geom, top.the_geom, 'SPHEROID["GRS_1980",6378137,298.257222]')) AS weight
FROM 	 incoming, pages AS fromp, pages as top, links
WHERE 	 top.page = incoming.page
AND 	 links."from" = fromp.page
AND      links."to" = top.page
AND	 ST_Distance_Spheroid(fromp.the_geom, top.the_geom, 'SPHEROID["GRS_1980",6378137,298.257222]') > 0
LIMIT 	 100;



-- pages linking to themselves
select * from links
where links."from" = links."to"

-- pages LINKING TO New York City

select pages.id, pages.page, pages.the_geom, (links.links + links.mentions) as refs
from links, pages
where links."to" = 'New York City'
and pages.page = links."from"

-- Get the list of the top 100 linked-to pages

SELECT pages.page, pages.id, incoming.incoming, pages.the_geom
FROM incoming, pages
WHERE pages.page = incoming.page
ORDER BY incoming DESC
LIMIT 100;

-- put pages on map based on incoming links:

SELECT pages.id, pages.page, pages.the_geom, incoming.incoming
FROM pages, incoming
WHERE pages.page = incoming.page
LIMIT 100



-- convex hull example

SELECT row_number() OVER() As fake_id, lang, ST_ConvexHull(ST_Collect(the_geom::geometry)) As hull_geom
    FROM pagesgeom as p, links as l
	WHERE page like 'New%'
    GROUP BY lang;


-- convex hull around places linking to NYC:

SELECT row_number() OVER() As fake_id, p.lang, ST_ConvexHull(ST_Collect(p.the_geom::geometry)) As hull_geom
    FROM pagesgeom as p, links as l
	WHERE l."to" = 'New York City'
	AND l."from" = p.page
	AND l.lang = p.lang
    GROUP BY p.lang;

-- loads pages with incoming links as a layer in QGIS:

SELECT pages.page, pages.id, (incoming.incoming * -1) AS incoming, pages.the_geom FROM pages, incoming WHERE pages.page = incoming.page
