# This file open the raster and .dot file representing
# the epsilon-machine for a given user. Users can be
# chosen based on their improvement rate over a 
# coinflip predictor (order 0 epsilon-machine).
#
# Can run this script from the command line as:
# 	open_files.py improvement_type improvement_rank
#
#	DMD, 270313-10-47

import ipdb
import cssr_interface
import numpy
import collections
import sys

import os

from filter_data_methods import *

# Import the uid <-> username lookup

rank_start = 0 # The ith most highly tweeting user, where we start
                # counting at 0.

K = 1000

users = get_K_users(K = K, start = rank_start)

if len(sys.argv) == 1:
	ind = 0

	improvement_type = 'improved'
else:
	improvement_type = sys.argv[1]
	ind = int(sys.argv[2])

# Import the uids of the improvement_type users, ranked from best->worst
# (for 'improved') and worst->best (for 'disimproved')

uids = [int(line) for line in open('user_improvements/{}.txt'.format(improvement_type))]

# Import the improvement scores for the users.

rate_lookup = numpy.loadtxt(fname = 'filtering_results.tsv', delimiter = '\t', skiprows = 1)

os.system('open rasters/raster-1s-{}.pdf'.format(users[uids[ind]]))
os.system('open timeseries/byday-600s-{}-train.dat_inf.dot'.format(users[uids[ind]]))

print 'For user ranked {} with userid {}...'.format(uids[ind], users[uids[ind]])
print 'The baseline rate was: {}'.format(rate_lookup[uids[ind], 1])
print 'The cm rate was: {}'.format(rate_lookup[uids[ind], 2])
print 'The improvement in rate was: {}'.format(rate_lookup[uids[ind], 2] - rate_lookup[uids[ind], 1])