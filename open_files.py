# This file opens the dot file for a specified
# user.
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

# rank_start = 0 # The ith most highly tweeting user, where we start
#                 # counting at 0.

# K = 1000

# users = get_K_users(K = K, start = rank_start)

with open('/Users/daviddarmon/Documents/Reference/R/Research/2013/sfi-dynComm/data/twitter_network_filtered_nodes.txt') as ofile:
    users = [line.strip() for line in ofile]

# if len(sys.argv) == 1:
# 	ind = 0
# else:
# 	ind = int(sys.argv[1])

inds = range(90, 100)

dir_prefix = '/Volumes/ddarmon-external/Reference/R/Research/Data/tweetpredict/timeseries_2011'

for ind in inds:
	os.system('open {}/byday-600s-{}-train+tune.dat_inf.dot'.format(dir_prefix, users[ind]))