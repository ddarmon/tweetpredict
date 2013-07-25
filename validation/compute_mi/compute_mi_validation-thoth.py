# Compute the mutual information between X and Y where
# X ~ Bernoulli(1/2)
# Y | X = x ~ Bernoulli(e^x / (1 + e^x))
# 
# The mutual information should be ~ 0.04116767240.
# The informational coherence should be ~ 0.0428322.
# 
# See attached pages in notebook from 4 May 2013.
#
# 	DMD, 040513-17-17
#
# Modified to investigate how bias in the entropies
# effects bias in the mutual information / 
# informational coherence.
#
#	DMD, 170713-15-36

import numpy
import collections

import sys
sys.path.append('/Users/daviddarmon/Documents/Reference/T/THOTH')
import thoth.thoth as thoth

# Generate a sequence according to the probability model above

n = 96*45

# Run several trials to see how biased the estimators for
# mutual information and informational coherence are. Save
# these outputs to sample.txt for analysis by R.

rfile = open('sample-thoth.txt', 'w')

rfile.write('mi\tic\n')

# The number of bootstrap samples.

B = 1000
B_thoth = 1000

for b in range(B):
	print 'On bootstrap trial {}...'.format(b)
	U = numpy.random.rand(n) # Uniform random numbers used to generate X.
	V = numpy.random.rand(n) # Uniform random numbers used to generate Y | X = x.

	X = numpy.zeros(n, dtype = 'int32')

	X[U > 0.5] = 1

	Y = numpy.zeros(n, dtype = 'int32')

	p0 = 0.5
	p1 = numpy.exp(1)/(1 + numpy.exp(1))

	for ind, x in enumerate(X):
		if x == 0:
			if V[ind] < p0:
				Y[ind] = 1
		elif x == 1:
			if V[ind] < p1:
				Y[ind] = 1

	symbols = [0, 1]

	# Compute the joint counts
	n = len(X)

	assert n == len(Y), 'The time series are of different length!'

	n_symbols = len(symbols)

	# This computes the count table

	count_array = collections.defaultdict(int)

	for ind in range(n):
		count_array[(X[ind], Y[ind])] += 1

	# Generate the estimated joint pmf

	joint_counts = numpy.zeros((n_symbols, n_symbols))

	for ind_x, symbol_x in enumerate(symbols):
		for ind_y, symbol_y in enumerate(symbols):
			joint_counts[ind_x, ind_y] = count_array[(symbol_x, symbol_y)]

	# Compute bootstrap estimate of entropy

	counts_x  = joint_counts.sum(axis = 1)

	results_x = thoth.calc_entropy(counts_x, B_thoth)

	H_x = results_x[0]

	counts_y  = joint_counts.sum(axis = 0)

	results_y = thoth.calc_entropy(counts_y, B_thoth)

	H_y = results_y[0]

	results_mi = thoth.calc_mi(joint_counts, B_thoth)

	mi = results_mi[0]

	IC = mi / numpy.min((H_x, H_y))

	# print H_x, H_y, mi, IC

	rfile.write('{}\t{}\n'.format(mi, IC))

rfile.close()