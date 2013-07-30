# This script computes the informational coherence between
# two timeseries.
#
# It has been modified to use the THOTH (DeDeo, et al.)
# bootstrap estimators for the entropies and 
# mutual informations.

import ipdb
import cssr_interface
import numpy
import collections
import glob
import pylab

from filter_data_methods import *
from traintunetest import create_traintunetest_cv, cleanup_cv

import sys
sys.path.append('/Users/daviddarmon/Documents/Reference/T/THOTH/THOTH-mi')
import thoth.thoth as thoth

L_max = 11

ires = 600

# The number of bootstrap samples to use in computing information
# theoretic statistics.

B_thoth = 1000

print 'Performing {} bootstraps for each compution of the statistics.'.format(B_thoth)

def get_total_state_series(fname, already_extracted = False):
	# Get out all the CSM related structures we need.

	if already_extracted:
		ofile = open('{}-states.dat'.format(fname))

		states, L = get_equivalence_classes('{}-train+tune'.format(fname))

		overall_states = []

		for line in ofile:
			line = line.rstrip('\n')

			overall_states.extend(line.split(';')[(L_max - L + 1):])

		ofile.close()

	else:
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

ofile = open('informational-coherence-{}s-thoth-u523.dat'.format(ires), 'w')

print 'Warning: Assuming the causal state model has already been inferred and the state series has already been extracted.'

first_pass = False

for file1_ind in range(523, 524):
	# We only have to *build* the machines the first pass through
	# the outer loop.

	# if file1_ind == 0:
	# 	first_pass = True
	# else:
	# 	first_pass = False

	fname1 = 'timeseries_clean/byday-{}s-{}'.format(ires, users[file1_ind])

	if first_pass:
		build_machine(fname = fname1, num_folds = 7, L_max = 11)

	hist_length, Cmu, hmu, num_states = cssr_interface.parseResultFile(fname1 + '-train+tune')

	# For coin flips, we don't need to do any computations, since
	# iid processes cannot have non-zero mutual information.

	is_coinflip = False

	if num_states == 1:
		is_coinflip = True

	timeseries1 = get_total_state_series(fname1, already_extracted = True)

	# Get out the state labels for the first
	# time series.

	symbols_x = []

	for sym in timeseries1:
		if sym not in symbols_x:
			symbols_x.append(sym)

	# for file2_ind in range(file1_ind+1, len(users)):
	for file2_ind in range(524, len(users)):
		if (file2_ind % 500) == 0:
			print 'Working on user pair ({}, {})...'.format(file1_ind, file2_ind)

		if is_coinflip == False:
			# Create a new, empty count array

			count_array = collections.defaultdict(int)

			fname2 = 'timeseries_clean/byday-{}s-{}'.format(ires, users[file2_ind])

			if first_pass:
				build_machine(fname = fname2, num_folds = 7, L_max = 11)

			hist_length, Cmu, hmu, num_states = cssr_interface.parseResultFile(fname2 + '-train+tune')

			if num_states != 1:
				timeseries2 = get_total_state_series(fname2, already_extracted = True)

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

				# Generate the estimated joint counts

				joint_counts = numpy.zeros((n_symbols_x, n_symbols_y))

				for ind_x, symbol_x in enumerate(symbols_x):
					for ind_y, symbol_y in enumerate(symbols_y):
						joint_counts[ind_x, ind_y] = count_array[(symbol_x, symbol_y)]

				# Generate the joint pmf

				jpmf = joint_counts/float(n)

				# Compute MLE estimates of entropies.

				# Compute marginals.

				px = jpmf.sum(axis = 1)
				py = jpmf.sum(axis = 0)

				H_x = 0
				H_y = 0

				for p in px:
					if p == 0:
						pass
					else:
						H_x += p*numpy.log2(p)

				H_x = -H_x

				for p in py:
					if p == 0:
						pass
					else:
						H_y += p*numpy.log2(p)

				H_y = -H_y

				# Compute the bootstrap estimate of the mutual
				# information.

				results_mi = thoth.calc_mi(joint_counts, B_thoth)

				mi = results_mi[0]

				# Estimate the informational coherence.

				if mi == 0 or numpy.min((H_x, H_y)) == 0: # We use the convention that 0/0 = 0.
					IC = 0
				elif len(symbols_x) == 1 or len(symbols_y) == 1:
					IC = 0	# A single state process cannot have non-zero informational coherence.
				else:
					IC = mi / numpy.min((H_x, H_y))

			else:
				IC = 0.
				mi = 0.
				H_x = -1
				H_y = -1
		else:
			IC = 0.
			mi = 0
			H_x = -1
			H_y = -1

		ofile.write('{}\t{}\t{}\t{}\t{}\t{}\n'.format(file1_ind, file2_ind, numpy.max([IC, 0.]), mi, H_x, H_y))

ofile.close()