####################################################################################
#
#	A file that takes in a .dat file (a time series that has been discretiezed)
#	and outputs 

import cssr_interface
import sys
import pylab
import numpy
import ipdb

# Use CSSR to generate the CSM files

fname = 'timeseries/twitter_ts-1800'

if len(sys.argv) > 1:
	historyLength = sys.argv[1]
else:
	historyLength = 2

cssr_interface.run_CSSR(filename = fname, L = historyLength, savefiles = True, showdot = True)

hist_length, Cmu, hmu, num_states = cssr_interface.parseResultFile(fname)