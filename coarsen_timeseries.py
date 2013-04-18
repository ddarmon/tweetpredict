import ipdb
import numpy
import pylab
import datetime
import random
import glob

from extract_timeseries_methods import *

from filter_data_methods import *

start = 2141
K = 859

users = get_K_users(K = K, start = start)

for index, user in enumerate(users):
	print 'Working on user {} ...'.format(start + index)
	ofile = open('timeseries_alldays/byday-1s-{}.dat'.format(user))

	ires = 600

	wfile = open('timeseries_alldays/byday-{}s-{}.dat'.format(ires, user), 'w')

	for line in ofile:
		data = line.rstrip()

		binarized = numpy.fromstring(data, dtype = 'int8') - 48

		binarized_coarse = coarse_resolution(binarized, iresolution = ires)

		for symbol in binarized_coarse:
			wfile.write("{0}".format(int(symbol)))

		wfile.write('\n')

	wfile.close()

	ofile.close()