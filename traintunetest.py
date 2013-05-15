####################################################################################
#
#	A file that takes in a .dat file (a time series that has been discretized)
#	and outputs 

import sys
import pylab
import numpy
import ipdb

from filter_data_methods import *

def create_traintunetest(fname, ratios = (0.8, 0.1, 0.1), toprint = False, shuffle = False):
	# This function takes in the file name for a
	# data file and outputs three files, one for
	# training, one for tuning, and one for
	# testing.

	ofile = open('{0}.dat'.format(fname))

	# Pull out each line of the file. Each line
	# corresponds to a single days worth of
	# data.

	days = [line.rstrip() for line in ofile]

	ofile.close()

	ndays = len(days) # The number of days in the data set

	assert numpy.sum(ratios) == 1, "Warning: Your train / tune / test ratios should sum to 1."

	# Get the number of training/tuning/testing
	# days.

	ntrain = int(numpy.ceil(ndays*ratios[0]))
	ntune = int(numpy.ceil(ndays*ratios[1]))

	ntest = ndays - (ntrain + ntune)

	# If we should shuffle the train/tune set, 
	# create a shuffled set of indices.

	if shuffle == True:
		shuffled_inds = numpy.arange(ntrain + ntune)

		numpy.random.shuffle(shuffled_inds)

	if toprint:
		print 'ntrain: {0}\nntune: {1}\nntest: {2}\n'.format(ntrain, ntune, ntest)

	# Generate the train/tune/test datasets.

	trainfile = open('{0}-train.dat'.format(fname), 'w')

	for ind in xrange(ntrain):
		if shuffle == True:
			trainfile.write('{0}\n'.format(days[shuffled_inds[ind]]))
		else:
			trainfile.write('{0}\n'.format(days[ind]))

	trainfile.close()

	tunefile = open('{0}-tune.dat'.format(fname), 'w')

	for ind in xrange(ntrain, ntrain + ntune):
		if shuffle == True:
			tunefile.write('{0}\n'.format(days[shuffled_inds[ind]]))
		else:
			tunefile.write('{0}\n'.format(days[ind]))

	tunefile.close()

	testfile = open('{0}-test.dat'.format(fname), 'w')

	for ind in xrange(ntrain + ntune, ndays):
		testfile.write('{0}\n'.format(days[ind]))

	testfile.close()