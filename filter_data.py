import ipdb
import cssr_interface
import numpy
import collections
import sys

class state:
	def __init__(self, p_emit0 = None, s_emit0 = None, s_emit1 = None):
		self.p_emit0 = p_emit0
		self.s_emit0 = s_emit0
		self.s_emit1 = s_emit1
	
	
	def setEmit0State(self, state, prob):
		self.s_emit0 = state
		self.p_emit0 = prob
	
	def setEmit1State(self, state):
		self.s_emit1 = state

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

def get_epsilon_machine(fname):
	ofile = open('{}.dat_inf.dot'.format(fname))

	line = ofile.readline()

	while line[0] != '0':
		line = ofile.readline()

	epsilon_machine = collections.defaultdict(state)

	while line != '}':
		lsplit = line.split()

		from_state = lsplit[0]
		to_state = lsplit[2]
		esymbol = int(lsplit[5][1])
		eprob = float(lsplit[6])
		
		if esymbol == 0:
			epsilon_machine[from_state].setEmit0State(to_state, eprob)
		elif esymbol == 1:
			epsilon_machine[from_state].setEmit1State(to_state)
		
		line = ofile.readline()

	ofile.close()

	return epsilon_machine

def CSM_filter(CSM, states, epsilon_machine, ts, L):
	# We look at most L time steps into the past. We can
	# synchronize on L - 1 timesteps, by virtue of how CSSR
	# does its filtering.

	# Note: We'll start predicting *L-1* days in. So,
	# our first prediction will be for day L.

	prediction = ''

	state_series = ''

	# We can predict on day L, since we have L - 1 days.

	cur_state = str(states.get(ts[0:L-1], 'M'))

	state_series += cur_state

	synchronized = False # Whether or not we've synchronized to the current state.
						 # Basically, can we tell what state we're in yet.

	# WE MIGHT HAVE TO REPEAT THIS MULTIPLE TIMES!!!

	if cur_state == 'M':
		print 'Warning: The sequence \'{}\' isn\'t allowed by this CSM!'.format(ts[0:L-1])

		prediction += 'M'
	else:
		if CSM[int(cur_state)] > 0.5:
			prediction += '1'
		else:
			prediction += '0'

		synchronized = True

	for i in xrange(L, len(ts)):
		# Now that we've synchronized, we get the new state
		# by looking at the transition that *must* have
		# occurred, given our epsilon machine.

		if synchronized:
			if ts[i-1] == '1':
				cur_state = epsilon_machine[str(cur_state)].s_emit1
			elif ts[i-1] == '0':
				cur_state = epsilon_machine[str(cur_state)].s_emit0

			if cur_state == None:
				# We have made a transition that isn't allowed by the epsilon
				# machine, so we need to resync.

				synchronized = False

				cur_state = states.get(ts[i - L:i], 'M')

				if cur_state == 'M':
					print 'Warning: The sequence \'{}\' isn\'t allowed by this CSM!'.format(ts[i - L:i])

					prediction += 'M'
				else:
					if CSM[int(cur_state)] > 0.5:
						prediction += '1'
					else:
						prediction += '0'

					synchronized = True
			else: # We haven't made a disallowed transition, so we can update like usual.
				if CSM[int(cur_state)] > 0.5:
					prediction += '1'
				else:
					prediction += '0'

			state_series += ';{}'.format(str(cur_state))
		else:
			cur_state = states.get(ts[i - L:i], 'M')

			if cur_state == 'M':
				print 'Warning: The sequence \'{}\' isn\'t allowed by this CSM!'.format(ts[i - L:i])

				prediction += 'M'
			else:
				if CSM[int(cur_state)] > 0.5:
					prediction += '1'
				else:
					prediction += '0'

				synchronized = True

	print state_series
	return prediction

def compute_precision(ts_true, ts_prediction):
	numerator = 0    # In precision, the numerator is the number of true
						 # positives which are predicted correctly.
	denominator = 0	 # In precision, the denominator is the total number
					 # of predicted positives.

	for char_ind in xrange(len(ts_true)):
		if ts_prediction[char_ind] == '1': # We predicted a 1
			denominator += 1

			if ts_true[char_ind] == '1': # We predicted a 1, and it is also the right
									   # answer.
				numerator += 1

	if denominator == 0:
		print 'Warning: you didn\'t predict any tweets! By convention, set precision to 1.'

		precision = 1
	else:
		precision = numerator/float(denominator)

	return precision

def compute_recall(ts_true, ts_prediction):
	numerator = 0    # In precision, the numerator is the number of true
						 # positives which are predicted correctly.
	denominator = 0	 # In precision, the denominator is the total number
					 # of true positives.

	for char_ind in xrange(len(ts_true)):
		if ts_true[char_ind] == '1': # The true value is a 1
			denominator += 1

			if ts_prediction[char_ind] == '1': # We predicted a 1, and it is also the right
									   		 # answer.
				numerator += 1

	if denominator == 0:
		print 'Warning: no tweets were in this day! By convention, set recall to 1.'

		recall = 1
	else:
		recall = numerator/float(denominator)

	return recall

