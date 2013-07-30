# This code compares the detected communities across *types* of communities.
# See notes from 30 July 2013 for the genesis of this idea.

# 	DMD, 300713-15-14

import ipdb
import cssr_interface
import numpy
import collections
import glob
import pylab

from filter_data_methods import *
from traintunetest import create_traintunetest_cv, cleanup_cv

# Get out the top K users, where K is typically 3000.

users = get_K_users(K = 3000, start = 0)

def get_communities_dict(fname):
	communities = {}

	ofile = open(fname)

	line = ofile.readline()

	line = ofile.readline()

	while line != '':
		lsplit = line.split()

		communities[lsplit[0]] = int(lsplit[1])

		line = ofile.readline()

	return communities

# Dictionaries of the form {userid : community_id}

type1 = 'membership_by_user_3K_weighted_IC-600s-mm'
type2 = 'membership_by_user_3K_weighted-600s'

communities_method1 = get_communities_dict(fname = '/Users/daviddarmon/Documents/R/Research/tweetpredict/community_structure/{}.txt'.format(type1))
communities_method2 = get_communities_dict(fname = '/Users/daviddarmon/Documents/R/Research/tweetpredict/community_structure/{}.txt'.format(type2))

# Populate two binary vectors each of length len(users)*(len(users) - 1)/2,
# where an entry is 1 is the users are in the same community and 0 otherwise.

Nv = len(users)

binary1 = numpy.zeros(Nv*(Nv - 1)/2.)
binary2 = binary1.copy()

count = 0

for ind1 in range(len(users)):

	user1 = users[ind1]

	for ind2 in range(ind1 + 1, len(users)):
		user2 = users[ind2]

		if communities_method1.get(user1, -1) == communities_method1.get(user2, -1):
			binary1[count] = 1

		if communities_method2.get(user1, -1) == communities_method2.get(user2, -1):
			binary2[count] = 1

		count += 1

print 'The similarity between the two clusterings is {}...'.format(numpy.sum(binary1*binary2)/numpy.max((numpy.sum(binary1), numpy.sum(binary2))))