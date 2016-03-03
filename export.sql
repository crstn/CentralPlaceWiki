COPY geo_tags (gt_page_id, gt_lat, gt_lon, gt_name, gt_type, gt_country, gt_region)
TO '/Users/carsten/Desktop/geo_tag.csv'
NULL '\N' DELIMITER ',' CSV HEADER ESCAPE '\' ;

COPY links
TO '/Users/carsten/Desktop/links.csv'
NULL '\N' DELIMITER ',' CSV HEADER ESCAPE '\' ;
