####################################################################################
#
#	A file that takes in a .dat file (a time series that has been discretized)
#	and outputs 

import os
import pylab
import numpy
import ipdb
import glob

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

	overallfile = open('{0}-train+tune.dat'.format(fname), 'w')

	trainfile = open('{0}-train.dat'.format(fname), 'w')

	for ind in xrange(ntrain):
		if shuffle == True:
			trainfile.write('{0}\n'.format(days[shuffled_inds[ind]]))
			overallfile.write('{0}\n'.format(days[shuffled_inds[ind]]))
		else:
			trainfile.write('{0}\n'.format(days[ind]))
			overallfile.write('{0}\n'.format(days[ind]))

	trainfile.close()

	tunefile = open('{0}-tune.dat'.format(fname), 'w')

	for ind in xrange(ntrain, ntrain + ntune):
		if shuffle == True:
			tunefile.write('{0}\n'.format(days[shuffled_inds[ind]]))
			overallfile.write('{0}\n'.format(days[shuffled_inds[ind]]))
		else:
			tunefile.write('{0}\n'.format(days[ind]))
			overallfile.write('{0}\n'.format(days[ind]))

	tunefile.close()

	overallfile.close()

	testfile = open('{0}-test.dat'.format(fname), 'w')

	for ind in xrange(ntrain + ntune, ndays):
		testfile.write('{0}\n'.format(days[ind]))

	testfile.close()

def create_traintunetest_cv(fname, ratios = (0.9, 0.1), k = 5):
	# This function takes in the file name for a
	# data file and outputs three types of files, one type for
	# training, one type for tuning, and one type for
	# testing.

	# It uses k-fold cross validation. So the first ratio in ratios is 
	# the size of the combined train/tune set, and the last ratio is the 
	# size of the testing set.

	# k-fold cross-validation means we'll partition the data into 
	# ceil(n / m) sets, and hold out one of these at a time as a tuning set.

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

	ntraintune = int(numpy.ceil(ndays*ratios[0]))

	partition_size = int(numpy.floor(ntraintune/float(k)))

	# Shuffle the train/tune set.

	shuffled_inds = numpy.arange(ntraintune)

	numpy.random.shuffle(shuffled_inds)

	# Generate the train/tune/test datasets.

	for k_ind in range(k):
		trainfile = open('{0}-train-cv{1}.dat'.format(fname, k_ind), 'w')
		tunefile = open('{0}-tune-cv{1}.dat'.format(fname, k_ind), 'w')

		for leading_ind in range(0, k_ind*partition_size):
			trainfile.write('{0}\n'.format(days[shuffled_inds[leading_ind]]))

		for tuning_ind in range(k_ind*partition_size, (k_ind+1)*partition_size):
			tunefile.write('{0}\n'.format(days[shuffled_inds[tuning_ind]]))

		for trailing_ind in range((k_ind+1)*partition_size, ntraintune):
			trainfile.write('{0}\n'.format(days[shuffled_inds[trailing_ind]]))

		trainfile.close()

		tunefile.close()

	# Generate a combined train+tune file

	traintunefile = open('{0}-train+tune.dat'.format(fname), 'w')

	for ind in range(ntraintune):
		traintunefile.write('{0}\n'.format(days[ind]))

	traintunefile.close()

def cleanup_cv(fname):
	# This function removes all of the files created for cross-validation.

	train_files = glob.glob('{}-train-cv*'.format(fname))
	tune_files  = glob.glob('{}-tune-cv*'.format(fname))

	for dfile in train_files:
		os.remove(os.path.abspath(dfile))

	for dfile in tune_files:
		os.remove(os.path.abspath(dfile))