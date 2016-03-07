import psycopg2, codecs

# This is similar to test-completeness, but this time on the pages table

# Try to connect
try:
    conn=psycopg2.connect("dbname='cpt'")
except:
    print "I am unable to connect to the database."

cur = conn.cursor()

f=codecs.open('DE_CPT_Hierarchy.txt', 'r', encoding='utf-8')

for place in f.readlines():

    place = place[:-1] # strip the \N from the end

    #try:
    cur.execute("""SELECT * FROM pages WHERE (  page = %s );""", (place,))

    # print cur.query

    if cur.rowcount == 0:
        print place.encode('utf-8') + " not found; checking whether it's in the links table."
    else:
        print str(cur.rowcount) + " row(s) found for " + place.encode('utf-8')
