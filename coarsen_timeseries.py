import ipdb
import numpy
import pylab
import datetime
import random
import glob

from extract_timeseries_methods import *

from filter_data_methods import *

start = 4000
K = 5000-start

users = get_K_users(K = K, start = start)

for index, user in enumerate(users):
	print 'Working on user {} ...'.format(start + index)
	ofile = open('timeseries_extra/byday-1s-{}.dat'.format(user))

	ires = 600

	wfile = open('timeseries_extra/byday-{}s-{}.dat'.format(ires, user), 'w')

	for ind, line in enumerate(ofile):
		# For now, remove days 11 through 23
		# and days 62 through 68. These days
		# have gaps in them for certain 
		# databases.

		if (11 <= ind <= 23) or (62 <= ind <= 68):
			pass
		else:
			data = line.rstrip()

			binarized = numpy.fromstring(data, dtype = 'int8') - 48

			binarized_coarse = coarse_resolution(binarized, iresolution = ires)

			for symbol in binarized_coarse:
				wfile.write("{0}".format(int(symbol)))

			wfile.write('\n')

	wfile.close()

	ofile.close()