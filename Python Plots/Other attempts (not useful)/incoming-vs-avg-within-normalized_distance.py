import os
import pandas as pd
import matplotlib
from matplotlib import pyplot
from matplotlib.backends.backend_pdf import PdfPages
import numpy as np

matplotlib.style.use('fivethirtyeight')

os.chdir('/Users/Carsten/Dropbox/Code/CentralPlaceWiki/Python Plots')

data = pd.read_csv('incoming-vs-avg-within-normalized_distance.csv', sep=',')

# remove extreme cases to see better what's going on inside the mess (the extreme cases are clear anyway):
# data = data[data["incoming"] < 30000]
# data = data[data["avg"] < 500]

upper = data[data["type"] == 1]
middle = data[data["type"] > 1]

# pyplot.plot(data["incoming"], data["avg"])
pyplot.scatter(np.log(middle["incoming"]), np.log(middle["avg_within_10k"]), facecolor='red')
pyplot.scatter(np.log(upper["incoming"]), np.log(upper["avg_within_10k"]))

# pyplot.scatter(middle["incoming"], middle["avg_within_10k"], facecolor='red')
# pyplot.scatter(upper["incoming"], upper["avg_within_10k"])

pyplot.xlabel('log(incoming)')
pyplot.ylabel('log(avg. of incoming within 10km)')
pyplot.legend(loc='upper right')

# pyplot.savefig('incoming-vs-avg-within-normalized_distance.pdf', bbox_inches='tight')
# pyplot.close()

pyplot.show()
