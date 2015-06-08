# -*- coding: utf-8 -*-
import re                     # Regex
from lxml import etree        # XML parsing
import timeit                 # simple benachmarking
import sys                    # to read command line args
import LatLon                 # conversion between degrees, minutes, seconds and decimal degrees 

lang = "en"  # so that we can keep track of different languages in our DB

ns = '{http://www.mediawiki.org/xml/export-0.10/}'

# these control how many copies of this script will be started, and which of those 
# this particular instance takes care of. Can be used to only parse every n-th page.
# These will be read from command line args! 
global numthreads # arg 1
global thisthread # arg 2
global infile     # arg 3 - the wikipedia XML dump

global currentpage

global logfile

# let's pre-compile some regexes (crazy long, huh?)
coordpattern = re.compile("\{\{coord\|?([^|\}\}]*)\|?([^|\}\}]*)(?:\|?([^|\}\}]*))?(?:\|?([^|\}\}]*))?(?:\|?([^|\}\}]*))?(?:\|?([^|\}\}]*))?(?:\|?([^|\}\}]*))?(?:\|?([^|\}\}]*))?", re.IGNORECASE)

# if written as latitude = 42° 26' 36'' N
latcompletepattern  = re.compile(u"\|\s*(?:lat|latitude|latd|lat_d|lat\_degrees)\s*\=\s*([^\|\s°]*)°\s*([^\|\s']*)'\s*([^\|\s'']*)''\s*([^\|\s]*)", re.IGNORECASE)
longcompletepattern = re.compile(u"\|\s*(?:long|longitude|longd|long_d|long\_degrees)\s*\=\s*([^\|\s°]*)°\s*([^\|\s']*)'\s*([^\|\s'']*)''\s*([^\|\s]*)", re.IGNORECASE)

# if separated as degree, minute, second, heading:
latdpattern  = re.compile("\|\s*(?:lat|latitude|latd|lat_d|lat\_degrees)\s*\=\s*([^\|\s\}\)>]*)", re.IGNORECASE)
latmpattern  = re.compile("\|\s*(?:latm|lat_m|lat\_minutes)\s*\=\s*([^\|\s]*)", re.IGNORECASE)
latspattern  = re.compile("\|\s*(?:lats|lat_s|lat\_seconds)\s*\=\s*([^\|\s]*)", re.IGNORECASE)
lathpattern  = re.compile("\|\s*(?:latns|lat\_ns|lat\_direction)\s*\=\s*(\w)", re.IGNORECASE)

longdpattern = re.compile("\|\s*(?:long|longitude|longd|long_d|long\_degrees)\s*\=\s*([^\|\s\}\)>]*)", re.IGNORECASE)
longmpattern = re.compile("\|\s*(?:longm|long_m|long\_minutes)\s*\=\s*([^\|\s]*)", re.IGNORECASE)
longspattern = re.compile("\|\s*(?:longs|long_s|long\_seconds)\s*\=\s*([^\|\s]*)", re.IGNORECASE)
longhpattern = re.compile("\|\s*(?:longew|long\_ew|long\_direction)\s*\=\s*(\w)", re.IGNORECASE)

