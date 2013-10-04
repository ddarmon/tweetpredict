# A script to compute the overlap in users between the 2011 and
# 2012 data sets.
#
# 	DMD, 260913-11-45

from sets import Set
from itertools import islice

from filter_data_methods import *

group1 = [] # The 2011 Twitter accounts
group2 = [] # The 2012 Twitter accounts

with open('user_lookup/tweet_counts-2011.tsv') as ofile:
	for line in islice(ofile, 1, None):
		group1.append(line.split('\t')[0])

with open('user_lookup/tweet_counts.tsv') as ofile:
	for line in islice(ofile, 1, None):
		group2.append(line.split('\t')[0])

intersection = Set(group1) & Set(group2)

print('The overlap is {} users out of {} from 2011 and {} from 2012.'.format(len(intersection), len(group1), len(group2)))

top_users_group1 = get_K_users(K = 3000, start = 0, year = '2011')
top_users_group2 = get_K_users(K = 3000, start = 0)

print('Of the top 3000 users, the overlap is {}.'.format(len(Set(top_users_group1) & Set(top_users_group2) )))