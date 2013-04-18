import numpy
import collections
import sys

from filter_data_methods import *

from traintunetest import create_traintunetest

users = get_top_K_users(3000)

wfile = open('tweet_rate_uncoarsened.dat', 'w')

wfile.write('user_id\ttweets per minute\n')

for user_num in range(0, 3000):
	print 'Working on user {}...'.format(user_num)
	user_id = users[user_num]

	suffix = user_id

	fname = 'timeseries_alldays/byday-1s-{}.dat'.format(suffix)

	ofile = open(fname)

	line = ofile.readline().rstrip('\n')

	# Keep track of the line we're on, since
	# we want to skip over the 'bad' days in
	# the dataset.

	linecount = 0

	# The number of bins. Each bin corresponds
	# to a single second.

	num_bins = len(line)

	daycount = 0

	onecount = 0 # A counter for the number of 1s across
				 # all of the days.

	while line != '':
		if (11 <= linecount <= 23) or (62 <= linecount <= 68):
			pass
		else:
			for character in line:
				if character == '1':
					onecount += 1

			daycount += 1

		line = ofile.readline()

		linecount += 1

	ofile.close()

	# Print the number of tweets per minute.
	# Taking from tweets per second to tweets per
	# minute gives requires:
	# 	tweets/second * 60 seconds / 1 minute

	tweets_per_minute = onecount/float(daycount*num_bins)*60

	wfile.write('{}\t{}\n'.format(user_id, tweets_per_minute))

wfile.close()