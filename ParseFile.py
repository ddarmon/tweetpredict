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

# Get the times between the tweets:

interarrivals = []

def parsedate(datestring):
    part1, part2 = datestring.split(' ')
    
    year, month, day = part1.split('-')
    
    hour, minute, second = part2.split(':')
    
    return year, month, day, hour, minute, second

for ind in range(1, len(ts)):
    
    t1 = map(int, parsedate(ts[ind - 1]))
    t2 = map(int, parsedate(ts[ind]))
    
    date_obj1 = datetime.datetime(year = t1[0], month = t1[1], day = t1[2], hour = t1[3], minute = t1[4], second = t1[5])
    date_obj2 = datetime.datetime(year = t2[0], month = t2[1], day = t2[2], hour = t2[3], minute = t2[4], second = t2[5])
    
    interarrivals.append((date_obj2 - date_obj1).seconds)

sorted_interarrivals = sorted(interarrivals) # Sort the interarrivals, to give some idea of the time scales for this system

seconds = numpy.sum(interarrivals) + 1 # The total number of seconds in the record

binarized = numpy.zeros(seconds)

binarized[0] = 1
binarized[numpy.cumsum(interarrivals)] = 1

f, axarr = pylab.subplots(1, sharex=True)

axarr.vlines(numpy.arange(seconds)[binarized==1], -0.5, 0.5)
axarr.yaxis.set_visible(False)
pylab.xlabel('Time (s)')
pylab.xlim(0, numpy.max(numpy.cumsum(interarrivals)[-1]))
pylab.locator_params(axis = 'x', nbins = 5)
pylab.savefig('_num_tweets.pdf')
pylab.show()

pylab.figure()
pylab.hist(interarrivals, bins = numpy.unique(interarrivals).shape[0], normed = True)
pylab.show()

# Q: How to deal with *night-time*?

# pylab.figure()
# pylab.hist(num_tweets[0,:], bins = 200, normed = True)
# pylab.xlabel('Number of Tweets Made')
# pylab.ylabel('Count of Users Making that Number of Tweets')
# pylab.show()