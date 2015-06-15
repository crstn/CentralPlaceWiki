SELECT row_to_json(fc)
 FROM ( 
 	SELECT 'FeatureCollection' As type, 
 		array_to_json(array_agg(f)) As features
 		FROM ( 
 			SELECT 'Feature' As type, 
 			         ST_AsGeoJSON(lg.the_geom)::json As geometry, 
 			         row_to_json(lp) As properties
   					 FROM pages As lg    					 
        			 INNER JOIN (SELECT id, page FROM pages LIMIT 100) As lp 
       				 ON lg.id = lp.id  ) As f )  As fc;