def compute_metrics(ts_true, ts_prediction, metric = None):
	# choices: 'accuracy', 'precision', 'recall', 'F'

	if metric == None or metric == 'accuracy': # By default, compute accurracy rate.
		correct = 0

		for char_ind in xrange(len(ts_true)):
			if ts_true[char_ind] == ts_prediction[char_ind]:
				correct += 1

		accuracy_rate = correct / float(len(ts_true))

		return accuracy_rate
	elif metric == 'precision':
		precision = compute_precision(ts_true, ts_prediction)

		return precision

	elif metric == 'recall':
			
		recall = compute_recall(ts_true, ts_prediction)

		return recall

	elif metric == 'F':
		precision = compute_precision(ts_true, ts_prediction)
		recall = compute_recall(ts_true, ts_prediction)

		if (precision + recall) == 0:
			F = 0
		else:
			F = 2*precision*recall/float(precision + recall)

		return F

	else:
		print "Please choose one of \'accuracy\', \'precision\', \'recall\', or \'F\'."

		return None

def run_tests(fname, CSM, states, epsilon_machine, L, L_max = None, metric = None):
	# NOTE: The filename should *already have* the suffix
	# '-tune', '-test', etc.

	# If a maximum L wasn't passed (i.e. we're not trying to 
	# compare CSMs on the same timeseries data), assume that
	# we want to use *all* of the timeseries in our test.

	if L_max == None:
		L_max = L

	datafile = open('{}.dat'.format(fname))

	days = [line.rstrip() for line in datafile]

	datafile.close()

	correct_rates = numpy.zeros(len(days))

	for day_ind, day in enumerate(days):

		prediction = CSM_filter(CSM, states, epsilon_machine, ts = day, L = L)

		# Visually compare the prediction to the true timeseries

		print 'True Timeseries / Predicted Timeseries\n'

		print day[L-1:] + '\n\n' + prediction + '\n'

		ts_true = day[L_max-1:]
		ts_prediction = prediction[(L_max - L):] # This bit makes sure we predict
												 # on the same amount of timeseries
												 # regardless of L. Otherwise we 
												 # might artificially inflate the
												 # accuracy rate for large L CSMs.

		# For a given L, compute the metric rate on the tuning set.
		# Allowed metrics are 'accuracy', 'precision', 'recall', 'F'.

		correct_rates[day_ind] = compute_metrics(ts_true, ts_prediction, metric = metric)

	return correct_rates

def get_top_K_users(K = 5):
	ofile = open('user_lookup/tweet_counts_labeled.tsv')

	ofile.readline()

	users = []

	for k in range(K):
		line = ofile.readline().split('\t')

		users.append(line[0])

	ofile.close()

	return users

users = get_top_K_users(20)

if len(sys.argv) < 2:
	user_num = 4
else:
	user_num = int(sys.argv[1])

suffix = users[user_num]
# suffix = 'FAKE'

L_max = 11

metrics = ['accuracy', 'precision', 'recall', 'F']

metric = metrics[0]

Ls = range(1,L_max)

correct_by_L = numpy.zeros(len(Ls))

for L_ind, L_val in enumerate(Ls):
	print 'Performing filter with L = {0}...\n\n'.format(L_val)
	fname = 'byday-600s-{}'.format(suffix)

	cssr_interface.run_CSSR(filename = fname + '-train', L = L_val, savefiles = True, showdot = False, is_multiline = True, showCSSRoutput = False)

	CSM = get_CSM(fname = '{}-train'.format(fname))

	epsilon_machine = get_epsilon_machine(fname = '{}-train'.format(fname))

	# print CSM

	states, L = get_equivalence_classes(fname + '-train') # A dictionary structure with the ordered pair
											# (symbol sequence, state)

	correct_rates = run_tests(fname = fname + '-tune', CSM = CSM, states = states, epsilon_machine = epsilon_machine, L = L, L_max = L_max, metric = metric)

	correct_by_L[L_ind] = correct_rates.mean()

print 'History Length\t{} Rate'.format(metric)

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

epsilon_machine = get_epsilon_machine(fname = '{}-train'.format(fname))

states, L = get_equivalence_classes(fname + '-train') # A dictionary structure with the ordered pair
													  # (symbol sequence, state)

correct_rates = run_tests(fname = fname + '-test', CSM = CSM, states = states, epsilon_machine = epsilon_machine, L = L, metric = metric)

print 'The mean {} rate on the held out test set is: {}'.format(metric, numpy.mean(correct_rates))

import os

os.system('open rasters/raster-1s-{}.pdf'.format(suffix))
# os.system('open rasters/raster-600s-{}.pdf'.format(suffix))