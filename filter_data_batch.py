import ipdb
import cssr_interface
import numpy
import collections
import sys

from filter_data_methods import *

from traintunetest import create_traintunetest

rank_start = 0 # The ith most highly tweeting user, where we start
                # counting at 0.

K = 3000-rank_start

users = get_K_users(K = K, start = rank_start)

metric_num = 0

Lopts = numpy.zeros(len(users))

Cmus  = numpy.zeros(len(users))

hmus = numpy.zeros(len(users))

n_states = numpy.zeros(len(users))

cm_rates = numpy.zeros(len(users))

baseline_rates = numpy.zeros(len(users))

ofile = open('filtering_results.tsv', 'w')

ofile.write('user_id\tRanking\tBaseline Rate\tCM Rate\tNumber of States\tCmu\thmu\tLopt\n')

for index, user_num in enumerate(range(len(users))):
    print 'On user {} of {}'.format(user_num, K)
    suffix = users[user_num]
    # suffix = 'FAKE'

    L_max = 10

    metrics = ['accuracy', 'precision', 'recall', 'F']

    metric = metrics[metric_num]

    Ls = range(1,L_max + 1)

    correct_by_L = numpy.zeros(len(Ls))

    fname = 'timeseries_alldays/byday-600s-{}'.format(suffix)

    create_traintunetest(fname = fname, ratios = (0.8, 0.1, 0.1), toprint = True) # Generate the train-tune-test partitioned data files

    # Get a 'zero-order' CSM that predicts as a 
    # biased coin. That is, if in the training 
    # set the user mostly tweets, always
    # predict tweeting. Otherwise, always
    # predict not-tweeting.

    zero_order_predict = generate_zero_order_CSM(fname + '-train')

    for L_ind, L_val in enumerate(Ls):
        # print 'Performing filter with L = {0}...\n\n'.format(L_val)

        cssr_interface.run_CSSR(filename = fname + '-train', L = L_val, savefiles = True, showdot = False, is_multiline = True, showCSSRoutput = False)

        CSM = get_CSM(fname = '{}-train'.format(fname))

        epsilon_machine = get_epsilon_machine(fname = '{}-train'.format(fname))

        # print CSM

        states, L = get_equivalence_classes(fname + '-train') # A dictionary structure with the ordered pair
                                                # (symbol sequence, state)

        correct_rates = run_tests(fname = fname + '-tune', CSM = CSM, zero_order_CSM = zero_order_predict, states = states, epsilon_machine = epsilon_machine, L = L, L_max = L_max, metric = metric, print_predictions = False, print_state_series = False)

        correct_by_L[L_ind] = correct_rates.mean()

    # print 'History Length\t{} Rate'.format(metric)

    # for ind in range(len(Ls)):
    #     print '{}\t{}'.format(Ls[ind], correct_by_L[ind])

    ind_L_best = correct_by_L.argmax()
    L_best = int(Ls[ind_L_best])

    # print 'The optimal L was {}.'.format(L_best)

    Lopts[index] = L_best

    cssr_interface.run_CSSR(filename = fname + '-train', L = L_best, savefiles = True, showdot = False, is_multiline = True, showCSSRoutput = False)

    hist_length, Cmu, hmu, num_states = cssr_interface.parseResultFile(fname + '-train')

    Cmus[index] = Cmu

    hmus[index] = hmu

    n_states[index] = num_states

    # print 'With this history length, the statistical complexity and entropy rate are:\nC_mu = {}\nh_mu = {}'.format(Cmu, hmu)

    # Perform filter on the held out test set, using the CSM from 
    # the L chosen by the tuning set, and compute the performance.

    CSM = get_CSM(fname = '{}-train'.format(fname))

    epsilon_machine = get_epsilon_machine(fname = '{}-train'.format(fname))

    states, L = get_equivalence_classes(fname + '-train') # A dictionary structure with the ordered pair
                                                          # (symbol sequence, state)

    test_correct_rates = run_tests(fname = fname + '-test', CSM = CSM, zero_order_CSM = zero_order_predict, states = states, epsilon_machine = epsilon_machine, L = L, L_max = L_max, metric = metric, print_predictions = False, print_state_series = False)

    # print 'The mean {} rate on the held out test set is: {}'.format(metric, numpy.mean(test_correct_rates))

    cm_rates[index] = test_correct_rates.mean()

    # Get the accuracy rate using the zero-order CSM.

    zero_order_rate = run_tests(fname = fname + '-test', CSM = zero_order_predict, zero_order_CSM = zero_order_predict, states = states, epsilon_machine = epsilon_machine, L = L, L_max = L_max, metric = metric, type = 'zero')

    baseline_rates[index] = zero_order_rate.mean()

    ofile.write('{}\t{}\t{:.4}\t{:.4}\t{}\t{}\t{}\t{}\n'.format(users[index], index + rank_start, baseline_rates[index], cm_rates[index], n_states[index], Cmus[index], hmus[index], Lopts[index]))

ofile.close()