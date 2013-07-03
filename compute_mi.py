# Code to compute the mutual information between two users, given a
# the files containing their timeseries.
# 
# DMD, 040513-15-14

import collections
import numpy
import glob
import pylab

from filter_data_methods import *

users = get_K_users(K = 3000, start = 0)

# Create an empty holder for the ICs

ICs = numpy.zeros([len(users), len(users)])

folder = 'timeseries_clean'
ires   = 60*5
# ires   = 60*10
# ires   = 60*15

for file1_ind in range(0, len(users)):
	print 'Working on user {}...'.format(file1_ind)
	fname1 = '{}/byday-{}s-{}.dat'.format(folder, ires, users[file1_ind])

	# Read in the two timeseries of interest.

	ofile = open(fname1)

	# Since mutual information doesn't incorporate any sort
	# of lag, we'll concatenate all of the days together.

	timeseries1 = ''

	for line in ofile:
		timeseries1 += line.rstrip('\n')

	ofile.close()

	for file2_ind in range(file1_ind+1, len(users)):
		# Create a new, empty count array

		count_array = collections.defaultdict(int)

		fname2 = '{}/byday-{}s-{}.dat'.format(folder, ires, users[file2_ind])

		ofile = open(fname2)

		timeseries2 = ''

		for line in ofile:
			timeseries2 += line.rstrip('\n')

		ofile.close()

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

		ICs[file1_ind, file2_ind] = IC

# numpy.savetxt('mutual-information.dat', ICs)

ofile = open('mutual-information-{}s.dat'.format(ires), 'w')

for i in range(len(users)):
	for j in range(i+1, len(users)):
		ofile.write('{}\t{}\t{}\n'.format(i, j, ICs[i, j]))

ofile.close()

sym_IC = ICs + ICs.T

sym_IC[sym_IC == 0] = numpy.nan

max_bar = 0.25

pylab.figure()
pylab.imshow(sym_IC, interpolation = 'nearest', vmin = 0, vmax = max_bar)
pylab.colorbar()

pylab.show()

# symmetric = numpy.log10(ICs + ICs.T)

# symmetric[symmetric == -numpy.inf] = numpy.nan

# pylab.figure()
# pylab.imshow(symmetric, interpolation = 'nearest')
# pylab.colorbar()
# pylab.show()

def get_ij(flat_ind, m):
	i = int(flat_ind / m)
	j = flat_ind - i*m

	return i, j