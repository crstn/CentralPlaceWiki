# DROP TABLE IF EXISTS links;

CREATE TABLE links 
	("from" 	varchar, 
	 "to" 		varchar, 
	 lang 		varchar, 
	 links 		integer, 
	 mentions 	integer,
	 id 		serial primary key );

CREATE INDEX link_from_index ON links USING hash ( "from" );
CREATE INDEX link_to_index ON links USING hash ( "to" );