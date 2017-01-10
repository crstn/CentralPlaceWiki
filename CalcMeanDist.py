# -*- coding: utf-8 -*-

import os
import csv
import numpy as np
import psycopg2
import psycopg2.extras
import pync

conn = psycopg2.connect("dbname='cpt' host='localhost'")

# returns a list of all results returned by the SQL query
def shootSQL(sql, args):
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute(sql, args)
    rows = cur.fetchall()
    cur.close()
    return rows



inp = '/Users/Carsten/Dropbox/Code/CentralPlaceWiki/Python Plots/Incoming references - plots/All Incoming references - upper centers.csv'
out = "/Users/Carsten/Dropbox/Code/CentralPlaceWiki/Python Plots/Incoming references - plots/incoming + median dist - upper centers.csv"

fieldnames = ['page_id', 'page', 'incoming', 'mediandist']
writer = csv.DictWriter(open(out, 'w'), delimiter=',', fieldnames=fieldnames)

# with open(out, "a") as myfile:
#     myfile.write("page,incoming,mediandist")

with open(inp) as infile:
    reader = csv.DictReader(infile)

    for row in reader:
        c = row['page']
        results = shootSQL(""" SELECT p.page, l.dist_sphere_meters
                            FROM links l, pages p
                            WHERE l.to = %s
                            AND l.from =p.page
                            AND p.type = 'city'; """, [c])


        distances = []

        for r in results:
            distances.append(r[1])

        try:
            row['mediandist'] = np.median(distances)
            writer.writerow(row)
        except Exception as e:
            print e
            print c



conn.close()


pync.Notifier.notify('Number crunching complete 💥 ', title='Python')
