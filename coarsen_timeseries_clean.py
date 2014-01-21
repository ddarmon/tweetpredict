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

prefix = '/Volumes/ddarmon-external/Reference/R/Research/Data/tweetpredict/timeseries_2011'

# start = 0
# K = 3000-start

# users = get_K_users(K = K, start = start)

# for index, user in enumerate(users):
# 	print 'Working on user {} ...'.format(start + index)

# Get out the users from the ICWSM study.

with open('/Users/daviddarmon/Documents/Reference/R/Research/2013/sfi-dynComm/data/twitter_network_filtered_nodes.txt') as ofile:
    users = [line.strip() for line in ofile]

for index, user in enumerate(users):
	print 'Working on user {}, which is {} of {}...'.format(user, index, len(users))
	
	try:
		ofile = open('{}/byday-1s-{}.dat'.format(prefix, user))

		ires = 60*10

		wfile = open('{}/byday-{}s-{}.dat'.format(prefix, ires, user), 'w')

		for ind, line in enumerate(ofile):
			data = line.rstrip()

			binarized = numpy.fromstring(data, dtype = 'int8') - 48

			binarized_coarse = coarse_resolution(binarized, iresolution = ires)

			for symbol in binarized_coarse:
				wfile.write("{0}".format(int(symbol)))

			wfile.write('\n')

		wfile.close()

		ofile.close()
	except IOError:
		pass