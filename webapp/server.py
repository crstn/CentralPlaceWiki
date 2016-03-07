import SimpleHTTPServer
import SocketServer
import logging
import cgi

import sys
import os

import psycopg2
from psycopg2 import extras

import json

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

try:
    conn = psycopg2.connect("dbname='cpt' host='localhost'")
except Exception as e:
    logging.error(e)

cur = conn.cursor()

class ServerHandler(SimpleHTTPServer.SimpleHTTPRequestHandler):

    def do_GET(self):
        logging.warning("======= GET STARTED =======")
        logging.warning(self.headers)
        if self.path.startswith('/search/'):
            search = self.path[8:]+"%" # last bit of the path contains the search term, plus wildcard
            try:

                cur.execute("""SELECT row_to_json(fc) FROM (SELECT array_to_json(array_agg(f)) As results FROM (SELECT page_id, page FROM pages WHERE ( page LIKE %s ) AND incoming > 0 AND the_geom IS NOT NULL ORDER BY incoming DESC limit 10) AS f ) AS fc;""", (search,))

                sendHeader(self, 200, 'application/json; charset=utf-8')

                row = cur.fetchone()
                self.wfile.write(row[0])

            except Exception as e:
                sendError(self, e)

            return

        elif self.path.startswith('/place/'):
            try:
                s = int(self.path[7:]) # last bit of the path contains the page id we'll look for
                cur.execute("""SELECT row_to_json(fc) FROM ( SELECT 'FeatureCollection' As type, array_to_json(array_agg(f)) As features FROM (SELECT 'Feature' As type, ST_AsGeoJSON(lg.the_geom)::json As geometry, row_to_json(lp) As properties FROM pages As lg INNER JOIN (SELECT page_id, page FROM pages WHERE page_id = %s AND the_geom IS NOT NULL) As lp ON lg.page_id = lp.page_id  ) As f ) As fc;""", (s,))

                sendHeader(self, 200, 'application/vnd.geo+json; charset=utf-8')

                row = cur.fetchone()
                self.wfile.write(row[0])

            except Exception as e:
                sendError(self, e)

            return
        # else continue as usual, i.e. serve any files from the folder
        SimpleHTTPServer.SimpleHTTPRequestHandler.do_GET(self)

# def searchPlace(self, s):

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

    logging.error(e)


Handler = ServerHandler

httpd = SocketServer.TCPServer(("", PORT), Handler)

print "Serving at: http://%(interface)s:%(port)s" % dict(interface=I or "localhost", port=PORT)
httpd.serve_forever()
