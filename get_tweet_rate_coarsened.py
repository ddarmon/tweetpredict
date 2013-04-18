import numpy
import collections
import sys

from filter_data_methods import *

from traintunetest import create_traintunetest

users = get_top_K_users(3000)

for user_num in range(0, 10):
	user_id = users[user_num]

	suffix = user_id

	fname = 'timeseries_alldays/byday-600s-{}.dat'.format(suffix)

	ofile = open(fname)

	line = ofile.readline().rstrip('\n')

	# The number of bins. This is the number of 
	# *already coarsened* bins, so this isn't a
	# *true* tweet rate of tweets / unit time.

	num_bins = len(line)

	daycount = 0

	onecount = 0 # A counter for the number of 1s across
				 # all of the days.

	while line != '':
		for character in line:
			if character == '1':
				onecount += 1

		daycount += 1

		line = ofile.readline()

	ofile.close()

	print onecount/float(daycount*num_bins)