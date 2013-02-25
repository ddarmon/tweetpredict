import ipdb

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
	ofile = open('{0}-train.dat_results'.format(fname))

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

# suffix = '184274305'
# suffix = '14448173'
# suffix = '1712831'
# suffix = '196071730'
suffix = 'FAKE'

fname = 'byday-600s-{}'.format(suffix)

CSM = get_CSM(fname = fname)

print CSM

states, L = get_equivalence_classes(fname + '-train') # A dictionary structure with the ordered pair
										# (symbol sequence, state)

# Open the file containing the time series from the 
# to-be-predicted time period

tunefile = open('{}-tune.dat'.format(fname))

tunedays = [line.rstrip() for line in tunefile]

tunefile.close()

for day in tunedays:

	prediction = CSM_filter(CSM, states, ts = day, L = L)

	# Visually compare the prediction to the true timeseries

	print 'True Timeseries / Predicted Timeseries\n'

	print day[L-1:] + '\n\n' + prediction + '\n'