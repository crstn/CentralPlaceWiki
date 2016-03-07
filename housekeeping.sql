-- add a primary key column to the links table:

ALTER TABLE links ADD COLUMN linkid SERIAL PRIMARY KEY;


-- clean up the columns where toid = -1, replace with NULL

UPDATE links
SET toid = NULL
WHERE toid = -1;

-- calculate point geometries from lat/lon columns (for FROM and TO)

ALTER TABLE links
ADD COLUMN from_geom geography (POINT, 4326 );

UPDATE links
SET from_geom = ST_SetSRID( ST_MakePoint( from_lon, from_lat ), 4326 );


ALTER TABLE links
ADD COLUMN to_geom geography (POINT, 4326 );

UPDATE links
SET to_geom = ST_SetSRID( ST_MakePoint( to_lon, to_lat ), 4326 );

-- insert the SRS that we need for the great circle distance:
INSERT into spatial_ref_sys (srid, auth_name, auth_srid, proj4text, srtext) values ( 953027, 'esri', 53027, '+proj=eqdc +lat_0=0 +lon_0=0 +lat_1=60 +lat_2=60 +x_0=0 +y_0=0 +a=6371000 +b=6371000 +units=m +no_defs ', 'PROJCS["Sphere_Equidistant_Conic",GEOGCS["GCS_Sphere",DATUM["Not_specified_based_on_Authalic_Sphere",SPHEROID["Sphere",6371000,0]],PRIMEM["Greenwich",0],UNIT["Degree",0.017453292519943295]],PROJECTION["Equidistant_Conic"],PARAMETER["False_Easting",0],PARAMETER["False_Northing",0],PARAMETER["Central_Meridian",0],PARAMETER["Standard_Parallel_1",60],PARAMETER["Standard_Parallel_2",60],PARAMETER["Latitude_Of_Origin",0],UNIT["Meter",1],AUTHORITY["EPSG","53027"]]');


-- calculate great circle line geometries for all links that have FROM and TO coordinates

ALTER TABLE links
ADD COLUMN line_geom geography (LINESTRING, 4326 );

UPDATE links
SET line_geom = ST_Transform(
  ST_Segmentize(
    ST_MakeLine(
      ST_Transform(from_geom::geometry, 953027),
      ST_Transform(to_geom::geometry, 953027)
    ),
  100000),
4326);

-- add indexes

CREATE INDEX links_fromid_index ON links USING btree ( fromid );
CREATE INDEX links_toid_index ON links USING btree ( toid );
CREATE INDEX links_from_index ON links USING btree ( "from" );
CREATE INDEX links_to_index ON links USING btree ( "to" );
CREATE INDEX links_lang_index ON links USING btree ( lang );
CREATE INDEX links_links_index ON links USING btree ( links );
CREATE INDEX links_mentions_index ON links USING btree ( mentions );
CREATE INDEX links_dist_index ON links USING btree ( dist_sphere_meters );
CREATE INDEX links_id_index ON links USING btree ( linkid );
CREATE INDEX links_fromgeo_index ON links USING GIST ( from_geom );
CREATE INDEX links_togeo_index ON links USING GIST ( to_geom );
CREATE INDEX links_linegeo_index ON links USING GIST ( line_geom );

-- add the number of incoming links for every page to the pages table

ALTER TABLE pages
ADD COLUMN incoming integer;

-- This one needs a subquery because UPDATE doesn't support GROUP BY.
-- It's pretty fast, though. Takes only a few minutes for dewiki
UPDATE pages
SET incoming = sq.summe
FROM (
  SELECT   toid, SUM(mentions) AS summe
  FROM     links
  GROUP BY toid
) AS sq
WHERE sq.toid = pages.page_id;

-- and index that column
CREATE INDEX pages_incoming_index ON pages USING btree ( incoming );
