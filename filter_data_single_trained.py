import ipdb
import cssr_interface
import numpy
import collections
import sys

from filter_data_methods import *

from traintunetest import create_traintunetest

metrics = ['accuracy', 'precision', 'recall', 'F']

metric = metrics[0]

L_max = 11

# Highest statistical complexity

# suffixes = ['14664756', '17789501', '18049840', '18773467', '19713521']

# Highest CM Rate - ESN Rate

CSM_file = '/Users/daviddarmon/Dropbox/papers/socialcom-2013/paper/CSM-Simulations/highest-statistical-complexity.txt'

suffixes = [line.rstrip('\n') for line in open(CSM_file)]

# suffixes = ['14326003', '14468043', '26744291', '186633188', '210014700']

for suffix in suffixes:
	fname = 'timeseries_alldays/byday-600s-{}'.format(suffix)

	test_fname = '/Users/daviddarmon/Dropbox/papers/socialcom-2013/paper/CSM-Simulations/best-csm'

	# Get a 'zero-order' CSM that predicts as a 
	# biased coin. That is, if in the training 
	# set the user mostly tweets, always
	# predict tweeting. Otherwise, always
	# predict not-tweeting.

	zero_order_predict = generate_zero_order_CSM(fname + '-train')

	hist_length, Cmu, hmu, num_states = cssr_interface.parseResultFile(fname + '-train')

	# Perform filter on the held out test set, using the CSM from 
	# the L chosen by the tuning set, and compute the performance.

	CSM = get_CSM(fname = '{}-train'.format(fname))

	epsilon_machine = get_epsilon_machine(fname = '{}-train'.format(fname))

	states, L = get_equivalence_classes(fname + '-train') # A dictionary structure with the ordered pair
														  # (symbol sequence, state)

	test_correct_rates = run_tests(fname = '{}/byday-600s-{}_sim'.format(test_fname, suffix), CSM = CSM, zero_order_CSM = zero_order_predict, states = states, epsilon_machine = epsilon_machine, L = L, L_max = L_max, metric = metric, print_predictions = False, print_state_series = False)

	print 'The mean {} rate on the held out test set is: {}'.format(metric, numpy.mean(test_correct_rates))

	# Get the accuracy rate using the zero-order CSM.

	zero_order_rate = run_tests(fname = '{}/byday-600s-{}_sim'.format(test_fname, suffix), CSM = zero_order_predict, zero_order_CSM = zero_order_predict, states = states, epsilon_machine = epsilon_machine, L = L, L_max = L_max, metric = metric, type = 'zero')

	print 'The mean {} rate using a biased coin is: {}'.format(metric, numpy.mean(zero_order_rate))

	print 'Note: A zero-order CSM would always predict... {}'.format(zero_order_predict)