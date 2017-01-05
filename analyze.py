# -*- coding: utf-8 -*-

import psycopg2
import psycopg2.extras
import pprint
import numpy as np
import csv
import matplotlib
import matplotlib.pyplot as plt
import urllib2
import scipy.stats as stat
import pync

conn = psycopg2.connect("dbname='cpt' host='localhost'")


# ====================
#
# some lil' helpers
#
# ====================

# fetches the population number for the place name from Wikipedia
def getPopForPlace(place):
    data = urllib2.urlopen("https://de.wikipedia.org/wiki/"+place)
    page =  data.read()

    parts  = page.split('<td>Einwohner:</td>')
    parts = parts[1].split('<td style="line-height: 1.2em;">')
    parts = parts[1].split('<')

    popstring = parts[0]

    return int(popstring.replace(".", ""))

def getAllPopNumbers():
    with open('popDE.csv', 'w') as csvfile:
        fieldnames = ['state', 'city', 'pop']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()

        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cur.execute("""select city, state from centers_de, pages where page = city;""")

        rows = cur.fetchall()

        for row in rows:
            try:
                p = getPopForPlace(row[0])
            except Exception as e:
                p = -1
                print row[0] + ", " + row[1] + " failed"

            print p
            writer.writerow({'state': row[1], 'city': row[0], 'pop': p})


# returns a list of all results returned by the SQL query
def shootSQL(sql):
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute(sql)
    rows = cur.fetchall()
    cur.close()
    return rows


# returns a dictionary of all centers a la {'name': level}
def getAllCenters():
    centers = dict()

    rows = shootSQL("""SELECT city, type
                       FROM centers_de;""")

    for row in rows:
        centers[row["city"]] = row["type"]
    return centers


# returns a list of all upper centers
def getUpperCenters():
    centers = []

    rows = shootSQL("""SELECT city
                       FROM centers_de
                       WHERE type = 1;""")

    for row in rows:
        centers.append(row["city"])
    return centers

# returns a dictionary of all upper centers a la {'name': level}
def getMiddleCenters():
    centers = []

    rows = shootSQL("""SELECT city, type
                       FROM centers_de
                       WHERE type > 1;""")

    for row in rows:
        centers.append(row["city"])
    return centers


# jaccard index of two lists (of city names in our case):
def jaccard(a, b):
    a = set(a)
    b = set(b)
    c = a.intersection(b)
    return float(len(c)) / (len(a) + len(b) - len(c))

def precision(found, reference):
    found = set(found)
    reference = set(reference)
    inter = found.intersection(reference)
    return float(len(inter))/float(len(found))

def recall(found, reference):
    found = set(found)
    reference = set(reference)
    inter = found.intersection(reference)
    return float(len(inter))/float(len(reference))

def f1(found, reference):
    p = precision(found, reference)
    r = recall(found, reference)

    # avoid division by 0 if precision and recall are both 0:
    if p + r == 0.0:
        return 0.0
    else:
        return 2.0 * ((p * r) / (p + r))


def printStats(found, reference):
    # if found and referencde have the same length, the
    # three values will be all the same:
    if (len(found) == len(reference)):
        print "Recall/Precision/F1:    " + str(recall(found, reference))
    else:
        print "Recall:    " + str(recall(found, reference))
        print "Precision: " + str(precision(found, reference))
        print "F1:        " + str(f1(found, reference))


# fetches the N clostest middle centers to the given upper center
def getNClosestMiddleCenters(upper, n):
    middle = set()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    cur.execute("""SELECT DISTINCT c2.city, ST_Distance(p1.the_geom, p2.the_geom)
           FROM pages p1, pages p2, centers_de c1, centers_de c2
           WHERE c1.city = '%s'
           AND c1.city = p1.page
           AND c2.city = p2.page
           AND c2.type > 1
           ORDER BY ST_Distance(p1.the_geom, p2.the_geom)
           LIMIT %s;""" % (upper, n))

    rows = cur.fetchall()
    for row in rows:
        # print row[0] + " -> " + upper
        middle.add(row[0])

    return middle


# fetches the n cities with the highest numbers of links to n
def getNStrongestLinkers(place, n):

    strongest = set()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    cur.execute("""SELECT links."from"
           FROM links, pages
           WHERE links.to = '%s'
           AND pages.page_id = links.fromid
           AND pages.type = 'city'
           ORDER BY links.mentions DESC
           LIMIT %s;""" % (place, n))

    rows = cur.fetchall()
    for row in rows:
        # print row[0] + " -> " + u
        strongest.add(row[0])

    return strongest


# returns the n most linked cities as a set
def getMostLinkedCities(n):

    mostlinked = set()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    cur.execute("""select page
                    from pages
                    where type = 'city'
                    and incoming > 0
                    and country = 'DE'
                    order by incoming desc
                    limit %s;""" % (n))

    rows = cur.fetchall()
    for row in rows:
        # print row[0] + " -> " + u
        mostlinked.add(row[0])

    return mostlinked



def printableSet(s):
    st = ""
    for p in sorted(s):
        st = st + "'" + p + "' "

    return st


def sortBoth(a, b):
    newa = []
    newb = []

    # repeat until the input list is empty:
    while a:
        i = a.index(min(a))
        newa.append(a[i])
        newb.append(b[i])
        del a[i]
        del b[i]

    return newa, newb




