####################################################################################
#
#	A file that takes in a .dat file (a time series that has been discretiezed)
#	and outputs 

import cssr_interface
import sys
import pylab
import numpy
import ipdb
import glob

# Use CSSR to generate the CSM files

fnames = glob.glob('timeseries/*-30.dat')

fnames = map(lambda x : x[:-4], fnames) # Strip off the '.dat'

if len(sys.argv) > 1:
	historyLength = sys.argv[1]
else:
	historyLength = 2

Cmus = []

for ind, fname in enumerate(fnames):
    if ind%10 == 0:
        print 'On file {}...\n'.format(ind)
        
    # fname = fnames[ind]
    
    cssr_interface.run_CSSR(filename = fname, L = historyLength, savefiles = True, showdot = False)

    hist_length, Cmu, hmu, num_states = cssr_interface.parseResultFile(fname)
    
    Cmus.append(Cmu)

numpy.array(fnames)[numpy.array(Cmus) != 0]

ofile = open('top_complexity.dat', 'w')

for ind in range(len(Cmus)):
    if Cmus[ind] != 0:
        # print '{}\t\t{}'.format(Cmus[ind], fnames[ind].split('_')[2].split('-')[0])
        ofile.write('{}\t{}\n'.format(fnames[ind].split('_')[2].split('-')[0], Cmus[ind]))

ofile.close()