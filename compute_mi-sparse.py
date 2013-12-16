# Code to compute the mutual information between two users, given a
# the files containing their timeseries.
#
# DMD, 040513-15-14

# Modification: Now this only computes the mutual information between
# two nodes who have an edge between them.
#
# DMD, 151213-20-49

import collections
import numpy
import glob
import pylab
from itertools import islice

from filter_data_methods import *

# The (undirected) edges in the network.

edge_list = []

with open('/Users/daviddarmon/Documents/R/Research/tweetpredict/community_structure/edge_list_3K_user_connected.txt') as ofile:
	for line in ofile:
		lsplit = map(int, line.strip().split(' '))
		edge_list.append((lsplit[0], lsplit[1]))

# A dictionary mapping from the nodeid to the userid.

user_lookup = {}

with open('/Users/daviddarmon/Documents/R/Research/tweetpredict/community_structure/node_lookup_table_3K_connected.txt') as ofile:
	for line in islice(ofile, 1, None):
		lsplit = map(int, line.strip().split('\t'))

		userid = lsplit[0]; nodeid = lsplit[1]

		user_lookup[nodeid] = userid

ICs = []

folder = '/Volumes/ddarmon-external/Reference/R/Research/Data/tweetpredict/timeseries_2011'
# ires   = 60*5
ires   = 60*10
# ires   = 60*15

V = len(edge_list)

for edge_ind, edge in enumerate(edge_list):
	u1 = edge[0]; u2 = edge[1]

	print 'Working on user pair ({}, {}), edge {} of {}...'.format(u1, u2, edge_ind, V)

	fname1 = '{}/byday-{}s-{}.dat'.format(folder, ires, user_lookup[u1])

	# Read in the two timeseries of interest.

	with open(fname1) as ofile:
		# Since mutual information doesn't incorporate any sort
		# of lag, we'll concatenate all of the days together.

		timeseries1 = ''

		for line in ofile:
			timeseries1 += line.rstrip('\n')

	# Create a new, empty count array

	count_array = collections.defaultdict(int)

	fname2 = '{}/byday-{}s-{}.dat'.format(folder, ires, user_lookup[u2])

	with open(fname2) as ofile:
		timeseries2 = ''

		for line in ofile:
			timeseries2 += line.rstrip('\n')

	# Compute the joint counts.

	n = len(timeseries1)

	assert n == len(timeseries2), 'The time series are of different length!'

	# The symbols we'll use. Assume binary.

	symbols = ['0', '1']

	n_symbols = len(symbols)

	# This computes the count table

	for ind in range(n):
		count_array[(timeseries1[ind], timeseries2[ind])] += 1

	# Generate the estimated joint pmf

	jpmf = numpy.zeros((n_symbols, n_symbols))

	for ind_x, symbol_x in enumerate(symbols):
		for ind_y, symbol_y in enumerate(symbols):
			jpmf[ind_x, ind_y] = count_array[(symbol_x, symbol_y)]/float(n)

	# Compute the estimated mutual information from the pmf

	mi = 0

	for ind_x in range(n_symbols):
		denom1 = jpmf[ind_x, :].sum() # p(x)

		for ind_y in range(n_symbols):
			num = jpmf[ind_x, ind_y] # p(x, y)
			
			denom2 = jpmf[:, ind_y].sum() # p(y)

			denom = denom1*denom2 # p(x)*p(y)

			# By convention, 0 log(0 / 0) = 0
			# and 0 log(0 / denom) = 0. We won't have
			# to worry about running into num log(num / 0)
			# since we're dealing with a discrete alphabet.

			if num == 0: # Handle the mutual information convention.
				pass
			else:
				mi += num * numpy.log2(num/denom)

	# Normalize the mutual information, using the fact that
	# I[X; Y] <= min{H[X], H[Y]}, to give the informational
	# coherence,
	# 	IC[X; Y] = I[X; Y] / min{H[X], H[Y]}
	# again the convention that 0/0 = 0.

	# Estimate the entropy of X

	H_x = 0

	for ind_x in range(n_symbols):
		p = jpmf[ind_x, :].sum()

		if p == 0:
			pass
		else:
			H_x += p*numpy.log2(p)

	H_x = -H_x

	# Estimate the entropy of Y

	H_y = 0

	for ind_y in range(n_symbols):
		p = jpmf[:, ind_y].sum()

		if p == 0:
			pass
		else:
			H_y += p*numpy.log2(p)

	H_y = -H_y

	# Estimate the informational coherence.

	IC = mi / numpy.min((H_x, H_y))

	ICs.append(IC)

with open('mutual-information-{}s-2011-sparse.dat'.format(ires), 'w') as wfile:
	for edge_ind, edge in enumerate(edge_list):
		wfile.write('{}\t{}\t{}\n'.format(edge[0], edge[1], ICs[edge_ind]))