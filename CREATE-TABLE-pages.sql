DROP TABLE IF EXISTS pages;

CREATE TABLE pages 
	(page 		varchar, 
	 lang 		varchar, 
	 the_geom 	geometry,
	 id 		serial primary key );

CREATE INDEX pages_geom_index ON pages USING GIST ( the_geom ); 

CREATE INDEX page_name_index ON pages USING hash ( page );