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

def plot_raster(binarized, num_bins, axarr, axind):
    axarr[axind].vlines(numpy.arange(num_bins)[binarized==1], -0.5, 0.5)
    axarr[axind].yaxis.set_visible(False)

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

reference_date = time_all_tweets[0]

from dividebyday import divide_by_day, binarize_timeseries

def export_ts(ts, user_id, num_bins, toplot = False, iresolution = None):
    if iresolution != None:
        ofile = open('byday-{0}s-{1}.dat'.format(iresolution, user_id), 'w')
    else:
        ofile = open('byday-1s-{0}.dat'.format(user_id), 'w')

    f, axarr = pylab.subplots(len(ts), sharex = True)

    if iresolution != None:
        num_bins_coarse = num_bins / iresolution # Account for the fact that we plan to coarsen the timeseries

    for axind, day in enumerate(ts):
        binarized = binarize_timeseries(day, num_bins)

        if iresolution != None:
            binarized = coarse_resolution(binarized, iresolution = iresolution)

            plot_raster(binarized, num_bins_coarse, axarr, axind)
        else:
            plot_raster(binarized, num_bins, axarr, axind)

        for symbol in binarized:
            ofile.write("{0}".format(int(symbol)))

        ofile.write("\n")

    if iresolution == None:
        pylab.xlabel('Time (each time tick corresponds to 1 s)')
    else:
        pylab.xlabel('Time (each time tick corresponds to {} s)'.format(iresolution))
    pylab.locator_params(axis = 'x', nbins = 5)

    if iresolution == None:
        pylab.savefig('raster-1s-{0}.pdf'.format(user_id))
    else:
        pylab.savefig('raster-{0}s-{1}.pdf'.format(iresolution, user_id))
    pylab.show()

    ofile.close()

iresolution = 60*10

for user_rank in xrange(20):
    user_id = str(num_tweets[1, sort_inds][user_rank])

    ts = user_dict[user_id]

    reference_date = ts[0]

    ts_by_day, num_bins = divide_by_day(reference_date, ts, num_days = 20, user_id = user_id, toplot = True)

    export_ts(ts_by_day[1:30], user_id, toplot = True, num_bins = num_bins, iresolution = iresolution)