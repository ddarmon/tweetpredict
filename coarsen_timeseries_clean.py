# This script coarsens the *clean* files, where
# 'clean' means the time series where we remove
# the bad days where the servers didn't appear
# to be working appropriately.
#
#	DMD 030713-11-32

import ipdb
import numpy
import pylab
import datetime
import random
import glob

from extract_timeseries_methods import *

from filter_data_methods import *

year = '2011'

start = 0
K = 3000-start

users = get_K_users(K = K, start = start, year = year)

for index, user in enumerate(users):
	print 'Working on user {} ...'.format(start + index)
	ofile = open('timeseries/byday-1s-{}.dat'.format(user))

	ires = 60*10

	# wfile = open('timeseries_alldays/byday-{}s-{}.dat'.format(ires, user), 'w')
	wfile = open('timeseries/byday-{}s-{}.dat'.format(ires, user), 'w')

	for ind, line in enumerate(ofile):
		# For now, remove days 11 through 23
		# and days 62 through 68. These days
		# have gaps in them for certain 
		# databases.

		data = line.rstrip()

		binarized = numpy.fromstring(data, dtype = 'int8') - 48

		binarized_coarse = coarse_resolution(binarized, iresolution = ires)

		for symbol in binarized_coarse:
			wfile.write("{0}".format(int(symbol)))

		wfile.write('\n')

	wfile.close()

	ofile.close()