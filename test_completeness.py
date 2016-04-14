import psycopg2, codecs

# Try to connect
try:
    conn=psycopg2.connect("dbname='cpt'")
except:
    print "I am unable to connect to the database."

cur = conn.cursor()

f=codecs.open('centers_de.csv', 'r', encoding='utf-8')

i = 1

for place in f.readlines():

    start = 1
    end = place.find('\'', 1)

    place = place[start:end]

    #try:
    cur.execute("""SELECT DISTINCT links.fromid, links."from", geo_tags.gt_name FROM links, geo_tags WHERE links.fromid = geo_tags.gt_page_id AND (  links."from" = %s );""", (place,))

    #print cur.query

    if cur.rowcount == 0:
        print i
        i = i+1
        print place.encode('utf-8') + " not found; checking whether it's in the links table."

        cur.execute("""SELECT DISTINCT links.fromid, links."from" FROM links WHERE links."from" = %s;""", (place,))
        if cur.rowcount == 0:
            print "Nope."
        else:
            print "Looks good, seems like only the coordinates are missing."
            rows = cur.fetchall()
            for row in rows:
                print "   ", row

        print " --- "
