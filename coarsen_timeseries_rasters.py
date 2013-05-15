import ipdb
import numpy
import pylab
import datetime

from extract_timeseries_methods import *

from filter_data_methods import *

start = 0
K = 3000-start

# users = get_K_users(K = K, start = start)

users = ['14870168', '18066875', '22935909', '790000', '221180607']

for index, user in enumerate(users):
	print 'Working on user {} ...'.format(start + index)
	ofile = open('timeseries_alldays/byday-1s-{}.dat'.format(user))

	ires = 600

	f, axarr = pylab.subplots(49, sharex = True)

	axind = 0

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
			
			# plot_raster(binarized, 57601, axarr, axind)
			plot_raster(binarized_coarse, 96, axarr, axind, colored = True)
			
			axind += 1

	pylab.xlabel('Time (600 s increments)')

	pylab.savefig('raster-600s-{}-colored.pdf'.format(user))

	ofile.close()