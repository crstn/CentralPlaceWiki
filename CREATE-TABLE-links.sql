DROP TABLE IF EXISTS links;

CREATE TABLE links
	("fromid"   integer,
	 "from" 	  varchar,
	 "to" 		  varchar,
	 "lang" 		varchar,
	 "links" 		integer,
	 "mentions" integer,
	 "id" 		  serial primary key );

CREATE INDEX links_index_to ON links USING hash ( "to" );
CREATE INDEX links_index_from ON links USING hash ( "from" );
