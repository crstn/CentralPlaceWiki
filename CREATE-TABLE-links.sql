DROP TABLE IF EXISTS links;

CREATE TABLE links
	("fromid"   integer,
	 "from" 	  varchar,
	 "to" 		  varchar,
	 "lang" 		varchar,
	 "links" 		integer,
	 "mentions" integer,
	 "id" 		  serial primary key );
