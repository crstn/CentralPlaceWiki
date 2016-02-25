# CentralPlaceWiki

Code for a research project about identifying central place structures using geotagged pages in Wikipedia. To run this, perform the following steps. You’ll need a lot of free disk space (how much depends on which language edition of wikipedia you are processing). A fast computer obviously helps running everything faster.

You should have a good idea of how Python and PostGIS work if you are trying to run this. I’m assuming here you’re on a Unix-ish system, good luck if you’re on Windows. Here we go:

1. Download a wikipedia pages XML dump in the language of your choice, e.g. go [here](https://dumps.wikimedia.org/enwiki/) for English, go to one of the date subfolders, and download the file ending in `ages-articles-multistream.xml.bz2`, then unzip it

2. From the same page, download the file ending in `geo_tags.sql.gz `, and unzip it, too

3. Run `threadedparser.py` on your unzipped `ages-articles-multistream.xml` file. It identifies all links and mentions between wikipedia pages, counts them, and summarizes that information in a SQL script to load into a PostGres database. You can start multiple copies of the script to speed things up if you have a multicore processor, e.g.
```
python threadedparser.py 2 1 ages-articles-multistream.xml > output1.sql &
python threadedparser.py 2 2 ages-articles-multistream.xml > output2.sql &
```
This would start the parser in 2 threads (first argument), the first thread will process every 1/2 articles, the second one every 2/2 article (second argument). The third argument is the file to process, output is written to a SQL file. This will take a while.

4. Once all threads are done parsing, run the following command on the terminal to combine all files into one sql file:
```
cat *.sql > insert-links.sql
```

5. Install PostGres and set up a new database cluster, start Postgres, and initialize a new database called `cpt`. Make sure you install the PostGIS extension for the database. 
```
psql -f CREATE-TABLE-links.sql cpt
psql —q f insert-links.sql cpt
```
This will also take a while. While you are waiting for this step to finish, you can work on the following step.

6. The unzipped `geo_tags.sql` is in MySQL’s SQL dialect. Since there seems to be no straightforward way to simply convert the SQL file to PostGres syntax, I have loaded the file into a MySQL database, and then used the `mysqlBinaryCast.sql` script to export the data in CSV format like so:
```
To be continued…
```
