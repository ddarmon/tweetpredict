# For a given user of interest, this code extracts the
# number of tweets by that user's followers for any
# given one hour period.

import ipdb
import numpy
import pylab
import datetime
import random
import copy

from dividebyday import divide_by_day, binarize_timeseries

from extract_timeseries_methods import *

from filter_data_methods import *

user_of_interest = '989' # Om Malik's Twitter id, used to seed the original network.

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
        
        if user in user_dict: # If the user is in the dictionary, add the time to the list of times they tweeted.
            user_dict[user].append(cur_time)
        else: # If not, add the user to the dictionary and record the time of their first tweet
            user_dict[user] = [cur_time]

    ofile.close()

# Get out the follower network of all of the users.

# Recall that the network is stored as
#
#   from_id -> to_id
# 
# which in this context means
#  
#   user_id -> follower_id
# 
# adj_dict is the of the form {userid : [followerid1, followerid2, ...]}

adj_dict = {}

with open('/Users/daviddarmon/Documents/R/Research/tweetpredict/community_structure/_follower_15K_user.txt') as ofile:
    for line in ofile:
        from_id, tmp, to_id, tmp = line.split()

        if from_id in adj_dict: # we've already seen this user
            adj_dict[from_id].append(to_id)
        else: # we haven't seen this user yet
            adj_dict[from_id] = [to_id]

for user_of_interest in adj_dict:
    print 'Working on the user with user id {}...'.format(user_of_interest)
    # Tabulate the number of Tweets per one hour period into a dictionary
    # of the form
    #   {tp : number of tweets}

    counts_by_hour = {}

    for user in adj_dict[user_of_interest]:
        if user in user_dict: # Only try to tabulate for users who have a status
            for tp in user_dict[user]: # tp stands for 'time point'
                time_struc = datetime.datetime(year = tp.year, month = tp.month, day = tp.day, hour = tp.hour)

                if time_struc in counts_by_hour:
                    counts_by_hour[time_struc] += 1
                else:
                    counts_by_hour[time_struc] = 1

    ipdb.set_trace()

    # Make the counts non-sparse, by starting at the
    # start time and recording the value from then
    # until some stop time.

    start_time = datetime.datetime(2011, 4, 26, 0, 0)
    stop_time  = datetime.datetime(2011, 6, 24, 23, 0)

    cur_time = copy.copy(start_time)

    with open('follower_activity_2011/follower_activity_{}.dat'.format(user_of_interest), 'w') as wfile:
        while cur_time <= stop_time:
            wfile.write('{}, {}\n'.format(cur_time, counts_by_hour.get(cur_time, 0)))

            cur_time = cur_time + datetime.timedelta(hours = 1)