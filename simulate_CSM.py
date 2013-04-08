import cssr_interface
import pylab
import numpy
import collections
import ipdb

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

tosave = True # Whether or not to save the timeseries to a file.

toplot = True # Whether or not to display a raster plot of the sequence

suffixes = ['1712831', '16290327', '184274305', '196071730', '32451329', '178808746']

prefix = 'byday-600s-{}'.format(suffixes[-1])
# prefix = 'byday-1s-16290327'
# prefix = 'off_even_process'
num_its = 96
fname = '{}.dat_inf.dot'.format(prefix)

ofile = open(fname)

line = ofile.readline()

while line[0] != '0':
	line = ofile.readline()

CSM = collections.defaultdict(state)

while line != '}':
	lsplit = line.split()

	from_state = lsplit[0]
	to_state = lsplit[2]
	esymbol = int(lsplit[5][1])
	eprob = float(lsplit[6])
	
	if esymbol == 0:
		CSM[from_state].setEmit0State(to_state, eprob)
	elif esymbol == 1:
		CSM[from_state].setEmit1State(to_state)
	
	line = ofile.readline()

ofile.close()

n_states = len(CSM)

num_sims = 70

urand = numpy.random.rand(num_its, num_sims)

symbol_seq = numpy.empty((num_its, num_sims), dtype = 'int32')

for cur_sim in xrange(num_sims):
	cur_state = str(numpy.random.randint(0, n_states))

	for ind in range(num_its):
		# The following probability isn't foolproof, since
		# we could run into the problem of pemit0 = None

		if urand[ind, cur_sim] < CSM[cur_state].p_emit0:
			symbol_seq[ind, cur_sim] = 0
			cur_state = CSM[cur_state].s_emit0
		else:
			symbol_seq[ind, cur_sim] = 1
			cur_state = CSM[cur_state].s_emit1

if toplot:
	f, axarr = pylab.subplots(num_sims, sharex=True)

	for axind in range(num_sims):
		axarr[axind].vlines(numpy.arange(symbol_seq.shape[0])[symbol_seq[:, axind] == 1], -0.5, 0.5)
		axarr[axind].yaxis.set_visible(False)

	pylab.show()

if tosave:
	ofile = open('{}_sim.dat'.format(prefix), 'w')

	for trial in xrange(symbol_seq.shape[1]):
		for symbol in symbol_seq[:, trial]:
			ofile.write(str(symbol))

		ofile.write('\n')

	ofile.close()