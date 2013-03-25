import ipdb
import cssr_interface
import numpy
import collections
import sys

from filter_data_methods import *

rank_start = 0 # The ith most highly tweeting user, where we start
                # counting at 0.

K = 40

users = get_K_users(K = K, start = rank_start)

metric_num = 0

Lopts = numpy.zeros(len(users))

Cmus  = numpy.zeros(len(users))

n_states = numpy.zeros(len(users))

cm_rates = numpy.zeros(len(users))

baseline_rates = numpy.zeros(len(users))

for index, user_num in enumerate(range(len(users))):
    suffix = users[user_num]
    # suffix = 'FAKE'

    L_max = 11

    metrics = ['accuracy', 'precision', 'recall', 'F']

    metric = metrics[metric_num]

    Ls = range(1,L_max)

    correct_by_L = numpy.zeros(len(Ls))

    fname = 'timeseries/byday-600s-{}'.format(suffix)

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

        correct_rates = run_tests(fname = fname + '-tune', CSM = CSM, zero_order_CSM = zero_order_predict, states = states, epsilon_machine = epsilon_machine, L = L, L_max = L_max, metric = metric)

        correct_by_L[L_ind] = correct_rates.mean()

    print 'History Length\t{} Rate'.format(metric)

    for ind in range(len(Ls)):
        print '{}\t{}'.format(Ls[ind], correct_by_L[ind])

    ind_L_best = correct_by_L.argmax()
    L_best = int(Ls[ind_L_best])

    print 'The optimal L was {}.'.format(L_best)

    Lopts[index] = L_best

    cssr_interface.run_CSSR(filename = fname + '-train', L = L_best, savefiles = True, showdot = False, is_multiline = True, showCSSRoutput = False)

    hist_length, Cmu, hmu, num_states = cssr_interface.parseResultFile(fname + '-train')

    Cmus[index] = Cmu

    n_states[index] = num_states

    print 'With this history length, the statistical complexity and entropy rate are:\nC_mu = {}\nh_mu = {}'.format(Cmu, hmu)

    # Perform filter on the held out test set, using the CSM from 
    # the L chosen by the tuning set, and compute the performance.

    CSM = get_CSM(fname = '{}-train'.format(fname))

    epsilon_machine = get_epsilon_machine(fname = '{}-train'.format(fname))

    states, L = get_equivalence_classes(fname + '-train') # A dictionary structure with the ordered pair
                                                          # (symbol sequence, state)

    test_correct_rates = run_tests(fname = fname + '-test', CSM = CSM, zero_order_CSM = zero_order_predict, states = states, epsilon_machine = epsilon_machine, L = L, metric = metric)

    print 'The mean {} rate on the held out test set is: {}'.format(metric, numpy.mean(test_correct_rates))

    cm_rates[index] = test_correct_rates.mean()

    # Get the accuracy rate using the zero-order CSM.

    zero_order_rate = run_tests(fname = fname + '-test', CSM = zero_order_predict, zero_order_CSM = zero_order_predict, states = states, epsilon_machine = epsilon_machine, L = L, metric = metric, type = 'zero')

    baseline_rates[index] = zero_order_rate.mean()

    print 'The mean {} rate using a biased coin is: {}'.format(metric, numpy.mean(zero_order_rate))

    import os

    # os.system('open rasters/raster-1s-{}.pdf'.format(suffix))
    # os.system('open rasters/raster-600s-{}.pdf'.format(suffix))

print 'Ranking\tBaseline Rate\tCM Rate'

for index in range(len(cm_rates)):
    print '{}\t{}\t{}'.format(index + rank_start, baseline_rates[index], cm_rates[index])

print 'Ranking\tLopt\tNumber of States\tCmu'

for index in range(len(cm_rates)):
    print '{}\t{}\t{}\t\t{}'.format(index + rank_start, Lopts[index], n_states[index], Cmus[index])

print 'Ranking\tBaseline Rate\tCM Rate\t\tNumber of States'

for index in range(len(cm_rates)):
    print '{}\t{:.3}\t\t{:.3}\t\t{}'.format(index + rank_start, baseline_rates[index], cm_rates[index], n_states[index])

# Print the results to a file for further analysis.

ofile = open('filtering_results.tsv', 'w')

ofile.write('Ranking\tBaseline Rate\tCM Rate\tNumber of States\tCmu\tLopt\n')

for index in range(len(cm_rates)):
    ofile.write('{}\t{:.3}\t{:.3}\t{}\t{}\t{}\n'.format(index + rank_start, baseline_rates[index], cm_rates[index], n_states[index], Cmus[index], Lopts[index]))

ofile.close()