# -*- coding: utf-8 -*-
import re, sys, logging
from lxml import etree

reload(sys)
sys.setdefaultencoding('utf8')

import LatLon                 # conversion between degrees, minutes, seconds and decimal degrees

lang = "de"  # so that we can keep track of different languages in our DB

ns = '{http://www.mediawiki.org/xml/export-0.10/}'

# these control how many copies of this script will be started, and which of those
# this particular instance takes care of. Can be used to only parse every n-th page.
# These will be read from command line args!
global numthreads # arg 1
global thisthread # arg 2
global infile     # arg 3 - the wikipedia XML dump

global currentpage

# let's pre-compile a regex to fetch coordinates matching the pattern described here:
# https://de.wikipedia.org/wiki/Wikipedia:WikiProjekt_Georeferenzierung/Kurzanleitung
coordpattern = re.compile("\{\{coordinate[\S]*\|[a-z]*NS=*([^|\}\}]*)\|[a-z]*EW=?([^|\}\}]*)", re.IGNORECASE)

# checks if a number has decimal fractions other than .0
def isDecimal(a):
    return (round(a) != a)

# adds an insert statement to the SQL file
def addInsert(pagetitle, lat, lon, sqlfile):
    global lang

    lat = float(lat)
    lon = float(lon)

    # skip coordinates that are wrong (or on the moon or other planets ...)
    if (lat < -90.0) or (lat > 90.0) or (lon < -180.0) or (lon > 180.0):
        logging.info("coords out of bounds for " + pagetitle +": " + str(lat) +", " + str(lon))
        # raise ValueError("Coordinates out of range.")
        return

    insert = u"INSERT INTO pages VALUES ('"+pagetitle.replace("'", "''")+"', '"+lang+"', ST_SetSRID(ST_MakePoint("+str(lon)+", "+str(lat)+"),4326));\n"
    sqlfile.write(insert.encode('utf8'))

# turns strings into floats, returning 0.0 for empty strings
def replaceEmptyFloat(matchGroup):
    if len(matchGroup.strip()) == 0:
        return 0.0
    else:
        return float(matchGroup.strip())

# this is the heart of the script, parsing through the text on a wikipedia page
# for the coordinate pattern defined above, and writing them
# to the sqlfile via addinsert when one is found. Note that only the first coordinates
# for every page are found!
def findreferences(page, sqlfile):

    pagetitle = page.find(ns+'title').text
    pagetext  = page.find(ns+'revision/'+ns+'text').text

    # find all coords via regex
    try:
        coordmatch = coordpattern.search(pagetext)
    except Exception:
        logging.info("Exception caught during coord search. Empty page text?")
        return

    if coordmatch:
        # turn into a list and remove empty segments:
        latgroup  = filter(None, coordmatch.groups()[0].split('/'))
        # turn back into string with blanks as separators, removing any extra blanks
        latstring = " ".join([s.strip() for s in latgroup])
        longroup  = filter(None, coordmatch.groups()[1].split('/'))
        lonstring = " ".join([s.strip() for s in longroup])

        try:
            if len(latgroup) == 1: # decimal degrees
                coords = LatLon.string2latlon(latstring, lonstring, 'D')
            if len(latgroup) == 2: # degrees + heading
                try:
                    coords = LatLon.string2latlon(latstring, lonstring, 'd% %H')
                except:
                    # if this goes wrong, we usually have degrees and minutes,
                    # but the headings are missing. Sometimes people seem to assume
                    # we are in N / E hemispheres, so we'll do the same:
                    latgroup.extend(["N"])
                    latstring = " ".join([s.strip() for s in latgroup])
                    longroup.extend(["E"])
                    lonstring = " ".join([s.strip() for s in longroup])
                    # ... then this will be taken care of in the next case:
            if len(latgroup) == 3: # degrees, decimal minutes + heading
                try:
                    coords = LatLon.string2latlon(latstring, lonstring, 'd% %M% %H')
                except:
                    # if this goes wrong, we usually have degrees, minutes, seconds,
                    # but the headings are missing. Sometimes people seem to assume
                    # we are in N / E hemispheres, so we'll do the same:
                    latgroup.extend(["N"])
                    latstring = " ".join([s.strip() for s in latgroup])
                    longroup.extend(["E"])
                    lonstring = " ".join([s.strip() for s in longroup])
                    # ... then this will be taken care of in the next case:
            if len(latgroup) == 4: # degrees, decimal minutes + heading
                coords = LatLon.string2latlon(latstring, lonstring, 'd% %m% %S% %H')

            addInsert(pagetitle, coords.to_string('D')[0], coords.to_string('D')[1], sqlfile)

        except Exception as e:
            logging.error(pagetitle)
            logging.error(latgroup)
            logging.error(longroup)
            logging.error(e)


def go():

    currentpage = 1

    sqlfile = open("insert-"+str(thisthread)+"-of-"+str(numthreads)+"-coords.sql", "a")

    # for the parsing, we follow the approach explained here:
    # http://www.ibm.com/developerworks/xml/library/x-hiperfparse/
    pages = etree.iterparse(infile, events=('end',), tag=ns+'page')

    count = 0

    # go through wikipedia pages in dump, one by one:
    for event, page in pages:
        # print page title:
        # print page.find(ns+'title').text
        count = count +1

        # make sure we only parse every n-th page!
        if currentpage == thisthread:
            # try:
            findreferences(page, sqlfile)
            # free up some memory
            page.clear()
            # Also eliminate now-empty references from the root node to the page
            while page.getprevious() is not None:
                del page.getparent()[0]

            # except Exception as e:
            #     logging.info("Exception caught when parsing: " + page.find(ns+'title').text)
            #

        currentpage = currentpage + 1
        if currentpage > numthreads:
            currentpage = 1

    # trigger housekeeping in DB after all inserts:
    insert = u"VACUUM;\n"
    sqlfile.write(insert.encode('utf8'))

    sqlfile.close()

    logging.info(str(count) + " pages processed.")


if __name__ == "__main__":

    numthreads = int(sys.argv[1])
    thisthread = int(sys.argv[2])
    infile = sys.argv[3]

    logging.basicConfig(level=logging.INFO,
                        filename="logfile-"+str(thisthread)+"-of-"+str(numthreads)+".log",
                        filemode='w',
                        format='%(asctime)s %(levelname)-8s %(message)s')

    try:
        go()
    except Exception, e:
        logging.exception(e)

    logging.info("done")
