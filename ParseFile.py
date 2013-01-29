import ipdb
import numpy
import pylab

# Setup of .csv file:
#       "row_added_at","status_id","user_id","status_date","status_text","status_is_retweet","status_retweet_of","status_retweet_count","status_latitude","status_longitude"
#
# Thus, we're more interested in:
#           "row_added_at", which gives us information about when the tweet occurs
#           "user_id", the user who tweets
#
# With these two, for each user we can create a binary time series that
# indicates 1 - a tweet, 0 - no tweet
#
# Think of a neuron firing v. not!

delimit_type = 'tsv'

ofile = open('../Binladen.tsv')

# Create hash table of the form {userid : [time_of_tweet1, time_of_tweet2, ..., time_of_tweetT]}

user_dict = {}

line = ofile.readline()

while line != '':
    line = ofile.readline()
    
    if '2011-' in line: # Several of the lines are broken up (in my opinion, unecessarily). This catches those lines.
        if delimit_type  == 'csv':
            lsplit = line.split(',')
        elif delimit_type == 'tsv':
            lsplit = line.split('\t')

        time = lsplit[0] # Get out the time of the tweet
        user = lsplit[2] # Get out the userid of the person who tweeted

        if user in user_dict: # If the user is in the dictionary, add the time to the list of times they tweeted.
            user_dict[user].append(time)
        else: # If not, add the user to the dictionary and record the time of their first tweet
            user_dict[user] = [time]
    else:
        pass

ofile.close()

num_tweets = numpy.zeros((2, len(user_dict)), dtype = 'int32')

for ind, userid in enumerate(user_dict):
    num_tweets[0, ind] = len(user_dict[userid])
    num_tweets[1, ind] = userid

sort_inds = num_tweets[0, :].argsort()[::-1]

# To extract the time-of-tweets for the (k + 1)st most common tweeter, use
# the following line of code.

k = 0
# k = 306 # The person who tweets the least

ts = user_dict[str(num_tweets[1, sort_inds][k])]

# Each entry in ts is a string of the form:
# 'year-month-day hour:min:sec', e.g. '2011-05-03 21:53:18'

import datetime

def parsedate(datestring):
    part1, part2 = datestring.split(' ')
    
    year, month, day = part1.split('-')
    
    hour, minute, second = part2.split(':')
    
    return year, month, day, hour, minute, second

# For the bin Laden data set, all of the Tweets occur on or after 2011-05-01. So use that to make
# the start reference date.

start_time = (2011, 5, 1, 0, 0, 0) # (year, month, day, hour, min, second)

reference_date = datetime.datetime(year = start_time[0], month = start_time[1], day = start_time[2], hour = start_time[3], minute = start_time[4], second = start_time[5])

# Store the (relative) time the tweet occurred.

tweet_time = []

for ind in range(0, len(ts)):
    
    t1 = map(int, parsedate(ts[ind]))
    
    date_obj1 = datetime.datetime(year = t1[0], month = t1[1], day = t1[2], hour = t1[3], minute = t1[4], second = t1[5])
    
    tweet_time.append((date_obj1 - reference_date).total_seconds())

seconds = tweet_time[-1] + 1 # The total number of seconds from the start_time

binarized = numpy.zeros(seconds)

binarized[tweet_time] = 1

f, axarr = pylab.subplots(1, sharex=True)

axarr.vlines(numpy.arange(seconds)[binarized==1], -0.5, 0.5)
axarr.yaxis.set_visible(False)
pylab.xlabel('Time (s)')
pylab.locator_params(axis = 'x', nbins = 5)
pylab.savefig('_num_tweets.pdf')
pylab.show()

# pylab.figure()
# pylab.hist(interarrivals, bins = numpy.unique(interarrivals).shape[0], normed = True)
# pylab.show()

# Q: How to deal with *night-time*?

# pylab.figure()
# pylab.hist(num_tweets[0,:], bins = 200, normed = True)
# pylab.xlabel('Number of Tweets Made')
# pylab.ylabel('Count of Users Making that Number of Tweets')
# pylab.show()