# -*- coding: utf-8 -*-

import psycopg2
import psycopg2.extras
import pprint
import numpy as np
import csv
import matplotlib
import matplotlib.pyplot as plt

conn = psycopg2.connect("dbname='cpt' host='localhost'")


# ====================
#
# some lil' helpers
#
# ====================

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

# ============================================================
#
# here's where the thing happens ✨
#
# ============================================================


# uppers = getUpperCenters()
# mostlinked = getMostLinkedCities(250)
#
# printStats(mostlinked, uppers)

# # uppers = ['Münster (Westfalen)', 'Osnabrück']
# recalls = []
#
# for place in uppers:
#
#     sizes = [6]
#
#     for size in sizes:
#         c = getNClosestMiddleCenters(place, size)
#         s = getNStrongestLinkers(place, size)
#
#         print "Closest "+str(size)+" centers for "+place+":\n" + printableSet(c)
#         print str(size)+" Cities with highest number of links for "+place+":\n"+printableSet(s)
#
#         printStats(s, c)
#
#         print " "
#
#         recalls.append(recall(s, c))
#
# r = np.array(recalls)
#
# print "Avg recall: " + str(np.average(r))
# print "Max recall: " + str(np.max(r))

#


einwohner = dict()

with open('bw.csv') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        if row['State'] not in einwohner:
            einwohner[row['State']] = dict()

        einwohner[row['State']][row['Name']] = int(row['Einwohner'].replace(".", ""))

# pprint.pprint(einwohner)



cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
cur.execute("""select city, state, incoming from centers_de, pages where state = 'Baden-Württemberg' and page = city;""")

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
        print city+": " + str(einwohner[state][city]) + ", " + str(incoming)
        inc.append(incoming)
        pop.append(einwohner[state][city])

inc, pop = sortBoth(inc, pop)

inc = np.array(inc)
pop = np.array(pop)

polynomial = np.poly1d(np.polyfit(inc,pop,2))

# Feed data into pyplot.
xpoints = np.linspace(0.0, np.max(pop), 100)
# xpoints = np.linspace(0.0, 100000, 100)
plt.plot(inc,pop,'x',xpoints,polynomial(xpoints),'-')
# plt.plot(inc,pop,'x')


# m, b = np.polyfit(inc, pop, 1)
#
# plt.plot(inc, pop, ".")
# plt.plot(inc, m*pop + b, "-", linewidth = 1.0)

plt.suptitle("Incoming links vs population")
plt.savefig("incoming_vs_pop.pdf")

plt.clf()


conn.close()
