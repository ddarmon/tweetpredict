# This script file is for performing the 'bit flip' experiment where
# we train on the entire data set, and then test on the same data
# set where we flip 0%, 1%, and 10% of the bits at random.

import ipdb
import cssr_interface
import numpy
import collections
import sys

from filter_data_methods import *

from traintunetest import create_traintunetest_cv

def generate_bit_flips(fname, p = 1, per_day = 96, num_days = 49):
    # Generate a new data file where we flip exactly p% of
    # the bits in the file.

    ofile = open(fname)

    # Get the complete timeseries as one long list.

    ts = []

    for line in ofile:
        day = line.rstrip('\n')
        for char in day:
            ts.append(char)

    ofile.close()

    # The number of time points in the time series.

    num_points = len(ts)

    # Choose which bits to flip.

    change_bits = numpy.arange(num_points)

    numpy.random.shuffle(change_bits)

    num_flips = int(numpy.ceil(p/100.*num_points))

    for flip_ind in range(num_flips):
        bit = ts[change_bits[flip_ind]]
        
        if bit == '1':
            ts[change_bits[flip_ind]] = '0'
        else:
            ts[change_bits[flip_ind]] = '1'

    outfile = open('flipbit-{}p.dat'.format(p), 'w')

    for day_ind in range(num_days):
        for time_ind in range(per_day):
            outfile.write('{}'.format(ts[day_ind*per_day + time_ind]))

        outfile.write('\n')

    outfile.close()


rank_start = 0 # The ith most highly tweeting user, where we start
                # counting at 0.

K = 3000-rank_start

users = get_K_users(K = K, start = rank_start)

metric_num = 0

ofile = open('bitflip-csm-test.tsv', 'w')

ofile.write('user_id\tacc 0%\tacc 10%\tacc 20%\tacc30%\tacc40%\tacc50%\tacc60%\tacc70%\tacc80%\tacc90%\tacc100%\tbase 0%\tbase 10%\tbase 20%\tbase 30%\tbase 40%\tbase 50%\tbase 60%\tbase 70%\tbase 80%\tbase 90%\tbase 100%\n')

# The number of folds to use in the cross-validation step.

num_folds = 9

ps = [0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100]

L_max = 10

metrics = ['accuracy', 'precision', 'recall', 'F']

metric = metrics[metric_num]

for index, user_num in enumerate(range(len(users))):
    print 'On user {} of {}'.format(user_num, K)
    suffix = users[user_num]

    Ls = range(1,L_max + 1)

    # correct_by_L is L_max by num_folds. Thus, each
    # *row* corresponds to the accuracy rate using a particular
    # value of L and each *column* corresponds to the accuracy
    # rates using all of the Ls on a particular fold.

    # We want to average across *rows*.

    correct_by_L = numpy.zeros((len(Ls), num_folds))

    fname = 'timeseries_alldays/byday-600s-{}'.format(suffix)

    numpy.random.seed(1)

    # create_traintunetest_cv(fname = fname, ratios = (1, 0), k = num_folds) # Generate the train-tune-test partitioned data files

    # Get a 'zero-order' CSM that predicts as a 
    # biased coin. That is, if in the training 
    # set the user mostly tweets, always
    # predict tweeting. Otherwise, always
    # predict not-tweeting.

    # for fold_ind in range(num_folds):
    #     zero_order_predict = generate_zero_order_CSM(fname + '-train-' + str(fold_ind))

    #     for L_ind, L_val in enumerate(Ls):
    #         cssr_interface.run_CSSR(filename = fname + '-train-' + str(fold_ind), L = L_val, savefiles = True, showdot = False, is_multiline = True, showCSSRoutput = False)

    #         CSM = get_CSM(fname = '{}-train-{}'.format(fname, fold_ind))

    #         epsilon_machine = get_epsilon_machine(fname = '{}-train-{}'.format(fname, fold_ind))

    #         # print CSM

    #         states, L = get_equivalence_classes(fname + '-train-' + str(fold_ind)) # A dictionary structure with the ordered pair
    #                                                 # (symbol sequence, state)

    #         correct_rates = run_tests(fname = fname + '-tune-' + str(fold_ind), CSM = CSM, zero_order_CSM = zero_order_predict, states = states, epsilon_machine = epsilon_machine, L = L, L_max = L_max, metric = metric, print_predictions = False, print_state_series = False, verbose = False)

    #         correct_by_L[L_ind, fold_ind] = correct_rates.mean()

    # ind_L_best = correct_by_L.mean(axis = 1).argmax()
    # L_best = int(Ls[ind_L_best])

    # # use_suffix determines whether, after choosing the optimal L, we
    # # should use only the training set, or use both the training and 
    # # the tuning set, combined.

    use_suffix = '-train+tune'

    # cssr_interface.run_CSSR(filename = fname + use_suffix, L = L_best, savefiles = True, showdot = False, is_multiline = True, showCSSRoutput = False)

    hist_length, Cmu, hmu, num_states = cssr_interface.parseResultFile(fname + use_suffix)

    CSM = get_CSM(fname = '{}{}'.format(fname, use_suffix))

    epsilon_machine = get_epsilon_machine(fname = '{}{}'.format(fname,use_suffix))

    states, L = get_equivalence_classes(fname + use_suffix) # A dictionary structure with the ordered pair
                                                          # (symbol sequence, state)

    zero_order_predict = generate_zero_order_CSM(fname + use_suffix)

    # Perform the filter on the 'dirty' data with the bits flipped.

    acc_flipped = numpy.zeros(len(ps))
    baseline_flipped = numpy.zeros(len(ps))

    for p_ind, p in enumerate(ps):
        generate_bit_flips('{}-test.dat'.format(fname), p = p, per_day = 96, num_days = 4)

        acc_flipped[p_ind] = numpy.mean(run_tests(fname = 'flipbit-{}p'.format(p), CSM = CSM, zero_order_CSM = zero_order_predict, states = states, epsilon_machine = epsilon_machine, L = L, L_max = L_max, metric = metric, print_predictions = False, print_state_series = False, verbose = False))
        baseline_flipped[p_ind] = numpy.mean(run_tests(fname = 'flipbit-{}p'.format(p), CSM = zero_order_predict, zero_order_CSM = zero_order_predict, states = states, epsilon_machine = epsilon_machine, L = L, L_max = L_max, metric = metric, type = 'zero'))

    ofile.write('{}\t'.format(users[user_num]))

    for val in acc_flipped:
        ofile.write('{:.4}\t'.format(val))

    for val in baseline_flipped:
        ofile.write('{:.4}\t'.format(val))

    ofile.write('\n')

ofile.close()