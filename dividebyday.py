import datetime
import numpy

numpy.random.seed(0) # Make the result reproducible

x = numpy.random.randint(low = 1, high = 1000, size = 1000)

increments = x.cumsum() # The number of seconds to add to reference_date

# A sythetic reference start date.

reference_date = datetime.datetime(year = 2012, month = 1, day = 1)

# A time series object, like the one associated with each user from
# the Twitter database.

ts = [reference_date]

for increment in increments:
	ts.append(reference_date + datetime.timedelta(seconds = int(increment)))

# Idea: Set a starttime and an endtime. Collect all of the ts[i]
# that lie between starttime and endtime. Generate a binary timeseries
# from that.

# For now, set these to 6am to 10pm

starttime = datetime.datetime(year = reference_date.year, month = reference_date.month, day = reference_date.day, hour = 6)
endtime   = datetime.datetime(year = reference_date.year, month = reference_date.month, day = reference_date.day, hour = 22)

for timepoint in ts:
	if starttime:
		pass #START HERE. Think this through, *carefully*. Use a picture!