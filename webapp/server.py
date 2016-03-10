import SimpleHTTPServer
import SocketServer
import logging
import cgi

import sys
import os

import psycopg2
from psycopg2 import extras

import urllib
import traceback

if len(sys.argv) > 2:
    PORT = int(sys.argv[2])
    I = sys.argv[1]
elif len(sys.argv) > 1:
    PORT = int(sys.argv[1])
    I = ""
else:
    PORT = 8000
    I = ""

# this will prevent the GeoJSON we load from PostGIS to be parsed into a Python object,
# since we want to send it straight to the client
extras.register_default_json(loads=lambda x: x)

# some content headers we'll need a few times:
geojsonHeader = 'application/vnd.geo+json; charset=utf-8'
jsonHeader = 'application/json; charset=utf-8'

try:
    conn = psycopg2.connect("dbname='cpt' host='localhost'")
except Exception as e:
    logging.error(e)

cur = conn.cursor()

class ServerHandler(SimpleHTTPServer.SimpleHTTPRequestHandler):

    def do_GET(self):
        logging.warning(self.path)

        # decompose the path to figure out what to do:
        urlpath = filter(None, self.path.split('/')) # the filter removes any empty strings from the list

        if len(urlpath) == 0:
            SimpleHTTPServer.SimpleHTTPRequestHandler.do_GET(self)

        # we'll start off with no restriction as to only querying cities,
        # this may be overriden in the individual queries (see below)
        citiesonly = """ """

        # check whether we have a limit argument on the path;
        # if not, set it to 10
        l = 10
        if len(urlpath) > 2:
            l = int(urlpath[2])



        if urlpath[0] == 'search':
            # s = urllib.unquote(self.path[8:]).decode('utf-8')+"%" # last bit of the path contains the search term, plus wildcard
            s = urllib.unquote(urlpath[1]).decode('utf-8')+"%" # last bit of the path contains the search term, plus wildcard

            # query only cities? TODO: doesn't work yet, have to figure
            # out how to make this work in typeahead.js
            if len(urlpath) > 3:
                if urlpath[3] == "citiesonly":
                    citiesonly = """ AND type = 'city' """


            query = """SELECT row_to_json(fc)
                       FROM (SELECT array_to_json(array_agg(f)) As results
                             FROM (SELECT page_id, page
                                   FROM pages
                                   WHERE ( page LIKE %s )
                                   AND incoming > 0
                                   AND the_geom IS NOT NULL
                                   """ + citiesonly + """
                                   ORDER BY incoming DESC limit %s ) AS f ) AS fc;"""

            queryDBsendResponse(self, query, (s,l,), jsonHeader)

            return

        elif urlpath[0] == 'place':

            s = int(urlpath[1]) # last bit of the path contains the page id we'll look for

            query = """SELECT row_to_json(fc) FROM (
                            SELECT 'FeatureCollection' As type, array_to_json(array_agg(f)) As features FROM (
                                    SELECT 'Feature' As type, ST_AsGeoJSON(lg.the_geom)::json As geometry, row_to_json(lp) As properties
                                    FROM pages As lg
                                    JOIN (
                                        SELECT page_id, page
                                        FROM pages
                                        WHERE page_id = %s
                                        AND the_geom IS NOT NULL
                                        ) As lp
                                    ON lg.page_id = lp.page_id  )
                                As f )
                            As fc;"""

            logging.info(query)

            queryDBsendResponse(self, query, (s,), geojsonHeader)

            return

        elif urlpath[0] == 'linksto':
            # s = int(self.path[9:]) # last bit of the path contains the page id we'll look for

            s = int(urlpath[1])

            frompart = """ FROM links """

            if len(urlpath) > 3:
                if urlpath[3] == "citiesonly":
                    frompart = """ FROM links, pages """
                    citiesonly = """ AND pages.page_id = links.fromid
                        AND pages.type = 'city' """

            query = """SELECT row_to_json(fc) FROM (
                        SELECT 'FeatureCollection' As type, array_to_json(array_agg(f)) As features FROM (
                            SELECT 'Feature' As type, ST_AsGeoJSON(lg.line_geom)::json As geometry, row_to_json(lp) As properties
                            FROM links As lg
                            JOIN ( SELECT links.toid, links.fromid, links."from", links.mentions
                                   """ + frompart + """
                                   WHERE links.toid = %s
                                   AND links.line_geom IS NOT NULL
                                   """ + citiesonly + """
                                   ORDER BY links.mentions DESC
                                   LIMIT %s) As lp
                            ON lg.fromid = lp.fromid AND lg.toid = lp.toid  )
                        As f )
                      As fc;"""

            logging.info(query)

            queryDBsendResponse(self, query, (s,l,), geojsonHeader)

            return

        elif urlpath[0] == 'placeslinkingto':

            s = int(urlpath[1])

            if len(urlpath) > 3:
                if urlpath[3] == "citiesonly":
                    citiesonly = """ AND pages.type = 'city' """

            query = """SELECT row_to_json(fc)
            FROM (
                SELECT 'FeatureCollection' As type, array_to_json(array_agg(f)) As features
                FROM (
                    SELECT 'Feature' As type, ST_AsGeoJSON(lg.the_geom)::json As geometry, row_to_json(lp) As properties
                    FROM pages AS lg
                    JOIN (
                        SELECT pages.page_id AS page_id,
                               pages.page AS page,
                               pages.the_geom AS the_geom,
                               links.mentions AS mentions
                        FROM links, pages
                        WHERE links.toid = %s
                        AND links.line_geom IS NOT NULL
                        AND pages.page_id = links.fromid
                        """ + citiesonly + """
                        ORDER BY links.mentions DESC
                        LIMIT %s) As lp
                    ON lg.page_id = lp.page_id)
                As f )
            As fc;"""

            logging.info(query)

            queryDBsendResponse(self, query, (s,l,), geojsonHeader)

            return

        # else continue as usual, i.e. serve any files from the folder
        SimpleHTTPServer.SimpleHTTPRequestHandler.do_GET(self)

def queryDBsendResponse(self, query, args, header):
    try:
        cur.execute(query, args)
        sendHeader(self, 200, header)
        row = cur.fetchone()
        self.wfile.write(row[0])
    except Exception as e:
        sendError(self, e)

def sendHeader(self, status, contentType):
    self.send_response(status)
    self.send_header('Content-type', contentType)
    self.end_headers()

def sendError(self, e):
    self.send_response(500)

    self.send_header('Content-type','text/html')
    self.end_headers()
    # Send the html message
    self.wfile.write("<h1>Internal Server Error</h1>")
    self.wfile.write(e)

    traceback.print_exc()


Handler = ServerHandler

httpd = SocketServer.TCPServer(("", PORT), Handler)

print "Serving at: http://%(interface)s:%(port)s" % dict(interface=I or "localhost", port=PORT)
httpd.serve_forever()
