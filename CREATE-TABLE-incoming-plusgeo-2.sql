DROP TABLE IF EXISTS incoming;

-- This portion took about 24 hours on a Macbook Air
CREATE TABLE incoming AS
  SELECT "to" AS page, lang, SUM(links.links + links.mentions) AS incoming
	FROM links
	GROUP BY "to", lang;

ALTER TABLE incoming
    ALTER COLUMN incoming SET DATA TYPE integer;

-- This portion took 16.6 hours on a Macbook Air
ALTER TABLE incoming ADD COLUMN incoming_geo integer;

UPDATE incoming
  SET "incoming_geo" =
  (
	SELECT SUM(injoin.links + injoin.mentions)
	FROM
	  ( --injoin: table where links."from" is in pages
	  	SELECT pages.page,
	  	pages.lang,
	  	links.from,
	  	links.to,
	  	links.links,
	  	links.mentions
		FROM pages
		INNER JOIN links
	      ON pages.lang=links.lang
	        AND pages.page=links.from
	  ) AS injoin
    WHERE (injoin.to = incoming.page
      AND injoin."lang" = incoming."lang")
  );

CREATE INDEX incoming_name_index ON incoming USING hash ( page );
