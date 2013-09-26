import ipdb
import cssr_interface
import numpy
import collections
import sys

from filter_data_methods import *

from traintunetest import create_traintunetest_cv, cleanup_cv

year = '2011'

# rank_start = 0 # The ith most highly tweeting user, where we start
rank_start = 2907 # The ith most highly tweeting user, where we start
                # counting at 0.

# To get the proper place to start up, from the failed run, compute
# rank_start + user_num + 1.

K = 3000-rank_start

users = get_K_users(K = K, start = rank_start, year = year)

metric_num = 0

Lopts = numpy.zeros(len(users))

Cmus  = numpy.zeros(len(users))

hmus = numpy.zeros(len(users))

n_states = numpy.zeros(len(users))

cm_rates = numpy.zeros(len(users))

baseline_rates = numpy.zeros(len(users))

ofile = open('filtering_results-cv-{}-append.tsv'.format(year), 'w')

ofile.write('user_id\tRanking\tBaseline Rate\tCM Rate\tNumber of States\tCmu\thmu\tLopt\n')

# The number of folds to use in the cross-validation step.

num_folds = 10

for index, user_num in enumerate(range(len(users))):
    print 'On user {} of {}'.format(user_num, K)
    suffix = users[user_num]
    # suffix = 'FAKE'

    L_max = 10

    metrics = ['accuracy', 'precision', 'recall', 'F']

    metric = metrics[metric_num]

    Ls = range(1,L_max + 1)

    # correct_by_L is L_max by num_folds. Thus, each
    # *row* corresponds to the accuracy rate using a particular
    # value of L and each *column* corresponds to the accuracy
    # rates using all of the Ls on a particular fold.

    # We want to average across *rows*.

    correct_by_L = numpy.zeros((len(Ls), num_folds))

    fname = 'timeseries/byday-600s-{}'.format(suffix)

    numpy.random.seed(1)

    create_traintunetest_cv(fname = fname, ratios = (0.9, 0.1), k = num_folds) # Generate the train-tune-test partitioned data files

    # Get a 'zero-order' CSM that predicts as a 
    # biased coin. That is, if in the training 
    # set the user mostly tweets, always
    # predict tweeting. Otherwise, always
    # predict not-tweeting.

    for fold_ind in range(num_folds):
        zero_order_predict = generate_zero_order_CSM(fname + '-train-cv' + str(fold_ind))

        for L_ind, L_val in enumerate(Ls):
            # print 'Performing filter with L = {0}...\n\n'.format(L_val)

            cssr_interface.run_CSSR(filename = fname + '-train-cv' + str(fold_ind), L = L_val, savefiles = True, showdot = False, is_multiline = True, showCSSRoutput = False)

            CSM = get_CSM(fname = '{}-train-cv{}'.format(fname, fold_ind))

            epsilon_machine = get_epsilon_machine(fname = '{}-train-cv{}'.format(fname, fold_ind))

            # print CSM

            states, L = get_equivalence_classes(fname + '-train-cv' + str(fold_ind)) # A dictionary structure with the ordered pair
                                                    # (symbol sequence, state)

            correct_rates = run_tests(fname = fname + '-tune-cv' + str(fold_ind), CSM = CSM, zero_order_CSM = zero_order_predict, states = states, epsilon_machine = epsilon_machine, L = L, L_max = L_max, metric = metric, print_predictions = False, print_state_series = False, verbose = False)

            correct_by_L[L_ind, fold_ind] = correct_rates.mean()

    cleanup_cv(fname)

    ind_L_best = correct_by_L.mean(axis = 1).argmax()
    L_best = int(Ls[ind_L_best])

    # The while loop handles that, sometimes, when building a CSM using
    # the train+tune set, we fail to construct the the \epsilon-machine.
    # In these cases, we decrement L_best by 1 and try again.

    while True:
        try:
            Lopts[index] = L_best

            # use_suffix determines whether, after choosing the optimal L, we
            # should use only the training set, or use both the training and 
            # the tuning set, combined.

            use_suffix = '-train+tune'

            zero_order_predict = generate_zero_order_CSM(fname + use_suffix)

            cssr_interface.run_CSSR(filename = fname + use_suffix, L = L_best, savefiles = True, showdot = False, is_multiline = True, showCSSRoutput = False)

            hist_length, Cmu, hmu, num_states = cssr_interface.parseResultFile(fname + use_suffix)

            Cmus[index] = Cmu

            hmus[index] = hmu

            n_states[index] = num_states

            # Perform filter on the held out test set, using the CSM from 
            # the L chosen by the tuning set, and compute the performance.

            CSM = get_CSM(fname = '{}{}'.format(fname, use_suffix))

            break # If everything goes as planned, break out of the while loop.
        except IOError:
            print '\n\nNo CSM was generated using the train+tune set. Decrementing L_best by one...\n\n'

            L_best -= 1 # If we fail to build the CSM, decrement L_best by 1 and try again.

    epsilon_machine = get_epsilon_machine(fname = '{}{}'.format(fname,use_suffix))

    states, L = get_equivalence_classes(fname + use_suffix) # A dictionary structure with the ordered pair
                                                          # (symbol sequence, state)

    test_correct_rates = run_tests(fname = fname + '-test', CSM = CSM, zero_order_CSM = zero_order_predict, states = states, epsilon_machine = epsilon_machine, L = L, L_max = L_max, metric = metric, print_predictions = False, print_state_series = False, verbose = False)

    cm_rates[index] = test_correct_rates.mean()

    # Get the accuracy rate using the zero-order CSM.

    zero_order_rate = run_tests(fname = fname + '-test', CSM = zero_order_predict, zero_order_CSM = zero_order_predict, states = states, epsilon_machine = epsilon_machine, L = L, L_max = L_max, metric = metric, type = 'zero')

    baseline_rates[index] = zero_order_rate.mean()

    ofile.write('{}\t{}\t{:.4}\t{:.4}\t{}\t{}\t{}\t{}\n'.format(users[index], index + rank_start, baseline_rates[index], cm_rates[index], n_states[index], Cmus[index], hmus[index], Lopts[index]))

ofile.close()