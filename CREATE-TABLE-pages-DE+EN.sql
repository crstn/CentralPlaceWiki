DROP TABLE IF EXISTS pages;

CREATE TABLE pages
	(de 		varchar,
	 en 		varchar,
	 the_geom 	geometry,
	 id 		serial primary key );

CREATE INDEX pages_geom_index ON pages USING GIST ( the_geom );

CREATE INDEX page_name_index_de ON pages USING hash ( de );

CREATE INDEX page_name_index_en ON pages USING hash ( en );
