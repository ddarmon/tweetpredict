import ipdb
import numpy
import pylab
import datetime
import random

from dividebyday import divide_by_day, binarize_timeseries

from extract_timeseries_methods import *

# Setup of .csv file:
#    "row_added_at","status_id","user_id","status_date","status_text","status_is_retweet","status_retweet_of","status_retweet_count","status_latitude","status_longitude"
#
# Thus, we're more interested in:
#      "row_added_at", which gives us information about when the tweet occurs
#      "user_id", the user who tweets
#
# With these two, for each user we can create a binary time series that
# indicates 1 - a tweet, 0 - no tweet
#
# Think of a neuron firing v. not!

files = ['../timeseries_a.tsv', '../timeseries_b.tsv', '../timeseries_c.tsv']

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
            user_dict[user].append(cur_time)
        else: # If not, add the user to the dictionary and record the time of their first tweet
            user_dict[user] = [cur_time]

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

# iresolution = 60*10
iresolution = None

# Some 49s [98078133, 95646719, 8957852]

# Some 50s [69124203, 68113369, 88498786, 49620984, 749333, 150312587]

# Some 51s [8474322, 140983662, 113651070]

for user_id in ['8957852']:
    ts = user_dict[user_id]

    ts.sort() # Sort the users Tweets. For the user ranked 68, for example, one of the Tweets was out of order.

    # You could use these if you *don't* want to forward- and back-pad with empty
    # days.

    # reference_start = ts[0]
    # reference_stop  = ts[-1]

    ts_by_day, days, num_bins = divide_by_day(reference_start, reference_stop, ts, user_id = user_id)

    include_idxs = []

    for idx, day in enumerate(days):
        if include_date(day):
            include_idxs.append(idx)

    for day in days:
        print day

    print len(days)

    print len(include_idxs)