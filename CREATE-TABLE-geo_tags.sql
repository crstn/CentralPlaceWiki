DROP TABLE IF EXISTS geo_tags;

CREATE TABLE geo_tags (
	gt_id 		integer primary key,
	gt_page_id 	integer,
	gt_lat		double precision,
	gt_lon		double precision,
	gt_dim 		integer,
	gt_type 	varchar,
	gt_name 	varchar,
	gt_country 	varchar,
	gt_region	varchar	
	);

COPY geo_tags FROM '/Users/carsten/geo_tags.csv' NULL '\N' DELIMITER ',' CSV ESCAPE '\' ;

-- make point geometries from lat/long:
ALTER TABLE geo_tags 
ADD COLUMN the_geom geography (POINT, 4326 );

UPDATE geo_tags 
SET the_geom = ST_SetSRID( ST_MakePoint( gt_lon, gt_lat ), 4326 );

-- add indexes on the page IDs and on the point geometries:
CREATE INDEX geo_tags_page_id ON geo_tags USING btree ( gt_page_id );
CREATE INDEX geo_tags_coords ON geo_tags USING gist ( the_geom );