# conveniece logging function
def logme(text):
    global logfile
    logfile.write(text.encode("UTF-8")+"\n")

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
        logme("coords out of bounds for " + pagetitle +": " + str(lat) +", " + str(lon))
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
# for the different coordinate patterns defined above, and writing them
# to the sqlfile via addinsert when one is found. Note that only the first coordinates
# for every page are found!
def findreferences(page, sqlfile):

    pagetitle = page.find(ns+'title').text
    pagetext  = page.find(ns+'revision/'+ns+'text').text
    
    # find all coords via regex
    try:
        coordmatch = coordpattern.search(pagetext) 
    except Exception:
        logme("Exception caught during coord search. Empty page text?")
        return

    #sqlfile.write(pagetitle.encode('utf8')+"\n")

    if coordmatch:
        #sqlfile.write(u" --- coords: " + str(coordmatch.group()) + "\n"); 
        
        # figure out if the string contains heading directions and if it does,
        # where they are:
        i = 1
        lath = "N"
        lathindex = 0
        longh = "W"
        longhindex = 0

        for part in coordmatch.groups():
            if part == "N" or part == "S":
                lathindex = i
            if part == "W" or part == "E":
                longhindex = i
            i = i+1

        #sqlfile.write("lathindex: " + str(lathindex) + ", longhindex: " + str(longhindex) + "\n") 

        # first handle the cases where we don't have headings        
        if lathindex == 0 and longhindex == 0:
            try:
                addInsert(pagetitle, str(float(coordmatch.group(1))), str(float(coordmatch.group(2))), sqlfile)
            except Exception:
                pass
            return

        # if we have headings, we have three different cases:
        # 1. just degrees
        if lathindex == 2 and longhindex == 4:  # continue here!
            latstring  = str(coordmatch.group(1)).strip() + " " + str(coordmatch.group(2)).strip()
            longstring = str(coordmatch.group(3)).strip() + " " + str(coordmatch.group(4)).strip()
            
            # just to check: 
            # sqlfile.write(latstring +" "+ longstring+ "\n")

            coords = LatLon.string2latlon(latstring, longstring, 'd% %H')

            # finally...
            addInsert(pagetitle, coords.to_string('D')[0], coords.to_string('D')[1], sqlfile)

            return
        # 2. degress + minutes
        if lathindex == 3 and longhindex == 6:  # continue here!
            latstring = str(coordmatch.group(1)).strip() + " " + str(float(coordmatch.group(2))).strip() + " " + str(coordmatch.group(3)).strip()
            longstring = str(coordmatch.group(4)).strip() + " " + str(float(coordmatch.group(5))).strip() + " " + str(coordmatch.group(6)).strip()
            
            # just to check: 
            # sqlfile.write(latstring +" "+ longstring+ "\n")

            coords = LatLon.string2latlon(latstring, longstring, 'd% %m% %H')

            # finally...
            addInsert(pagetitle, coords.to_string('D')[0], coords.to_string('D')[1], sqlfile)
        # 3. degrees + minutes + seconds
        if lathindex == 4 and longhindex == 8:  # continue here!
            
            latstring = str(coordmatch.group(1)).strip() + " " + str(replaceEmptyFloat(coordmatch.group(2))) + " " + str(replaceEmptyFloat(coordmatch.group(3))) + " "+ str(coordmatch.group(4)).strip()
            longstring = str(coordmatch.group(5)).strip() + " " + str(replaceEmptyFloat(coordmatch.group(6))) + " " + str(replaceEmptyFloat(coordmatch.group(7))) + " "+ str(coordmatch.group(8)).strip()

            coords = LatLon.string2latlon(latstring, longstring, 'd% %m% %S% %H')

            # finally...
            addInsert(pagetitle, coords.to_string('D')[0], coords.to_string('D')[1], sqlfile)
        
        return
    
    latcompletematch  = latcompletepattern.search(pagetext)
    longcompletematch = longcompletepattern.search(pagetext)

    if latcompletematch and longcompletematch:
        latstring = latcompletematch.group(1) + " " + latcompletematch.group(2) + " " +latcompletematch.group(3) + " " + latcompletematch.group(4)
        longstring = longcompletematch.group(1) + " " + longcompletematch.group(2) + " " +longcompletematch.group(3) + " " + longcompletematch.group(4)

        coords = LatLon.string2latlon(latstring, longstring, 'd% %m% %S% %H')
        addInsert(pagetitle, coords.to_string('D')[0], coords.to_string('D')[1], sqlfile)
        
        return

    # try other patterns:
    latdmatch = latdpattern.search(pagetext)
    longdmatch = longdpattern.search(pagetext)

    if latdmatch and longdmatch:
        
        # skip if the coordinates are empty:
        if len(latdmatch.group(1).strip()) == 0 or len(longdmatch.group(1).strip()) == 0:
            return
        
        latd = float(latdmatch.group(1));
        longd = float(longdmatch.group(1));
        
        # do we heave a heading?
        lathmatch = lathpattern.search(pagetext)
        longhmatch = longhpattern.search(pagetext)

        if(lathmatch and longhmatch):
            lath = str(lathmatch.group(1))
            lonh = str(longhmatch.group(1))
        else:
            # print "no heading found for ", pagetitle
            if str(latd)[0] == "-":
                lath = "S"
            else:
                lath  = "N"

            if str(longd)[0] == "-":
                lonh = "W"
            else:
                lonh = "E"
        
        # if they are already decimals, we are done:
        if isDecimal(latd) and isDecimal(longd):  
            latstring  = str(latd)  + " " + lath
            longstring = str(longd) + " " + lonh
            
            coords = LatLon.string2latlon(latstring, longstring, 'd% %H')

            # finally...
            addInsert(pagetitle, coords.to_string('D')[0], coords.to_string('D')[1], sqlfile)          
            return

        # do we have minutes?
        latmmatch = latmpattern.search(pagetext)
        longmmatch = longmpattern.search(pagetext)

        if(latmmatch and longmmatch):
            try:
                latm  = float(latmmatch.group(1))
                longm = float(longmmatch.group(1))
            except: #if that goes wrong, assume we have no minutes:
                # print "Error trying to convert string to float - latm: " + str(latmmatch.group() + ", lonm: " + longmmatch.group()) # TODO - remove
                latstring  = str(latd)  + " " + lath
                longstring = str(longd) + " " + lonh
                
                coords = LatLon.string2latlon(latstring, longstring, 'd% %H')

                # finally...
                addInsert(pagetitle, coords.to_string('D')[0], coords.to_string('D')[1], sqlfile)          
                return

        else:
            latstring  = str(latd)  + " " + lath
            longstring = str(longd) + " " + lonh
            
            coords = LatLon.string2latlon(latstring, longstring, 'd% %H')

            # finally...
            addInsert(pagetitle, coords.to_string('D')[0], coords.to_string('D')[1], sqlfile)          
            return

        # do we have seconds?

        lats = 0.0
        longs = 0.0

        latsmatch = latspattern.search(pagetext)
        longsmatch = longspattern.search(pagetext)

        if(latsmatch and longsmatch):
            try:
                lats = float(latsmatch.group(1))
                longs = float(longsmatch.group(1))
            except Exception:
                #logme("Error trying to convert string to float - lats: " + str(latsmatch.group() + ", lons: " + longsmatch.group())) # TODO - remove            
                pass
            
        #sqlfile.write(u"'" + str(int(latd)) + " " + str(latm) + " " + str(lats) + " " + lath + "', '" + str(int(longd)) + " " + str(longm) + " " + str(longs) + " " + lonh + "'\n")

        latstring = str(int(latd)) + " " + str(latm) + " " + str(lats) + " " + lath
        longstring = str(int(longd)) + " " + str(longm) + " " + str(longs) + " " + lonh
        
        # just to check: sqlfile.write(latstring +" "+ longstring+ "\n")

        coords = LatLon.string2latlon(latstring, longstring, 'd% %m% %S% %H')

        # finally...
        addInsert(pagetitle, coords.to_string('D')[0], coords.to_string('D')[1], sqlfile)

                                     
