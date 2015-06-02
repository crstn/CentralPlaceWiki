import re                     # Regex
from lxml import etree        # XML parsing
import timeit                 # simple benachmarking
import sys                    # to read command line args

lang = "en"  # so that we can keep track of different languages in our DB

ns = '{http://www.mediawiki.org/xml/export-0.10/}'


# these control how many copies of this script will be started, and which of those 
# this particular instance takes care of. Can be used to only parse every n-th page.
# These will be read from command line args! 
global numthreads # arg 1
global thisthread # arg 2
global infile     # arg 3 - the wikipedia XML dump


global currentpage

# let's pre-compile some regexes
linkpattern = re.compile("\[\[?([^]|]*)(\|)?([^]|]*)?\]\]")
    
def findreferences(page, sqlfile):
    
    pagetitle = page.find(ns+'title').text
    pagetext  = page.find(ns+'revision/'+ns+'text').text
    
    # find all links via regex, save in a dict with the link as key and number of occurrences for this link as value
    try:
        links = linkpattern.findall(pagetext)
    except:
        print "Exception caught during link discovery."
        return

    
    # we'll go through the links in alphabetical order; whenever the lastlink is different from the current one, we'll 
    # write the accumulated count of the lastlinks to the DB:
    lastlink = None 
    lastalias = None
    linkscount = 0
    mentionscount = 0
    
    for match in sorted(links):
        link = match[0]

        theselinks = 0
        
        if link != lastlink: 
            #write to DB:
            if lastlink:  # don't write on the first iteration when lastlink is empty!
                # create statement to insert results into DB
                insert = u"INSERT INTO links VALUES ('"+pagetitle.replace("'", "''")+"', '"+lastlink.replace("'", "''")+"', '"+lang+"', "+str(linkscount)+", "+str(mentionscount)+");\n"
                sqlfile.write(insert.encode('utf8'))
                
            # and start over
            lastlink = link
            linkscount = 1
        
            # find all occurrences of the link text on the page:
            matches = re.findall(re.escape(link), pagetext)
            theselinks = len(matches)
            mentionscount = theselinks
            
        else:
            # still the same link, only update the linkscount
            linkscount = linkscount + 1

        # if there is an alias in this link, also look for its occurrences: 
        if match[2]:  # this is the alias
            alias = match[2].strip(" ")
            if len(alias) > 0: # skips empty alias, which does happen...
                # only search for appearances of this alias if it is not the same as in the last iteration!
                if alias != lastalias: 
                    lastalias = alias
                    aliasmatches = re.findall(re.escape(alias), pagetext)

                    # if the alias is a substring of the full page title, e.g. "Brooklyn, NY" and "Brooklyn"
                    # avoid double counting!
                    if alias in link:
                        mentionscount = mentionscount + len(aliasmatches) - theselinks
                    else:
                        mentionscount = mentionscount + len(aliasmatches)   
                        
    page.clear()

    # Also eliminate now-empty references from the root node to the page 
    while page.getprevious() is not None:
        del page.getparent()[0]
            
def go():
    
    numthreads = int(sys.argv[1])
    thisthread = int(sys.argv[2])
    infile = sys.argv[3]

    currentpage = 1

    sqlfile = open("insert-"+str(thisthread)+"-of-"+str(numthreads)+".sql", "a")

    # for the parsing, we follow the approach explained here: 
    # http://www.ibm.com/developerworks/xml/library/x-hiperfparse/ 
    pages = etree.iterparse(infile, events=('end',), tag=ns+'page')

    # go through wikipedia pages in dump, one by one:
    for event, page in pages:   
        
        # make sure we only parse every n-th page!
        if currentpage == thisthread:
            findreferences(page, sqlfile)
           
        currentpage = currentpage + 1
        if currentpage > numthreads:
            currentpage = 1
           
    sqlfile.close()    

if __name__ == "__main__":
    print timeit.timeit(go, 'gc.enable()', number = 1)
    print "done"