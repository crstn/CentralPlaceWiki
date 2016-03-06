-- set up pages table

DROP TABLE IF EXISTS pages;

CREATE TABLE pages (
  page_id integer primary key,
  page varchar,
  lat double precision,
  lon double precision,
  gt_name varchar,
  type varchar,
  country varchar,
  region varchar
);


-- import pages data

COPY pages FROM '/Volumes/Solid Guy/CPT Python Data/pages_processed.csv' HEADER NULL '' DELIMITER ',' CSV ESCAPE '\';



-- calculate point geometries from lat/lon columns

ALTER TABLE pages
ADD COLUMN the_geom geography (POINT, 4326 );

UPDATE pages
SET the_geom = ST_SetSRID( ST_MakePoint( lon, lat ), 4326 );

-- add indexes:

CREATE INDEX pages_page_id_index ON pages USING btree ( page_id );
CREATE INDEX pages_page_index ON pages USING btree ( page );
CREATE INDEX pages_gt_name_index ON pages USING btree ( gt_name );
CREATE INDEX pages_type_index ON pages USING btree ( type );
CREATE INDEX pages_country_index ON pages USING btree ( country );
CREATE INDEX pages_region_index ON pages USING btree ( region );
CREATE INDEX pages_geom_index ON pages USING GIST ( the_geom );

-- set up links table

DROP TABLE IF EXISTS links;

CREATE TABLE links (
  fromid integer,
  "from" varchar,
  "to" varchar,
  lang varchar,
  links integer,
  mentions integer,
  toid integer,
  from_lat double precision,
  from_lon double precision,
  to_lat double precision,
  to_lon double precision,
  dist_sphere_meters double precision,
);

-- Now import links data via pgloader!
