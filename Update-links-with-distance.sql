ALTER TABLE links ADD distance double precision, ADD w_dist double precision;

UPDATE links SET
	   distance = ST_Distance_Spheroid(fromp.the_geom, top.the_geom, 'SPHEROID["GRS_1980",6378137,298.257222]'),
	   w_dist = (ST_Distance_Spheroid(fromp.the_geom, top.the_geom, 'SPHEROID["GRS_1980",6378137,298.257222]') / (incoming.incoming * incoming.incoming))
FROM   incoming, pages AS fromp, pages as top
WHERE  top.de = incoming.page
AND    links."from" = fromp.de
AND    links."to" = top.de;

-- these create sorted ascending indexes, i.e., the results will ALWAYS be ordered
-- ascendingly, even if we don't ask for it. See http://www.postgresql.org/docs/8.3/static/indexes-ordering.html
-- should also speed up ORDER BY DESC queries
CREATE INDEX distance_index ON links USING btree ( distance ASC NULLS LAST);
CREATE INDEX w_dist_index ON links USING btree (w_dist ASC NULLS LAST);
