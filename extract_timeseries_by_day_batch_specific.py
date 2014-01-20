import ipdb
import numpy
import pylab
import datetime
import random

from dividebyday import divide_by_day, binarize_timeseries

from extract_timeseries_methods import *

from filter_data_methods import *

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

# Get out the top K, prespecified by some ranking.

# In this case, we're getting the top 3000 from 2012,
# but using the 2011 data.

start = 118+42
users = get_K_users(K = 3000, start = start, year = None)

for ind, user_id in enumerate(users):
    print 'Working on the user with the {}th tweet rate'.format(start+ind)

    # We have to catch when the user of interest did *not* Tweet
    # at all during the time period.

    try:
        ts = user_dict[user_id]
    except KeyError:
        ts = []

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

    export_ts(numpy.array(ts_by_day)[include_idxs], user_id, toplot = False, saveplot = False, num_bins = num_bins, iresolution = iresolution)

    # with open('2011_tweetrank.txt', 'w') as ofile:
    #     for ind in range(num_tweets.shape[1]):
    #         ofile.write('{}\t{}\n'.format(num_tweets[1, sort_inds][ind], num_tweets[0, sort_inds][ind]))