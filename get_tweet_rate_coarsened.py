import numpy
import collections
import sys

from filter_data_methods import *

from traintunetest import create_traintunetest

users = get_top_K_users(5000)

wfile = open('tweet_rate_coarsened.dat', 'w')

wfile.write('user_id\ttweets per unit time\n')

for user_num in range(0, 3000):
	print 'Working on user {}...'.format(user_num)
	user_id = users[user_num]

	suffix = user_id

	fname = 'timeseries_alldays/byday-600s-{}.dat'.format(suffix)

	ofile = open(fname)

	line = ofile.readline().rstrip('\n')

	# The number of bins. Each bin to 10 minutes of time.

	num_bins = len(line)

	daycount = 0

	onecount = 0 # A counter for the number of 1s across
				 # all of the days.

	while line != '':
		for character in line:
			if character == '1':
				onecount += 1

		daycount += 1

		line = ofile.readline()

	ofile.close()

	# Print the number of tweets per unit time.

	if daycount == 0: # Account for when no tweets occur in the specified window.
		tweets_per_minute  = 0
	else:
		tweets_per_minute = onecount/float(daycount*num_bins)

	wfile.write('{}\t{}\n'.format(user_id, tweets_per_minute))

wfile.close()