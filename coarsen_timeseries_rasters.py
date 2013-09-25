import ipdb
import numpy
import pylab
import datetime
import glob

from extract_timeseries_methods import *

from filter_data_methods import *

# rank_start = 0 # The ith most highly tweeting user, where we start
#                 # counting at 0.

# K = 3000-rank_start

# users = get_K_users(K = K, start = rank_start)

fnames = glob.glob('timeseries/byday-1s-*.dat')

total_hours = 16

print 'Assuming the day has been windowed into {} hours...'.format(total_hours)

ires = 0

if ires == 0:
	to_coarsen = False
else:
	to_coarsen = True

if to_coarsen:
	num_bins = (3600*total_hours + 1)/ires
else:
	num_bins = 3600*total_hours + 1

# for index, user in enumerate(users):
for index, fname in enumerate(fnames):
	user = fname.split('-')[2].split('.')[0]

	ofile = open('timeseries/byday-1s-{}.dat'.format(user))

	line_count = 0

	for line in ofile:
		line_count += 1

	ofile.close()

	ofile = open('timeseries/byday-1s-{}.dat'.format(user))

	f = pylab.figure()

	# Count the number of trials

	num_trials = 0

	for line in ofile:
		num_trials += 1

	ofile.close(); ofile = open('timeseries/byday-1s-{}.dat'.format(user))

	for ind, line in enumerate(ofile):
		data = line.rstrip()
		
		binarized = numpy.fromstring(data, dtype = 'int8') - 48

		if to_coarsen == True:
			binarized_coarse = coarse_resolution(binarized, iresolution = ires)
		else:
			binarized_coarse = binarized
		
		if to_coarsen:
			plot_raster_big(binarized_coarse, num_bins, trial = ind, num_trials = num_trials, colored = False)
		else:
			plot_raster_big(binarized, num_bins, trial = ind, num_trials = num_trials, colored = False)
	
	tmax = len(binarized_coarse)

	ax = f.axes[0]

	# ax.axes.get_yaxis().set_visible(False)		

	if to_coarsen:
		pylab.xlabel('Time ({} s increments)'.format(ires))
	else:
		pylab.xlabel('Time (1 s increments)')

	pylab.ylabel('Day')
	pylab.ylim([0, num_trials])
	pylab.gca().invert_yaxis()

	pylab.xticks(rotation='vertical')

	pylab.gcf().subplots_adjust(bottom=0.2)

	pylab.xlim([0, tmax])

	if to_coarsen:
		pylab.savefig('raster-{}s-{}.pdf'.format(ires, user))
	else:
		pylab.savefig('raster-1s-{}.pdf'.format(user))

	ofile.close()