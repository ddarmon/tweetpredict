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

import numpy
import collections

# Generate a sequence according to the probability model above

n = 500000

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

ofile = open('validation_x.dat', 'w')

for symbol in X:
	ofile.write('{0}'.format(str(symbol)))

ofile.close()

ofile = open('validation_y.dat', 'w')

for symbol in Y:
	ofile.write('{0}'.format(str(symbol)))

ofile.close()

fname1 = 'validation_x.dat'

# Read in the two timeseries of interest.

ofile = open(fname1)

# Since mutual information doesn't incorporate any sort
# of lag, we'll concatenate all of the days together.

timeseries1 = ''

for line in ofile:
	timeseries1 += line.rstrip('\n')

ofile.close()

count_array = collections.defaultdict(int)

fname2 = 'validation_y.dat'

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

print H_x, H_y, mi, IC