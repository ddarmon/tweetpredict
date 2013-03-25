####################################################################################
#
#	A file that takes in a .dat file (a time series that has been discretiezed)
#	and outputs 

import cssr_interface
import sys
import pylab
import numpy
import ipdb

def create_traintunetest(fname, ratios = (0.8, 0.1, 0.1), toprint = False):
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

	if toprint:
		print 'ntrain: {0}\nntune: {1}\nntest: {2}'.format(ntrain, ntune, ntest)

	# Generate the train/tune/test datasets.

	trainfile = open('{0}-train.dat'.format(fname), 'w')

	for ind in xrange(ntrain):
		trainfile.write('{0}\n'.format(days[ind]))

	trainfile.close()

	tunefile = open('{0}-tune.dat'.format(fname), 'w')

	for ind in xrange(ntrain, ntrain + ntune):
		tunefile.write('{0}\n'.format(days[ind]))

	tunefile.close()

	testfile = open('{0}-test.dat'.format(fname), 'w')

	for ind in xrange(ntrain + ntune, ndays):
		testfile.write('{0}\n'.format(days[ind]))

	testfile.close()

def get_top_K_users(K = 5):
	ofile = open('user_lookup/tweet_counts_labeled.tsv')

	ofile.readline()

	users = []

	for k in range(K):
		line = ofile.readline().split('\t')

		users.append(line[0])

	ofile.close()

	return users

# Use CSSR to generate the CSM files

users = get_top_K_users(40)

for user in users:
	suffix = user

	# suffix = '184274305'
	# suffix = '14448173'
	# suffix = '1712831'
	# suffix = '196071730'
	# suffix = '59697909'
	# suffix = 'FAKE'
	fname = 'byday-600s-{}'.format(suffix)

	create_traintunetest(fname = 'timeseries' + fname, ratios = (0.8, 0.1, 0.1), toprint = True)

	# fname_to_CSSR = fname + '-train'

	# if len(sys.argv) > 1:
	# 	historyLength = sys.argv[1]
	# else:
	# 	historyLength = 2

	# is_multiline = True

	# cssr_interface.run_CSSR(filename = fname_to_CSSR, L = historyLength, savefiles = True, showdot = True, is_multiline = is_multiline, showCSSRoutput = False)

	# hist_length, Cmu, hmu, num_states = cssr_interface.parseResultFile(fname_to_CSSR)

	# print 'C_mu: {0}\nh_mu: {1}\nNumber of States: {2}'.format(Cmu, hmu, num_states)