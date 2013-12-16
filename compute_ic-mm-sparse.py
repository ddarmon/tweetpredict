# This script compute the informational coherence between two
# time series.

# Modification: Now this only computes the mutual information between
# two nodes who have an edge between them.
#
# DMD, 151213-20-49

import ipdb
import cssr_interface
import numpy
import collections
import glob
import pylab
from itertools import islice

from filter_data_methods import *
from traintunetest import create_traintunetest_cv, cleanup_cv

L_max = 11

ires = 600

def get_total_state_series(fname, already_extracted = False):
	# Get out all the CSM related structures we need.

	CSM = get_CSM(fname = '{}-train+tune'.format(fname))

	epsilon_machine = get_epsilon_machine(fname = '{}-train+tune'.format(fname))

	zero_order_CSM = generate_zero_order_CSM(fname)

	if already_extracted:
		ofile = open('{}-states.dat'.format(fname))

		states, L = get_equivalence_classes('{}-train+tune'.format(fname))

		overall_states = []

		for line in ofile:
			line = line.rstrip('\n')

			overall_states.extend(line.split(';')[(L_max - L + 1):])

		ofile.close()

	else:
		# Get out the timeseries.

		ofile = open('{}.dat'.format(fname))

		days = [line.rstrip('\n') for line in ofile]

		states, L = get_equivalence_classes('{}-train+tune'.format(fname))

		overall_states = []

		with open('{}-states.dat'.format(fname), 'w') as wfile:
			for day in days:
				prediction, state_series = CSM_filter(CSM, zero_order_CSM, states, epsilon_machine, day, L, verbose = False)

				wfile.write('{}\n'.format(state_series))

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

	cssr_interface.run_CSSR(filename = fname + use_suffix, L = L_best, savefiles = True, showdot = False, is_multiline = True, showCSSRoutput = False)

	candidate = glob.glob(fname + use_suffix + '.dat_inf.dot')

	if candidate == []:
		error_file = open('faulty-IC.txt', 'a')

		error_file.write('{}\n'.format(fname + use_suffix))

		error_file.close()

	while candidate == []:
		L_best -= L_best

		cssr_interface.run_CSSR(filename = fname + use_suffix, L = L_best, savefiles = True, showdot = False, is_multiline = True, showCSSRoutput = False)

		candidate = glob.glob(fname + use_suffix + '.dat_inf.dot')

	cleanup_cv(fname)

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

V = len(edge_list)

ICs = []

wfile = open('informational-coherence-{}s-2011-sparse-mm.dat'.format(ires), 'w')

# print 'Warning: Assuming the causal state model has already been inferred and the state series has already been extracted.'

# Keep a list of those users who have already had their CSM inferred.

already_learned = {}

# Keep a list of those users who we have already extracted their state
# series.

already_extracted = {}

first_pass = True

folder = '/Volumes/ddarmon-external/Reference/R/Research/Data/tweetpredict/timeseries_2011'

for edge_ind, edge in enumerate(edge_list):
	u1 = edge[0]; u2 = edge[1]

	print 'Working on user pair ({}, {}), edge {} of {}...'.format(u1, u2, edge_ind, V)

	fname1 = '{}/byday-{}s-{}'.format(folder, ires, user_lookup[u1])

	if u1 not in already_learned:
		build_machine(fname = fname1, num_folds = 7, L_max = 11)
		already_learned[u1] = 1
	else:
		pass

	hist_length, Cmu, hmu, num_states = cssr_interface.parseResultFile(fname1 + '-train+tune')

	# For coin flips, we don't need to do any computations, since
	# iid processes cannot have non-zero informational coherence.

	is_coinflip = False

	if num_states == 1:
		is_coinflip = True

	if u1 in already_extracted:
		timeseries1 = get_total_state_series(fname1, already_extracted = True)
	else:
		timeseries1 = get_total_state_series(fname1, already_extracted = False)
		already_extracted[u1] = 1

	# Get out the state labels for the first
	# time series.

	symbols_x = []

	for sym in timeseries1:
		if sym not in symbols_x:
			symbols_x.append(sym)

	if is_coinflip == False:
		# Create a new, empty count array

		count_array = collections.defaultdict(int)

		fname2 = '{}/byday-{}s-{}'.format(folder, ires, user_lookup[u2])

		if u2 not in already_learned:
			build_machine(fname = fname2, num_folds = 7, L_max = 11)
			already_learned[u2] = 1
		else:
			pass

		hist_length, Cmu, hmu, num_states = cssr_interface.parseResultFile(fname2 + '-train+tune')

		if num_states != 1:
			if u2 in already_extracted:
				timeseries2 = get_total_state_series(fname2, already_extracted = True)
			else:
				timeseries2 = get_total_state_series(fname2, already_extracted = False)
				already_extracted[u2] = 1

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

			# Compute the joint entropy from the empirical joint probability
			# mass function.

			H_xy = 0

			for ind_x in range(n_symbols_x):
				for ind_y in range(n_symbols_y):
					p = jpmf[ind_x, ind_y]

					if p == 0: # Use the convention that 0 log2 0 = 0
						pass
					else:
						H_xy += p*numpy.log2(p)

			H_xy = -H_xy

			# Make the Miller-Madow correction for bias in the entropy
			# estimator.

			H_xy += (n_symbols_x*n_symbols_y - 1)/(2.*n)

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

			# Make the Miller-Madow correction.

			H_x += (n_symbols_x - 1)/(2.*n)

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

			# Make the Miller-Madow correction.

			H_y += (n_symbols_y - 1)/(2.*n)

			# Estimate the mutual information.

			mi = H_x + H_y - H_xy

			# Estimate the informational coherence.

			if mi == 0 or numpy.min((H_x, H_y)) == 0: # We use the convention that 0/0 = 0.
				IC = 0
			elif len(symbols_x) == 1 or len(symbols_y) == 1:
				IC = 0	# A single state process cannot have non-zero informational coherence.
			else:
				IC = mi / numpy.min((H_x, H_y))

		else:
			IC = 0.
	else:
		IC = 0.

	wfile.write('{}\t{}\t{}\n'.format(u1, u2, numpy.max([IC, 0.])))

wfile.close()