# This script extracts the state series for computing informational
# coherence.

import ipdb
import cssr_interface
import numpy
import collections
import glob
import pylab

from filter_data_methods import *

from traintunetest import create_traintunetest_cv, cleanup_cv

L_max = 10

ires = 600

def get_total_state_series(fname):
	# Get out all the CSM related structures we need.

	CSM = get_CSM(fname = '{}-train+tune'.format(fname))

	epsilon_machine = get_epsilon_machine(fname = '{}-train+tune'.format(fname))

	zero_order_CSM = generate_zero_order_CSM(fname + '-train+tune')

	# Get out the timeseries.

	ofile = open('{}.dat'.format(fname))

	days = [line.rstrip('\n') for line in ofile]

	states, L = get_equivalence_classes('{}-train+tune'.format(fname))

	overall_states = []

	for day in days:
		prediction, state_series = CSM_filter(CSM, zero_order_CSM, states, epsilon_machine, day, L, verbose = False)

		day_states = state_series.split(';')

		overall_states.extend(day_states[(L_max - L + 1):])

	return overall_states

def build_machine(fname, num_folds = 7, L_max = 11, metric = 'accuracy'):
	Ls = range(1,L_max + 1)

	correct_by_L = numpy.zeros((len(Ls), num_folds))

	create_traintunetest_cv(fname = fname, k = num_folds, ratios = (1, 0)) # Generate the train-tune-test partitioned data files

	for fold_ind in range(num_folds):
	    zero_order_predict = generate_zero_order_CSM(fname + '-train-cv' + str(fold_ind))

	    for L_ind, L_val in enumerate(Ls):
	        cssr_interface.run_CSSR(filename = fname + '-train-cv' + str(fold_ind), L = L_val, savefiles = True, showdot = False, is_multiline = True, showCSSRoutput = False)

	        CSM = get_CSM(fname = '{}-train-cv{}'.format(fname, fold_ind))

	        epsilon_machine = get_epsilon_machine(fname = '{}-train-cv{}'.format(fname, fold_ind))

	        states, L = get_equivalence_classes(fname + '-train-cv' + str(fold_ind)) # A dictionary structure with the ordered pair
	                                                # (symbol sequence, state)

	        correct_rates = run_tests(fname = fname + '-tune-cv' + str(fold_ind), CSM = CSM, zero_order_CSM = zero_order_predict, states = states, epsilon_machine = epsilon_machine, L = L, L_max = L_max, metric = metric, print_predictions = False, print_state_series = False, verbose = False)

	        correct_by_L[L_ind, fold_ind] = correct_rates.mean()

	ind_L_best = correct_by_L.mean(axis = 1).argmax()
	L_best = int(Ls[ind_L_best])

	# use_suffix determines whether, after choosing the optimal L, we
	# should use only the training set, or use both the training and 
	# the tuning set, combined.

	use_suffix = '-train+tune'

	# Sometimes, CSSR cannot infer the CSM for the L_best chosen using 
	# cross-validation. In this case, we decrement L_best by one and
	# try to infer the associated CSM. We also record this error
	# in faulty-IC.txt.

	candidate = []

	cssr_interface.run_CSSR(filename = fname + use_suffix, L = L_best, savefiles = True, showdot = False, is_multiline = True, showCSSRoutput = True)

	candidate = glob.glob(fname + use_suffix + '.dat_inf.dot')

	if candidate == []:
		error_file = open('faulty-IC.txt', 'a')

		error_file.write('{}\n'.format(fname + use_suffix))

		error_file.close()

	while candidate == []:
		L_best -= L_best

		cssr_interface.run_CSSR(filename = fname + use_suffix, L = L_best, savefiles = True, showdot = False, is_multiline = True, showCSSRoutput = True)

		candidate = glob.glob(fname + use_suffix + '.dat_inf.dot')

	cleanup_cv(fname)

users = get_K_users(K = 3000, start = 0)

ICs = numpy.zeros((len(users), len(users)))

ofile = open('informational-coherence-{}s_append.dat'.format(ires), 'w')

