import SimpleHTTPServer
import SocketServer
import logging
import cgi

import sys
import os

import psycopg2

if len(sys.argv) > 2:
    PORT = int(sys.argv[2])
    I = sys.argv[1]
elif len(sys.argv) > 1:
    PORT = int(sys.argv[1])
    I = ""
else:
    PORT = 8089
    I = ""

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
            try:
                search = self.path[8:]+"%" # last bit of the path contains the search term, plus wildcard
                cur.execute("""SELECT page_id, page FROM pages WHERE ( page LIKE %s ) AND incoming > 0 AND the_geom IS NOT NULL ORDER BY incoming DESC limit 10;""", (search,))
                self.send_response(200)
        #        self.send_header('Content-type','application/vnd.geo+json')
                self.send_header('Content-type','text/html; charset=utf-8')
                self.end_headers()
        		# Send the html message
                rows = cur.fetchall()

                for row in rows:
                    self.wfile.write(row[1]+" ("+str(row[0])+")"+"<br />")

            except Exception as e:

                self.send_response(500)

                self.send_header('Content-type','text/html')
                self.end_headers()
        		# Send the html message
                self.wfile.write("<h1>Internal Server Error</h1>")
                self.wfile.write(e)

                logging.error(e)

            return
        elif self.path.startswith('/placelinks/'):
            try:
                id = int(self.path[12:]) # last bit of the path contains the page id we'll look for
                cur.execute("""SELECT row_to_json(fc) FROM ( SELECT 'FeatureCollection' As type, array_to_json(array_agg(f)) As features FROM (SELECT 'Feature' As type, ST_AsGeoJSON(lg.the_geom)::json As geometry, row_to_json(lp) As properties FROM pages As lg INNER JOIN (SELECT page_id, page FROM pages WHERE page_id = %id AND the_geom IS NOT NULL) As lp ON lg.page_id = lp.page_id  ) As f ) As fc;""", (id,))

                row = cur.fetchone()
                self.wfile.write(row[0])

            except Exception as e:

                self.send_response(500)

                self.send_header('Content-type','text/html')
                self.end_headers()
        		# Send the html message
                self.wfile.write("<h1>Internal Server Error</h1>")
                self.wfile.write(e)

                logging.error(e)

            return
        # else continue as usual, i.e. serve any files from the folder
        SimpleHTTPServer.SimpleHTTPRequestHandler.do_GET(self)

    # def do_POST(self):
    #     logging.warning("======= POST STARTED =======")
    #     # logging.warning(self.headers)
    #     form = cgi.FieldStorage(
    #         fp=self.rfile,
    #         headers=self.headers,
    #         environ={'REQUEST_METHOD':'POST',
    #                  'CONTENT_TYPE':self.headers['Content-Type'],
    #                  })
    #     logging.warning("======= POST VALUES =======")
    #     # for item in form.list:
    #     #     logging.warning(item)
    #
    #     session = form.getvalue('session')
    #
    #     directory = 'experiments/'+session
    #
    #     if not os.path.exists(directory):
    #         os.makedirs(directory)
    #
    #     # this is to process the final questionnaire:
    #     if(form.getvalue('q') == 't'):
    #         header = ""
    #         values = ""
    #
    #         for key in form.keys():
    #             header += str(key)+", "
    #             values += str(form.getvalue(str(key)))+", "
    #
    #         with open("experiments/questionnaires.csv", "a") as text_file:
    #                 text_file.write(header+"\n")
    #                 text_file.write(values+"\n")
    #
    #         # redirect to thank you page
    #         self.send_response(301)
    #         self.send_header('Location','http://localhost:8000/thanks.html')
    #         self.end_headers()
    #
    #     # this process the randomized car json datasets
    #     else:
    #         data = form.getvalue('data')
    #         page = form.getvalue('page')
    #
    #         with open(directory+"/"+page+".json", "w") as text_file:
    #             text_file.write(data)
    #
    #         logging.warning("\n")
    #         SimpleHTTPServer.SimpleHTTPRequestHandler.do_GET(self)

Handler = ServerHandler

httpd = SocketServer.TCPServer(("", PORT), Handler)

print "Serving at: http://%(interface)s:%(port)s" % dict(interface=I or "localhost", port=PORT)
httpd.serve_forever()
