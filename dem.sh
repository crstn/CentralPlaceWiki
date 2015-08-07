uptime
gdal_grid -zfield "incoming" -a invdist:power=2.0:smoothing=1.0 -txe -180 180 -tye -90 90 -outsize 2880 1440 -of GTiff -ot Float64 PG:dbname=CPT -sql "SELECT pages.page, pages.id, (incoming.incoming * -1) AS incoming, pages.the_geom FROM pages, incoming WHERE pages.page = incoming.page" gdal-dem-invdist-2.0.tiff --config GDAL_NUM_THREADS ALL_CPUS
uptime