for file1_ind in range(0, 1):
	# We only have to *build* the machines the first pass through
	# the outer loop.

	if file1_ind == 0:
		first_pass = True
	else:
		first_pass = False

	fname1 = 'timeseries_clean/byday-{}s-{}'.format(ires, users[file1_ind])

	if first_pass:
		build_machine(fname = fname1, num_folds = 7, L_max = 11)

	timeseries1 = get_total_state_series(fname1)

	# Get out the state labels for the first
	# time series.

	symbols_x = []

	for sym in timeseries1:
		if sym not in symbols_x:
			symbols_x.append(sym)

	# for file2_ind in range(file1_ind+1, len(users)):
	for file2_ind in range(485, len(users)):
		print 'Working on user pair ({}, {})...'.format(file1_ind, file2_ind)

		# Create a new, empty count array

		count_array = collections.defaultdict(int)

		fname2 = 'timeseries_clean/byday-{}s-{}'.format(ires, users[file2_ind])

		if first_pass:
			build_machine(fname = fname2, num_folds = 7, L_max = 11)

		timeseries2 = get_total_state_series(fname2)

		# Get out the symbols for the second timeseries

		symbols_y = []

		for sym in timeseries2:
			if sym not in symbols_y:
				symbols_y.append(sym)

		# Compute the joint counts.

		n = len(timeseries1)

		assert n == len(timeseries2), 'The time series are of different length!'

		n_symbols_x = len(symbols_x)
		n_symbols_y = len(symbols_y)

		# This computes the count table

		for ind in range(n):
			count_array[(timeseries1[ind], timeseries2[ind])] += 1

		# Generate the estimated joint pmf

		jpmf = numpy.zeros((n_symbols_x, n_symbols_y))

		for ind_x, symbol_x in enumerate(symbols_x):
			for ind_y, symbol_y in enumerate(symbols_y):
				jpmf[ind_x, ind_y] = count_array[(symbol_x, symbol_y)]/float(n)

		# Compute the estimated mutual information from the pmf

		mi = 0

		for ind_x in range(n_symbols_x):
			denom1 = jpmf[ind_x, :].sum() # p(x)

			for ind_y in range(n_symbols_y):
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

		p_x = jpmf.sum(axis = 1) # The marginal pmf for X

		for ind_x in range(n_symbols_x):
			p = p_x[ind_x]

			if p == 0:
				pass
			else:
				H_x += p*numpy.log2(p)

		H_x = -H_x

		# Estimate the entropy of Y

		H_y = 0

		p_y = jpmf.sum(axis = 0) # The marginal pmf for Y

		for ind_y in range(n_symbols_y):
			p = p_y[ind_y]

			if p == 0:
				pass
			else:
				H_y += p*numpy.log2(p)

		H_y = -H_y

		# Estimate the informational coherence.

		if mi == 0 or numpy.min((H_x, H_y)) == 0: # We use the convention that 0/0 = 0.
			IC = 0
		elif len(symbols_x) == 1 or len(symbols_y) == 1:
			IC = 0	# A single state process cannot have non-zero informational coherence.
		else:
			IC = mi / numpy.min((H_x, H_y))

		ICs[file1_ind, file2_ind] = IC

		ofile.write('{}\t{}\t{}\n'.format(file1_ind, file2_ind, numpy.max([IC, 0.])))

ofile.close()

# ICs = numpy.loadtxt('informational-coherence.dat')

# modICs = ICs + ICs.T

# pylab.imshow(modICs, interpolation = 'nearest', vmin = 0, vmax = 1)
# pylab.colorbar()
# pylab.xlabel('User $j$')
# pylab.ylabel('User $i$')

# pylab.savefig('ic.pdf')

# modICs = ICs.copy()
# modICs[modICs == 0] = nan

# pylab.imshow(modICs, interpolation = 'nearest', vmin = 0, vmax = 1)
# pylab.colorbar()
# pylab.xlabel('User $j$')
# pylab.ylabel('User $i$')

# pylab.show()

# def get_ij(flat_ind, m):
# 	i = int(flat_ind / m)
# 	j = flat_ind - i*m

# 	return i, j