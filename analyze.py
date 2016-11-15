# -*- coding: utf-8 -*-

import psycopg2
import psycopg2.extras
import pprint
import numpy as np

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
    print "Recall:    " + str(recall(found, reference))

    # No point in printing those – as long as both sets have
    # the same length, the values will all be the same.
    # print "Precision: " + str(precision(found, reference))
    # print "F1:        " + str(f1(found, reference))


# fetches the N clostest middle centers to the given upper center
def getNClosestMiddleCenters(upper, n):
    middle = set()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    cur.execute("""SELECT c2.city
           FROM pages p1, pages p2, centers_de c1, centers_de c2
           WHERE c1.city = '%s'
           AND c1.city = p1.page
           AND c2.city = p2.page
           AND c2.type > 1
           ORDER BY ST_Distance(p1.the_geom, p2.the_geom)
           LIMIT %s;""" % (upper, n))

    rows = cur.fetchall()
    for row in rows:
        # print row[0] + " -> " + u
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


def printableSet(s):
    st = ""
    for p in sorted(s):
        st = st + "'" + p + "' "

    return st

# ============================================================
#
# here's where the thing happens ✨
#
# ============================================================



for place in getUpperCenters():

    sizes = [6]

    for size in sizes:
        c = getNClosestMiddleCenters(place, size)
        s = getNStrongestLinkers(place, size)

        print "Closest "+str(size)+" centers for "+place+":\n" + printableSet(c)
        print str(size)+" Cities with highest number of links for "+place+":\n"+printableSet(s)

        printStats(s, c)

        print " "


conn.close()
