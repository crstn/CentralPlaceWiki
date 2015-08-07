ALTER TABLE hexgrid
ADD COLUMN pages_en integer;

UPDATE hexgrid h
SET pages_en = point_count
FROM (
	SELECT a.gid, count(*) AS point_count
	FROM hexgrid a JOIN pages b
		ON (ST_Contains(a.the_geom, b.the_geom))
	GROUP BY a.gid
	) c
WHERE h.gid = c.gid;
