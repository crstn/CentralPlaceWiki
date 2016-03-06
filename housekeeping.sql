-- add a primary key column to the links table:

ALTER TABLE links ADD COLUMN linkid SERIAL PRIMARY KEY;


-- clean up the columns where toid = -1, replace with NULL

UPDATE links
SET toid = NULL
WHERE toid = -1;

-- calculate point geometries from lat/lon columns (for FROM and TO)



-- calculate great circle line geometries for all links that have FROM and TO coordinates




-- add indexes on the FROMID, TOID, FROM, TO, LANG, FROM POINT and TO POINT columns



-- add the number of incoming links for every page to the pages table






-- and index that column
