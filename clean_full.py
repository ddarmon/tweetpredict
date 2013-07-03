# This script removes the 'bad' days from the
# time series data for the 15K network. Before
# this script, I did this manually in the
# coarsening step.
#
#	DMD 030713-11-31

import ipdb
import numpy
import pylab
import datetime
import random
import glob

from extract_timeseries_methods import *

from filter_data_methods import *

start = 0
K = 3000-start

users = get_K_users(K = K, start = start)

for index, user in enumerate(users):
	print 'Working on user {} with user id {}...'.format(start + index, users[start+index])
	ofile = open('timeseries_alldays/byday-1s-{}.dat'.format(user))

	ires = 1

	# wfile = open('timeseries_alldays/byday-{}s-{}.dat'.format(ires, user), 'w')
	wfile = open('timeseries_clean/byday-{}s-{}.dat'.format(ires, user), 'w')

	for ind, line in enumerate(ofile):
		# For now, remove days 11 through 23
		# and days 62 through 68. These days
		# have gaps in them for certain 
		# databases.

		if (11 <= ind <= 23) or (62 <= ind <= 68):
			pass
		else:
			wfile.write(line)

	wfile.close()

	ofile.close()