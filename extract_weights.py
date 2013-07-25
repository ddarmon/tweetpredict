# Code to get out the weight between two users
# (either normalized mutual information or 
# informational coherence).

# DMD, 250713-16-32

import ipdb
import cssr_interface
import numpy
import collections
import glob
import pylab

from filter_data_methods import *
from traintunetest import create_traintunetest_cv, cleanup_cv

users = get_K_users(K = 3000, start = 0)

weights = numpy.zeros((3000, 3000))

ofile = open('mutual-information-600s.dat')

for line_ind, line in enumerate(ofile):
	lsplit = line.split('\t')

	from_ind = int(lsplit[0])
	to_ind   = int(lsplit[1])
	weight   = float(lsplit[2])

	weights[from_ind, to_ind] = weight

ofile.close()

# A dictionary of the form {uid : rank}

user_lookup = {}

for ind, user in enumerate(users):
	user_lookup[user] = ind

# The user pair we would like to look up the weight
# for.

# uoi = ('10876852', '46958309')
# uoi = ('17155995', '21429357')
# uoi = ('9147742', '198911524')
# uoi = ('17925141', '198911524')
uoi = ('13693042', '14384696')

rank1 = user_lookup[uoi[0]]
rank2 = user_lookup[uoi[1]]

if rank1 < rank2:
	print weights[rank1, rank2]
else:
	print weights[rank2, rank1]