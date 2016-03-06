# CentralPlaceWiki

Code for a research project about identifying central place structures using geotagged pages in Wikipedia. To run this, perform the following steps. You’ll need a lot of free disk space (how much depends on which language edition of wikipedia you are processing). A fast computer obviously helps running everything faster.

You should have a good idea of how Python and PostGIS work if you are trying to run this. I’m assuming here you’re on a Unix-ish system, good luck if you’re on Windows. Here we go:

1. Download a wikipedia pages XML dump in the language of your choice, e.g. go [here](https://dumps.wikimedia.org/enwiki/) for English, go to one of the date subfolders, and download the file ending in `ages-articles-multistream.xml.bz2`, then unzip it. You can down and unzip in one go like so:
  ```
  curl https://dumps.wikimedia.org/dewiki/20160203/dewiki-20160203-pages-articles-multistream.xml.bz2 | bunzip2 > dewiki-20160203-pages-articles-multistream.xml
  ```

2. From the same page, download the file ending in `geo_tags.sql.gz `, and unzip it, too

3. Install PostGres and set up a new database cluster. Before you start Postgres, make sure to [tune the configuration](https://wiki.postgresql.org/wiki/Tuning_Your_PostgreSQL_Server). This will speed things up that we’ll do later (a sample config file for a Mac Pro is included in this repo). Then start PostGres and initialize a new database called `cpt`. Make sure you install the PostGIS extension for the database (Note about the content of the database: Because of the way the parser is set up, the count in the `mentions` column *includes* the count for the `links` column, so this is already the total number of references from page A to page B).
  ```
  psql -f CREATE-TABLE-links.sql cpt
  ```
4. Run `threadedparser.py` on your unzipped `ages-articles-multistream.xml` file. It identifies all links and mentions between wikipedia pages, counts them, and summarizes that information in a SQL script to load into a PostGres database. You can start multiple copies of the script to speed things up if you have a multicore processor, e.g.
  ```
  python threadedparser.py 2 1 ages-articles-multistream.xml en | psql -q cpt &
  python threadedparser.py 2 2 ages-articles-multistream.xml en | psql -q cpt &
  ```
This would start the parser in 2 threads (first argument), the first thread will process every 1/2 articles, the second one every 2/2 article (second argument). The third argument is the file to process, and the output is directly piped to psql, i.e., written into the database. This will take a while (probably several hours).

5. The unzipped `geo_tags.sql` is in MySQL’s SQL dialect. Since there seems to be no straightforward way to simply convert the SQL file to PostGres syntax, I have loaded the file into a MySQL database (I have [MAMP](https://www.mamp.info/en/) installed and set up a new database named `wikipedia`) like so:
  ```
  /Applications/MAMP/Library/bin/mysql wikipedia -uroot -proot < geo_tags.sql
  ```
  and then use the `mysqlBinaryCast.sql` script to export the data in CSV format like so:
  ```
  /Applications/MAMP/Library/bin/mysql wikipedia -uroot -proot < mysqlBinaryCast.sql
  ```
After running that (this one should be fast), you will find a file called `geo_tags.csv` in your home directory. Note that the export only take the *primary* geotag for every page, so the export will have significantly fewer rows than the original database.

6. Import the file into PostGIS by running `CREATE-TABLE-geo_tags.sql`. You’ll need to edit the file first and change the path to the csv file, since PostGres doesn’t understand the ~ shortcut for the user’s home.
  ```
  psql -f CREATE-TABLE-geo_tags.sql cpt
  ```

7. Now is a good time to check whether your imported data is complete, using the `test-completeness.py` python script. Modify the file `DE_CPT_Hierarchy.txt` so that it contains all places that you need to have with coordinates. The script will query your DB for all of them and print out the ones that are missing. You could then choose to add them manually, for example. In my case, most of the missing places were just spelled differently ion my list compared to wikipedia, so changing the spelling in your list can also fix the issue. I had to manually add two places to the geo_tags table because they didn’t have coordinates on Wikipedia:
  ```
  2814320, Oberzentraler Städteverbund
  1095309, Städtebund Silberberg
  ```

8. Since those represent groups of towns that have been set up as  a combined center due to the lack of a larger city in the region, it makes sense that these groups do not have coordinates in Wikipedia. For our calculations, however, we need all places to have coordinates. So I looked up the places that belong to those groups of towns online, and then looked up the page IDs of their wikipedia pages in the links table. I have then calculated the centroid between the places like so:
  ```SQL
  SELECT gt_country, ST_AsEWKT(st_centroid(st_union(the_geom::geometry))) as geom
  FROM geo_tags
  WHERE gt_page_id = 3698848
  OR gt_page_id = 17322
  OR gt_page_id = 16976
  GROUP BY gt_country;
  ```
and created insert statements with those centroids for the geo_tags table like so (I know this could be done in one step, but I was too lazy to write that query):
  ```SQL
  INSERT INTO geo_tags(gt_id, gt_page_id, gt_lat, gt_lon, gt_dim, gt_type, gt_name, gt_country, gt_region, the_geom)
  VALUES (56029078, 2814320, 51.25583221, 14.5537037933333, 10000, ‘city’, ‘Oberzentraler Städteverbund’, ‘DE’, ‘SN’, ST_GeomFromText(‘POINT(14.5537037933333 51.25583221)’, 4326));
  INSERT INTO geo_tags(gt_id, gt_page_id, gt_lat, gt_lon, gt_dim, gt_type, gt_name, gt_country, gt_region, the_gom)
  VALUES (56029079, 1095309, 50.5871758916667, 12.7122222216667, 10000, ‘city’, ‘Städtebund Silberberg’, ‘DE’, ‘SN’, ST_GeomFromText(‘POINT(12.7122222216667 50.5871758916667)’, 4326));
  ```

9. In order to compute the distance between two places that link to each other, we need the IDs for the linked-to pages. This is a self-join on the `links` table, which tries to find the ID for ever linked-to page (these IDs are missing in the links table) by looking for the page named in the `from` column of the same table, then using the `fromid` (which _is_ contained in the table). Naturally, this means we do not find all of the IDs because some pages do not have any links in them, but this is only a very small number of pages. Since this was very slow in PostGIS, I decided to do this step in Python and then re-import the data. So, let’s export the data first (before you run this, edit the script to adjust the path to the export file):
  ```
  psql -f export.sql cpt
  ```
This will export the `geo_tags` and the `links` table as CSV files that we’ll process in Python in the next step.




## Known issues

This approach currently does not take [redirects within Wikipedia](https://en.wikipedia.org/wiki/Wikipedia:Redirect) into account, so the link count is slightly off for some pages that link to redirects. The redirects can also be downloaded from the dumps archive; to address this, one would have to replace each link to a redirect in the links table with the page that redirect redirects to (yes, that sentence *is* correct 😬).
