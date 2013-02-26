import ipdb
import cssr_interface
import numpy

def get_equivalence_classes(fname):
	ofile = open('{0}.dat_results'.format(fname))

	# Start at state = 0, and then loop up to state = N, where 
	# N is the number of states

	state = 0
	state_list = {}

	ofile.readline()

	line = ofile.readline()

	while line != '':
		while line.split()[0] != 'distribution:':
			state_list[line.rstrip()] = state
			
			line = ofile.readline()
		state = state + 1
		for lineind in xrange(4):
			ofile.readline()
		line = ofile.readline()

	ofile.close()

	# Get out the history length used.

	L = -1

	for history in state_list:
		L = max(L, len(history))

	return state_list, L

def get_CSM(fname):
	ofile = open('{0}.dat_results'.format(fname))

	CSM = {} # A dictionary structure for the CSM

	line = ofile.readline()

	while line != '':
		state = int(line.split()[2])

		while 'distribution' not in line:
			line = ofile.readline()

		CSM[state] = float(line.split()[-1])

		for ind in xrange(3):
			ofile.readline()

		line = ofile.readline()

	ofile.close()

	return CSM

def CSM_filter(CSM, states, ts, L):
	# We look at most L time steps into the past. We can
	# synchronize on L - 1 timesteps, by virtue of how CSSR
	# does its filtering.

	# Note: We'll start predicting *L-1* days in. So,
	# our first prediction will be for day L.

	prediction = ''

	# We can predict on day L, since we have L - 1 days.

	cur_state = states.get(ts[0:L-1], 'M')

	if cur_state == 'M':
		print 'Warning: The sequence \'{}\' isn\'t allowed by this CSM!'.format(ts[0:L])

		prediction += 'M'
	else:
		if CSM[int(cur_state)] > 0.5:
			prediction += '1'
		else:
			prediction += '0'

	for i in xrange(L, len(ts)):
		cur_state = states.get(ts[i - L:i], 'M')

		if cur_state == 'M':
			print 'Warning: The sequence \'{}\' isn\'t allowed by this CSM!'.format(ts[i - L:i])

			prediction += 'M'
		else:
			if CSM[int(cur_state)] > 0.5:
				prediction += '1'
			else:
				prediction += '0'
	return prediction

def compute_metrics(ts_true, ts_prediction):
	correct = 0

	for char_ind in xrange(len(ts_true)):
		if ts_true[char_ind] == ts_prediction[char_ind]:
			correct += 1

	accuracy_rate = correct / float(len(ts_true))

	return accuracy_rate

def run_tests(fname, CSM, states, L):
	# NOTE: The filename should *already have* the suffix
	# '-tune', '-test', etc.

	datafile = open('{}.dat'.format(fname))

	days = [line.rstrip() for line in datafile]

	datafile.close()

	correct_rates = numpy.zeros(len(days))

	for day_ind, day in enumerate(days):

		prediction = CSM_filter(CSM, states, ts = day, L = L)

		# Visually compare the prediction to the true timeseries

		print 'True Timeseries / Predicted Timeseries\n'

		print day[L-1:] + '\n\n' + prediction + '\n'

		ts_true = day[L-1:]
		ts_prediction = prediction

		# For a given L, compute the accuracy rate on the tuning set.
		# That is, compute the proportion of the time series
		# predicted correctly.

		correct_rates[day_ind] = compute_metrics(ts_true, ts_prediction)

	return correct_rates

# suffix = '184274305'
# suffix = '14448173'
# suffix = '1712831'
# suffix = '196071730'
suffix = 'FAKE'

Ls = range(1, 11)

correct_by_L = numpy.zeros(len(Ls))

for L_ind, L_val in enumerate(Ls):
	print 'Performing filter with L = {0}...\n\n'.format(L_val)
	fname = 'byday-600s-{}'.format(suffix)

	cssr_interface.run_CSSR(filename = fname + '-train', L = L_val, savefiles = True, showdot = False, is_multiline = True, showCSSRoutput = False)

	CSM = get_CSM(fname = '{}-train'.format(fname))

	# print CSM

	states, L = get_equivalence_classes(fname + '-train') # A dictionary structure with the ordered pair
											# (symbol sequence, state)

	correct_rates = run_tests(fname = fname + '-tune', CSM = CSM, states = states, L = L)

	correct_by_L[L_ind] = correct_rates.mean()

print 'History Length\tCorrect Rate'

for ind in range(len(Ls)):
	print '{}\t{}'.format(Ls[ind], correct_by_L[ind])

ind_L_best = correct_by_L.argmax()
L_best = int(Ls[ind_L_best])

print 'The optimal L was {}.'.format(L_best)

cssr_interface.run_CSSR(filename = fname + '-train', L = L_best, savefiles = True, showdot = True, is_multiline = True, showCSSRoutput = False)

hist_length, Cmu, hmu, num_states = cssr_interface.parseResultFile(fname + '-train')

print 'With this history length, the statistical complexity and entropy rate are:\nC_mu = {}\nh_mu = {}'.format(Cmu, hmu)

# Perform filter on the held out test set, using the CSM from 
# the L chosen by the tuning set, and compute the performance.

CSM = get_CSM(fname = '{}-train'.format(fname))

states, L = get_equivalence_classes(fname + '-train') # A dictionary structure with the ordered pair
													  # (symbol sequence, state)

correct_rates = run_tests(fname = fname + '-test', CSM = CSM, states = states, L = L)

print 'The accuracy rate on the held out test set is: {}'.format(numpy.mean(correct_rates))