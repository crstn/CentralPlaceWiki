DROP TABLE IF EXISTS pages;

CREATE TABLE pages
	(de 					varchar,
	 en 				  varchar,
	 de_alias_for varchar,
 	 en_alias_for varchar,
	 the_geom 		geometry,
	 wikidata_id	varchar,
	 id 					serial primary key );

CREATE INDEX pages_geom_index ON pages USING GIST ( the_geom );

CREATE INDEX page_name_index_de ON pages USING hash ( de );

CREATE INDEX page_name_index_en ON pages USING hash ( en );

CREATE INDEX page_alias_index_de ON pages USING hash ( de_alias_for );

CREATE INDEX page_alias_index_en ON pages USING hash ( en_alias_for );
