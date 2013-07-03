import ipdb
import numpy
import pylab
import datetime

from extract_timeseries_methods import *

from filter_data_methods import *

start = 0
K = 3000-start

# users = get_K_users(K = K, start = start)

# users = ['210014700']
users = ['42381705']

to_coarsen = True

if to_coarsen:
	num_bins = 96
else:
	num_bins = 57601

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
			
			if to_coarsen:
				plot_raster(binarized_coarse, num_bins, axarr, axind, colored = False)
			else:
				plot_raster(binarized, num_bins, axarr, axind, colored = False)
			
			
			axind += 1

	pylab.xlabel('Time (600 s increments)')

	if to_coarsen:
		pylab.savefig('raster-600s-{}.pdf'.format(user))
	else:
		pylab.savefig('raster-1s-{}.pdf'.format(user))

	ofile.close()