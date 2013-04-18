import ipdb
import cssr_interface
import numpy
import collections
import sys

from filter_data_methods import *

from traintunetest import create_traintunetest

users = get_top_K_users(1000)

# The system input can be of the form
# 	python filter_data_single.py user_id metric_type

# NOTE: I have changed the script to take in the user_id
# instead of the user_rank. Thus, user_num now 
# contains the user_id, *not* the rank.

if len(sys.argv) < 2:
	user_num = 0
	metric_num = 0
else:
	user_num = int(sys.argv[1])
	metric_num = int(sys.argv[2])

# suffix = users[user_num]
suffix = str(user_num)
# suffix = 'FAKE'

L_max = 10

metrics = ['accuracy', 'precision', 'recall', 'F']

metric = metrics[metric_num]

Ls = range(1,L_max + 1)

correct_by_L = numpy.zeros(len(Ls))

fname = 'timeseries_alldays/byday-600s-{}'.format(suffix)
# fname = 'off_even_process_sim'

create_traintunetest(fname = fname, ratios = (0.8, 0.1, 0.1), toprint = True) # Generate the train-tune-test partitioned data files

# Get a 'zero-order' CSM that predicts as a 
# biased coin. That is, if in the training 
# set the user mostly tweets, always
# predict tweeting. Otherwise, always
# predict not-tweeting.

zero_order_predict = generate_zero_order_CSM(fname + '-train')

for L_ind, L_val in enumerate(Ls):
	print 'Performing filter with L = {0}...\n\n'.format(L_val)

	cssr_interface.run_CSSR(filename = fname + '-train', L = L_val, savefiles = True, showdot = False, is_multiline = True, showCSSRoutput = False)

	CSM = get_CSM(fname = '{}-train'.format(fname))

	epsilon_machine = get_epsilon_machine(fname = '{}-train'.format(fname))

	# print CSM

	states, L = get_equivalence_classes(fname + '-train') # A dictionary structure with the ordered pair
											# (symbol sequence, state)

	correct_rates = run_tests(fname = fname + '-tune', CSM = CSM, zero_order_CSM = zero_order_predict, states = states, epsilon_machine = epsilon_machine, L = L, L_max = L_max, metric = metric, print_predictions = True, print_state_series = True)

	correct_by_L[L_ind] = correct_rates.mean()

print 'History Length\t{} Rate'.format(metric)

for ind in range(len(Ls)):
	print '{}\t{}'.format(Ls[ind], correct_by_L[ind])

ind_L_best = correct_by_L.argmax()
L_best = int(Ls[ind_L_best])

print 'The optimal L was {}.'.format(L_best)

cssr_interface.run_CSSR(filename = fname + '-train', L = L_best, savefiles = True, showdot = True, is_multiline = True, showCSSRoutput = False)

hist_length, Cmu, hmu, num_states = cssr_interface.parseResultFile(fname + '-train')

print 'With this history length, the number of states, statistical complexity and entropy rate are:\nNumber of States: {} (compared to {} possible)\nC_mu = {}\nh_mu = {}'.format(num_states,2**hist_length, Cmu, hmu)

# Perform filter on the held out test set, using the CSM from 
# the L chosen by the tuning set, and compute the performance.

CSM = get_CSM(fname = '{}-train'.format(fname))

epsilon_machine = get_epsilon_machine(fname = '{}-train'.format(fname))

states, L = get_equivalence_classes(fname + '-train') # A dictionary structure with the ordered pair
													  # (symbol sequence, state)

test_correct_rates = run_tests(fname = fname + '-test', CSM = CSM, zero_order_CSM = zero_order_predict, states = states, epsilon_machine = epsilon_machine, L = L, L_max = L_max, metric = metric, print_predictions = True, print_state_series = True)

print 'The mean {} rate on the held out test set is: {}'.format(metric, numpy.mean(test_correct_rates))

# Get the accuracy rate using the zero-order CSM.

zero_order_rate = run_tests(fname = fname + '-test', CSM = zero_order_predict, zero_order_CSM = zero_order_predict, states = states, epsilon_machine = epsilon_machine, L = L, L_max = L_max, metric = metric, type = 'zero')

print 'The mean {} rate using a biased coin is: {}'.format(metric, numpy.mean(zero_order_rate))

print 'Note: A zero-order CSM would always predict... {}'.format(zero_order_predict)

import os

os.system('open rasters_alldays/raster-1s-{}.pdf'.format(suffix))
# os.system('open rasters/raster-600s-{}.pdf'.format(suffix))