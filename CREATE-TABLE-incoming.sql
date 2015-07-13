DROP TABLE IF EXISTS incoming;

CREATE TABLE incoming AS 
  SELECT "to" AS page, lang, SUM(links.links + links.mentions) AS incoming
	FROM links
	GROUP BY "to", lang;

CREATE INDEX incoming_name_index ON incoming USING hash ( page );
