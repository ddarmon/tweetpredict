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

def coarse_resolution(binarized, iresolution = 60):
    # Recall: The current resolution is in seconds. We want to be able
    # to group together anything from seconds

    # The number of bins we'll have after coarsening.

    n_coarsebins = numpy.divide(binarized.shape[0], iresolution)

    # An (empty) binary time series to hold the
    # coarsened time series.

    binarized_coarse = numpy.zeros(n_coarsebins)

    for cind in range(n_coarsebins):
        binarized_coarse[cind] = numpy.sum(binarized[(cind*iresolution):((cind + 1)*iresolution)])
    
    # Convert the *number* of tweets in the time interval
    # into *whether* a tweet occurs in that time interval.
    
    binarized_coarse[binarized_coarse != 0] = 1
    
    return binarized_coarse

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

reference_date = time_all_tweets[0]

# To extract the time-of-tweets for the (k + 1)st most common tweeter, use
# the following line of code.

ids = range(0, 10) # Gets the most frequent tweeters

# ids = range(1, 11) # Gets the least frequent tweeters
# ids = map(lambda input : -input, ids) # Gets the least frequent tweeters

# ids = random.sample(range(len(sort_inds)), 10)

# ids = [0]

toplot = True

# Set byuser to TRUE if you want to specify the userid,
# and FALSE if you want to specify the kth highest
# frequency tweeter.

byuser = False

tocoarsen = True

tosave = False

if tosave == False:
    print 'Warning: the time series are *not* being saved!'

# The number of seconds per each in the discretized 
# time series bin.

iresolution = 60*15

if byuser == True:
    # ids = ['43600056', '92102625', '92285511'] # UniBul accounts
    
    user_file = open('to_investigate.dat')
    
    ids = user_file.readline().split(',')
    
    user_file.close()

if toplot:
    f, axarr = pylab.subplots(len(ids), sharex=True)

for axind, uid in enumerate(ids):
    if axind%100 == 0:
        print 'Parsing file for Tweeter {}...'.format(axind)
    
    if byuser == True:
        ts = user_dict[uid]
        user_id = uid
    else:
        ts = user_dict[str(num_tweets[1, sort_inds][uid])]
        user_id = num_tweets[1, sort_inds][uid]
    
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
    
    # If we decide to coarse grain the timeseries below the
    # 1 second resolution.
    
    if tocoarsen:
        # Coarse grain the time series.
        
        binarized = coarse_resolution(binarized, iresolution = iresolution)

        # Recompute 'seconds', that is, the total number of
        # units of time, where the unit is given by iresolution.

        seconds = numpy.ceil((tweet_time[-1] + 1)/float(iresolution)) # The total number of time units from start_time


    # print 'The true number of Tweets is {}. After binning, there appear to be {}.\nAfter coarsening, there are {}.'.format(len(tweet_time), numpy.unique(tweet_time).shape[0], numpy.sum(binarized))

    if toplot:
        axarr[axind].vlines(numpy.arange(seconds)[binarized==1], -0.5, 0.5)
        axarr[axind].yaxis.set_visible(False)
    
    if tosave == True:
        ofile = open('timeseries/twitter_ts_{}-{}.dat'.format(user_id, iresolution), 'w')
        for val in binarized:
            ofile.write('{} '.format(int(val)))
        ofile.close()

if toplot:
    pylab.locator_params(axis = 'x', nbins = 5)
    if tocoarsen == True:
        pylab.xlabel('Time (each time tick corresponds to {} s)'.format(iresolution))
    else:
        pylab.xlabel('Time (each time tick corresponds to 1 s)')
    pylab.show()