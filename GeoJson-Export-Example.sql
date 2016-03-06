SELECT row_to_json(fc)
 FROM ( SELECT 'FeatureCollection' As type, array_to_json(array_agg(f)) As features
 FROM (SELECT 'Feature' As type
    , ST_AsGeoJSON(lg.the_geom)::json As geometry
    , row_to_json(lp) As properties
   FROM pages As lg
         INNER JOIN (SELECT page_id, page FROM pages WHERE page LIKE 'Berlin%' AND the_geom IS NOT NULL) As lp
       ON lg.page_id = lp.page_id  ) As f )  As fc;