def findMedianDistance():
    rows = shootSQL("""SELECT l.to, l.from, l.dist_sphere_meters
                       FROM centers_de c, pages pf, pages pt, links l
                       WHERE c.type = 1
                       AND c.city = pt.page
                       AND pt.page_id = l.toid
                       AND pf.page_id = l.fromid
                       AND pf.type = 'city'
                       AND l.dist_sphere_meters > 0;""")


    distances1 = []

    for row in rows:
        distances1.append(row[2])

    print "Median distance for incoming links to upper centers: " + str(np.median(distances1) / 1000.0)
    print "Mean distance for incoming links to upper centers: " + str(np.mean(distances1) / 1000.0)



    # repeat for middle centers

    rows = shootSQL("""SELECT l.to, l.from, l.dist_sphere_meters
                       FROM centers_de c, pages pf, pages pt, links l
                       WHERE c.type > 1
                       AND c.city = pt.page
                       AND pt.page_id = l.toid
                       AND pf.page_id = l.fromid
                       AND pf.type = 'city'
                       AND l.dist_sphere_meters > 0;""")


    distances2 = []

    for row in rows:
        distances2.append(row[2])

    print "Median distance for incoming links to middle centers: " + str(np.median(distances2) / 1000.0)
    print "Mean distance for incoming links to middle centers: " + str(np.mean(distances2) / 1000.0)


    # repeat once again for all cities

    rows = shootSQL("""SELECT l.to, l.from, l.dist_sphere_meters
                       FROM pages pf, pages pt, links l
                       WHERE pt.type  = 'city'
                       AND pf.type    = 'city'
                       AND pt.page_id = l.toid
                       AND pf.page_id = l.fromid
                       AND l.dist_sphere_meters > 0
                       AND pt.page NOT IN (SELECT city FROM centers_de) ;""")


    distances3 = []

    for row in rows:
        distances3.append(row[2])

    print "Median distance for incoming links to all non-center cities: " + str(np.median(distances3) / 1000.0)
    print "Mean distance for incoming links to all non-center cities: " + str(np.mean(distances3) / 1000.0)


    # make a box plot of all 3 for comparison
    data = [np.divide(distances1, 1000.0), np.divide(distances2, 1000.0), np.divide(distances3, 1000.0)]

    ax = plt.subplot(1, 1, 1)

    ax.boxplot(data, labels=["Upper Centers", "Middle Centers", "Other Cities"])

    axes = plt.gca()
    axes.set_ylim([0,250])

    plt.suptitle("Distances to linking cities in KM")

    plt.savefig("boxplot_distances.pdf")

    plt.clf()




def plotPopVsIncoming():

    einwohner = dict()

    with open('popDEcomplete.csv') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            if row['state'] not in einwohner:
                einwohner[row['state']] = dict()

            einwohner[row['state']][row['city']] = int(row['pop'])


    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute("""select city, state, incoming from centers_de, pages where page = city;""")

    rows = cur.fetchall()

    inc = []
    pop = []

    for row in rows:

        city = row[0]
        state = row[1]
        incoming = row[2]

        if city not in einwohner[state]:
             print city + " not in Pop figures"
        else:
            # print city+": " + str(einwohner[state][city]) + ", " + str(incoming)
            inc.append(incoming)
            pop.append(einwohner[state][city])

    inc, pop = sortBoth(inc, pop)

    print stat.pearsonr(inc, pop)

    inc = np.log(np.array(inc))
    pop = np.log(np.array(pop))

    matplotlib.style.use("fivethirtyeight")

    plt.plot(pop, np.poly1d(np.polyfit(pop, inc, 1))(pop), linewidth = 1.0)
    plt.plot(pop, inc, ".")


    plt.suptitle("Incoming references vs population")

    plt.xlabel('Population')
    popticks = np.log(np.array([100,1000,10000,100000,1000000,4000000]))
    popticklabels = np.array(["100", "1k", "10k","100k","1m","4m"])
    plt.xticks(popticks, popticklabels)

    plt.ylabel('Incoming references')
    incticks = np.log(np.array([100,1000,10000,100000,700000]))
    incticklabels = np.array(["100", "1k", "10k", "100k", "700k"])
    plt.yticks(incticks, incticklabels)

    plt.savefig("incoming_vs_pop.pdf")

    plt.clf()

# ============================================================
#
# here's where the thing happens ✨
#
# ============================================================

findMedianDistance()

# uppers = getUpperCenters()
# mostlinked = getMostLinkedCities(250)
#
# printStats(mostlinked, uppers)

# uppers = ['Hamburg', 'Osnabrück', 'Berlin']
# steps = []
#
# for place in uppers:
#
#     print place
#
#     size = 6
#     rec = 0.0
#
#     while rec < 1.0:
#         size = size * 2
#         c = getNClosestMiddleCenters(place, 6)
#         s = getNStrongestLinkers(place, size)
#
#         # print "Closest "+str(size)+" centers for "+place+":\n" + printableSet(c)
#         # print str(size)+" Cities with highest number of links for "+place+":\n"+printableSet(s)
#         #
#         # printStats(s, c)
#         #
#         # print " "
#         rec = recall(s, c)
#         print str(size) + ": "+str(rec)
#
#     steps.append(size)
#
# r = np.array(steps)
#
# print "Avg steps: " + str(np.average(r))
# print "Max steps: " + str(np.max(r))
#
# #




conn.close()


pync.Notifier.notify('Number crunching complete 💥 ', title='Python')
