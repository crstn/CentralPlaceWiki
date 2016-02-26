-- Based on https://ariejan.net/2008/11/27/export-csv-directly-from-mysql/
SELECT gt_id,
       gt_page_id,
--       CAST(gt_globe as CHAR) AS gt_globe,              -- not needed
--       gt_primary,                                      -- not needed
       CONCAT('POINT(', gt_lon, ' ', gt_lat, ')') AS geom, -- directly construct PostGIS points
       gt_dim,
       CAST(gt_type as CHAR) AS gt_type,
       CAST(gt_name as CHAR) AS gt_name,
       CAST(gt_country as CHAR) AS gt_country,
       CAST(gt_region as CHAR) AS gt_region
INTO OUTFILE '~/geo_tags.csv'
FIELDS TERMINATED BY ','
OPTIONALLY ENCLOSED BY '"'
ESCAPED BY '\\'
LINES TERMINATED BY '\n'
FROM     geo_tags
WHERE    gt_primary = 1                     -- only use primary geotags
AND      CAST(gt_globe as CHAR) = 'earth'   -- use only coordinates on Earth (there does not seem to be others in the dataset, but just in case...)
