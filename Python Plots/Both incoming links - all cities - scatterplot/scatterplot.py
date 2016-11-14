import os
import pandas as pd
import matplotlib
from matplotlib import pyplot
from matplotlib.backends.backend_pdf import PdfPages
import numpy as np

matplotlib.style.use('fivethirtyeight')

os.chdir('/Users/Carsten/Dropbox/Code/CentralPlaceWiki/Python Plots/Both incoming links - all cities - scatterplot')

cities = pd.read_csv('Both incoming - all cities.csv', sep=',')
upper  = pd.read_csv('Both incoming - upper centers.csv', sep=',')
middle = pd.read_csv('Both incoming - middle centers.csv', sep=',')

# make 0.1 step bins from 0 to 15:
ints = range(0,150,1)
bins = [ (float(x)/10.0) for x in ints ]

props = dict(alpha=0.5, edgecolors='none' )

pyplot.scatter(np.log(cities['incoming_from_cities']), np.log(cities['incoming']),  label='All cities', color='008fd5', **props)
pyplot.scatter(np.log(middle['incoming_from_cities']), np.log(middle['incoming']),  label='Middle centers', color='fc4f30', **props)
pyplot.scatter(np.log(upper['incoming_from_cities']), np.log(upper['incoming']),  label='Upper centers', color='e5ae38', **props)


pyplot.xlabel('incoming references from cities (log scale)')
pyplot.ylabel('all incoming references (log scale)')
pyplot.legend(loc='lower right')

pyplot.savefig('scatterplot.pdf', bbox_inches='tight')
pyplot.close()

# pyplot.show()
