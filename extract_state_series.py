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

def save_total_state_series(fname):
	# Get out all the CSM related structures we need.

	CSM = get_CSM(fname = '{}-train+tune'.format(fname))

	epsilon_machine = get_epsilon_machine(fname = '{}-train+tune'.format(fname))

	zero_order_CSM = generate_zero_order_CSM(fname + '-train+tune')

	# Get out the timeseries.

	ofile = open('{}.dat'.format(fname))

	days = [line.rstrip('\n') for line in ofile]

	states, L = get_equivalence_classes('{}-train+tune'.format(fname))

	ofile = open('{}-states.dat'.format(fname), 'w')

	for day in days:
		prediction, state_series = CSM_filter(CSM, zero_order_CSM, states, epsilon_machine, day, L, verbose = False)

		ofile.write('{}\n'.format(state_series))

	ofile.close()

users = get_K_users(K = 3000, start = 0)

ICs = numpy.zeros((len(users), len(users)))

for file1_ind in range(43, 44):
	# We only have to *build* the machines the first pass through
	# the outer loop.

	print file1_ind

	fname1 = 'timeseries_clean/byday-{}s-{}'.format(ires, users[file1_ind])

	save_total_state_series(fname1)