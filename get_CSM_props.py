# Record the statistical complexity and entropy
# rate for each user from a CSM built using
# 9-fold cross-validation.

# DMD, 210913-22-15

import ipdb
import numpy
import pylab
import glob
from itertools import islice
from pandas import *

from matplotlib import cm

from extract_timeseries_methods import *

from filter_data_methods import *

start = 0
K = 3000-start

users = get_K_users(K = K, start = start)

with open('properties_3K.txt', 'w') as ofile:
	ofile.write('uid\tC\th\t|S|\n')

	for user in users:
		fname = 'timeseries_clean/byday-600s-{}-train+tune'.format(user)

		hist_length, Cmu, hmu, num_states = cssr_interface.parseResultFile(fname)

		ofile.write('{}\t{}\t{}\t{}\n'.format(user, Cmu, hmu, num_states))

# The properties_* file is sorted by the tweet rate, while the 
# community file is sorted by the uid.

# Goal: Plot (C, h) with colors given by the community label.

# Get the community for each user.

comm_file_prefix = '/Users/daviddarmon/Documents/R/Research/tweetpredict/community_structure/'

# comm_file_suffix = 'membership_by_user_3K_connected_weighted-600s.txt'
comm_file_suffix = 'membership_by_user_3K_connected_weighted_IC-600s-mm.txt'
# comm_file_suffix = 'membership_by_user_3K_unweighted.txt'

comm_file = comm_file_prefix + comm_file_suffix

# Create a lookup from user id (uid) to the associated community.

uid_to_comm = {}

with open(comm_file) as ofile:
	for line in islice(ofile, 1, None):
		uid, comm = map(int, line.strip().split('\t'))

		uid_to_comm[uid] = comm

# Get out the properties associated with the CSM

df = DataFrame.from_csv('properties_3K.txt', sep='\t')

comms = numpy.empty(len(users))

for ind in range(len(users)):
	comms[ind] = uid_to_comm.get(int(users[ind]), -1)

# Plot (h, C) across the communities.

comms_of_interest = range(0, 9)
# comms_of_interest = range(0, len(numpy.unique(comms)))

for ind in range(len(comms_of_interest)):
	comm_ind = comms_of_interest[ind]

	comm_bools = (comms == comm_ind)

	pylab.figure()
	pylab.scatter(df.h[comm_bools], df.C[comm_bools], c = cm.jet(1.*ind/len(comms_of_interest)))
	pylab.xlim(0, 1)
	pylab.ylim(0, 8)
	pylab.xlabel('$h$')
	pylab.ylabel('$C$')

pylab.show()