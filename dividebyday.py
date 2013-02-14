import datetime
import numpy

def is_same_day(day1, day2):
	if (day1.day != day2.day):
		is_same = False
	elif (day1.month != day2.month):
		is_same = False
	elif (day1.year != day2.year):
		is_same = False
	else:
		is_same = True

	return is_same

def is_in_window(day, starttime, endtime):
	diff_back = (day - starttime).total_seconds()
	diff_forward = (endtime - day).total_seconds()
	if (diff_back < 0) or (diff_forward < 0):
		is_in = False
	else:
		is_in = True

	return is_in
	

numpy.random.seed(0) # Make the result reproducible

x = numpy.random.randint(low = 1, high = 3000, size = 1000)

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

# ts_by_day is a list of list, where the internal lists contain the
# timeseries broken up by day

ts_by_day = [[]]

for timepoint in ts:
	# Check if we're still in the same day bracketed 
	# by starttime and endtime.

	if (is_same_day(timepoint, starttime)): # we're in the same day, so append if we're in the window
		if (is_in_window(timepoint, starttime, endtime)): # We're in the desired window
			ts_by_day[-1].append(timepoint)
		else: # we're not in the desired window, so don't record it
			pass
	else: # we're not in the same day, so append a new day to ts_by_day
		if len(ts_by_day[-1]) != 0:
			ts_by_day.append([])

		# Update our window to the current day

		starttime = starttime.replace(day = timepoint.day, month = timepoint.month, year = timepoint.year)

		endtime = endtime.replace(day = timepoint.day, month = timepoint.month, year = timepoint.year)

		if (is_in_window(timepoint, starttime, endtime)): # We're in the desired window
			ts_by_day[-1].append(timepoint)
		else:
			pass