def go():
    
    global logfile

    numthreads = int(sys.argv[1])
    thisthread = int(sys.argv[2])
    infile = sys.argv[3]

    currentpage = 1

    sqlfile = open("insert-"+str(thisthread)+"-of-"+str(numthreads)+"-coords.sql", "a")

    logfile = open("logfile-"+str(thisthread)+"-of-"+str(numthreads)+".txt", "a")

    # for the parsing, we follow the approach explained here: 
    # http://www.ibm.com/developerworks/xml/library/x-hiperfparse/ 
    pages = etree.iterparse(infile, events=('end',), tag=ns+'page')

    # go through wikipedia pages in dump, one by one:
    for event, page in pages:   
        
        # make sure we only parse every n-th page!
        if currentpage == thisthread:
            try:
                findreferences(page, sqlfile)
                # free up some memory
                page.clear()
                # Also eliminate now-empty references from the root node to the page 
                while page.getprevious() is not None:
                    del page.getparent()[0]
                
            except Exception as e:
                logme("Exception caught when parsing: " + page.find(ns+'title').text)
                # logme(page.find(ns+'revision/'+ns+'text').text)
           
        currentpage = currentpage + 1
        if currentpage > numthreads:
            currentpage = 1
           
    sqlfile.close()    

if __name__ == "__main__":
    logme(str(timeit.timeit(go, 'gc.enable()', number = 1)))
    logme("done")