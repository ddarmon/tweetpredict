import ipdb
import numpy
import pylab
import datetime
import random

def parsedate(datestring):
    part1, part2 = datestring.split(' ')
    
    year, month, day = part1.split('-')
    
    hour, minute, second = part2.split(':')
    
    return year, month, day, hour, minute, second

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

# NOTE: We need to distinguish between .tsv and .csv files.

delimit_type = 'tsv'

ofile = open('../Binladen.tsv')

# delimit_type = 'csv'
# 
# ofile = open('../Irene15K.csv')

# Create hash table of the form {userid : [time_of_tweet1, time_of_tweet2, ..., time_of_tweetT]}

user_dict = {}

line = ofile.readline()

time_all_tweets = [] # Keep track of when *all* of the tweets occur, so we can
                     # set a relative t = 0.

while line != '':
    line = ofile.readline()
    
    if '2011-' in line: # Several of the lines are broken up (in my opinion, unecessarily). This catches those lines.
        if delimit_type  == 'csv':
            lsplit = line.split(',')
        elif delimit_type == 'tsv':
            lsplit = line.split('\t')

        time = lsplit[0] # Get out the time of the tweet
        user = lsplit[2] # Get out the userid of the person who tweeted
        
        year, month, day, hour, minute, second = map(int, parsedate(time))
        
        cur_time = datetime.datetime(year = year, month = month, day = day, hour = hour, minute = minute, second = second)
        
        time_all_tweets.append(cur_time)
        
        if user in user_dict: # If the user is in the dictionary, add the time to the list of times they tweeted.
            user_dict[user].append(cur_time)
        else: # If not, add the user to the dictionary and record the time of their first tweet
            user_dict[user] = [cur_time]
    else:
        pass

ofile.close()

num_tweets = numpy.zeros((2, len(user_dict)), dtype = 'int32')

for ind, userid in enumerate(user_dict):
    num_tweets[0, ind] = len(user_dict[userid])
    num_tweets[1, ind] = userid

sort_inds = num_tweets[0, :].argsort()[::-1]

# Set the reference start time to the time of the first tweet recorded over the entire
# network.

time_all_tweets.sort() # Sorts the times of the tweets from oldest to newest

reference_date = time_all_tweets[0]

# To extract the time-of-tweets for the (k + 1)st most common tweeter, use
# the following line of code.

# ids = range(0, 20) # Gets the most frequent tweeters

# ids = range(1, 21) # Gets the least frequent tweeters
# ids = map(lambda input : -input, ids) # Gets the least frequent tweeters

# ids = random.sample(range(len(sort_inds)), 10)

ids = [0, 1, 3]

toplot = True

if toplot:
    f, axarr = pylab.subplots(len(ids), sharex=True)

for axind, uid in enumerate(ids):
    ts = user_dict[str(num_tweets[1, sort_inds][uid])]
    
    # Sort the time series, since apparently the tweets aren't necessarily
    # stored in chronological order.
    
    ts = sorted(ts)

    # Each entry in ts is a string of the form:
    # 'year-month-day hour:min:sec', e.g. '2011-05-03 21:53:18'

    # For the bin Laden data set, all of the Tweets occur on or after 2011-05-01. So use that to make
    # the start reference date.
    
    # start_time stores the date in a tuple of the form (year, month, day, hour, min, second)
    # start_time = (2011, 5, 1, 0, 0, 0)
    # reference_date = datetime.datetime(year = start_time[0], month = start_time[1], day = start_time[2], hour = start_time[3], minute = start_time[4], second = start_time[5])
    
    # Store the (relative) time each tweet occurred.
    
    tweet_time = []
    
    for ind in range(0, len(ts)):
    
        t1 = ts[ind]
    
        tweet_time.append((t1 - reference_date).total_seconds())

    seconds = tweet_time[-1] + 1 # The total number of seconds from the start_time

    binarized = numpy.zeros(seconds)

    binarized[tweet_time] = 1
    
    if toplot:
        axarr[axind].vlines(numpy.arange(seconds)[binarized==1], -0.5, 0.5)
        axarr[axind].yaxis.set_visible(False)

ofile = open('twitter_ts.dat', 'w')

for val in binarized:
    ofile.write('{} '.format(int(val)))
    
ofile.close()

if toplot:
    pylab.locator_params(axis = 'x', nbins = 5)
    pylab.xlabel('Time (s)')
    pylab.show()