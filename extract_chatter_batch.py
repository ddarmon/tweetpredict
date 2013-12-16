# Extract the number of users active at any given time 
# instant in the 15K network.
#
# This allows us to work on Keith's idea of extracting
# network structure using the properties of the timeseries.
#
#   DMD, 041113-15-18

import ipdb
import numpy
import pylab
import datetime
import random

from dividebyday import divide_by_day, binarize_timeseries

from extract_timeseries_methods import *

# files = ['../timeseries_a.tsv', '../timeseries_b.tsv', '../timeseries_c.tsv']
files = ['../timeseries_2011.tsv']

# Create hash table of the form {userid : [time_of_tweet1, time_of_tweet2, ..., time_of_tweetT]}

user_dict = {}

time_all_tweets = [] # Keep track of when *all* of the tweets occur, so we can
                     # set a relative t = 0.

for fname in files:
    ofile = open(fname)

    count = 0

    for line in ofile:
        if count % 100000 == 0:
            print 'On line {}\n'.format(count)

        count += 1

        lsplit = line.split('\t')

        time = lsplit[0] # Get out the time of the tweet
        user = lsplit[1].rstrip() # Get out the userid of the person who tweeted
        
        year, month, day, hour, minute, second = map(int, parsedate(time))
        
        cur_time = datetime.datetime(year = year, month = month, day = day, hour = hour, minute = minute, second = second)
        
        time_all_tweets.append(cur_time)
        
        if user in user_dict: # If the user is in the dictionary, add the time to the list of times they tweeted.
            user_dict[user][cur_time] = 1
        else: # If not, add the user to the dictionary and record the time of their first tweet
            user_dict[user] = {cur_time : 1}

    ofile.close()

# Create a 2 * (number of users) array. The first row contains 
# the number of tweets made by that person. The second row
# contains the userid (as an integer) for that person.

num_tweets = numpy.zeros((2, len(user_dict)), dtype = 'int32')

for ind, userid in enumerate(user_dict):
    num_tweets[0, ind] = len(user_dict[userid])
    num_tweets[1, ind] = userid

sort_inds = num_tweets[0, :].argsort()[::-1]

# Set the reference start time to the time of the first tweet recorded over the entire
# network.

time_all_tweets.sort() # Sorts the times of the tweets from oldest to newest

reference_start = time_all_tweets[0]
reference_stop  = time_all_tweets[-1]

with open('activity_by_second.dat', 'w') as wfile:
    for time_ind in xrange(int((reference_stop - reference_start).total_seconds())):
        if time_ind%1000 == 0:
            print 'At time {} of {}'.format(time_ind, (reference_stop - reference_start).total_seconds())

        cur_time = reference_start + datetime.timedelta(seconds = time_ind)

        for user in user_dict:
            if user_dict[user].get(cur_time, 0) == 1:
                wfile.write('{}\t'.format(user))

        wfile.write('\n')