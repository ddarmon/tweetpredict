# This script extracts the state series for computing informational
# coherence.

import ipdb
import cssr_interface
import numpy
import collections
import sys

from filter_data_methods import *

L_max = 10

def get_total_state_series(fname):
	# Get out all the CSM related structures we need.

	CSM = get_CSM(fname = '{}-train'.format(fname))

	epsilon_machine = get_epsilon_machine(fname = '{}-train'.format(fname))

	zero_order_CSM = generate_zero_order_CSM(fname + '-train')

	# Get out the timeseries.

	ofile = open('{}.dat'.format(fname))

	days = [line.rstrip('\n') for line in ofile]

	states, L = get_equivalence_classes('{}-train'.format(fname))

	overall_states = []

	for day in days:
		prediction, state_series = CSM_filter(CSM, zero_order_CSM, states, epsilon_machine, day, L)

		day_states = state_series.split(';')

		overall_states.extend(day_states[(L_max - L + 1):])

	return overall_states

# Get the filtered state series.

fname1 = 'timeseries_alldays/byday-600s-21658412'

overall_states1 = get_total_state_series(fname1)

fname2 = 'timeseries_alldays/byday-600s-184274305'

overall_states2 = get_total_state_series(fname2)

count_array = collections.defaultdict(int)

# Get out the state labels for the first
# and second timeseries.

# # Compute the joint counts.

# n = len(timeseries1)

# assert n == len(timeseries2), 'The time series are of different length!'

# # The symbols we'll use. Assume binary.

# symbols = ['0', '1']

# n_symbols = len(symbols)

# # This computes the count table

# for ind in range(n):
# 	count_array[(timeseries1[ind], timeseries2[ind])] += 1

# # Generate the estimated joint pmf

# jpmf = numpy.zeros((n_symbols, n_symbols))

# for ind_x, symbol_x in enumerate(symbols):
# 	for ind_y, symbol_y in enumerate(symbols):
# 		jpmf[ind_x, ind_y] = count_array[(symbol_x, symbol_y)]/float(n)

# # Compute the estimated mutual information from the pmf

# mi = 0

# for ind_x in range(n_symbols):
# 	denom1 = jpmf[ind_x, :].sum() # p(x)

# 	for ind_y in range(n_symbols):
# 		num = jpmf[ind_x, ind_y] # p(x, y)
		
# 		denom2 = jpmf[:, ind_y].sum() # p(y)

# 		denom = denom1*denom2 # p(x)*p(y)

# 		# By convention, 0 log(0 / 0) = 0
# 		# and 0 log(0 / denom) = 0. We won't have
# 		# to worry about running into num log(num / 0)
# 		# since we're dealing with a discrete alphabet.

# 		if num == 0: # Handle the mutual information convention.
# 			pass
# 		else:
# 			mi += num * numpy.log2(num/denom)

# # Normalize the mutual information, using the fact that
# # I[X; Y] <= min{H[X], H[Y]}, to give the informational
# # coherence,
# # 	IC[X; Y] = I[X; Y] / min{H[X], H[Y]}
# # again the convention that 0/0 = 0.

# # Estimate the entropy of X

# H_x = 0

# for ind_x in range(n_symbols):
# 	p = jpmf[ind_x, :].sum()

# 	if p == 0:
# 		pass
# 	else:
# 		H_x += p*numpy.log2(p)

# H_x = -H_x

# # Estimate the entropy of Y

# H_y = 0

# for ind_y in range(n_symbols):
# 	p = jpmf[:, ind_y].sum()

# 	if p == 0:
# 		pass
# 	else:
# 		H_y += p*numpy.log2(p)

# H_y = -H_y

# # Estimate the informational coherence.

# IC = mi / numpy.min((H_x, H_y))