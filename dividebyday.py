import datetime
import numpy
import pylab
import ipdb

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

def is_next_day(day1, day2):
	# We'll ask 'Is day2 the day after day1?'

	next_day = day1 + datetime.timedelta(days = 1)

	if (next_day.day != day2.day):
		is_same = False
	elif (next_day.month != day2.month):
		is_same = False
	elif (next_day.year != day2.year):
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

def binarize_timeseries(day, num_bins):
	binarized = numpy.zeros(num_bins)

	binarized[day] = 1

	return binarized

def is_before(day1, day2):
	# We'll ask: is day1 before day2?

	if (day2 - day1).total_seconds() >= 0:
		return True
	else:
		return False

def divide_by_day(reference_start, reference_stop, ts, user_id = 'NA', to_reference_stop = True, cutoff_start = 6, cutoff_stop = 22):
	# Idea: Set a starttime and an endtime. Collect all of the ts[i]
	# that lie between starttime and endtime. Generate a binary timeseries
	# from that.

	# Use reference_start and reference_stop to decide what day we should
	# start from and end on in terms of generating a time series for 
	# each user.

	normalized_reference_start = datetime.datetime(year = reference_start.year, month = reference_start.month, day = reference_start.day, hour = cutoff_start)

	day_start = datetime.datetime(year = reference_start.year, month = reference_start.month, day = reference_start.day, hour = cutoff_start)
	day_stop  = datetime.datetime(year = reference_stop.year, month = reference_stop.month, day = reference_stop.day, hour = cutoff_start)

	ts_by_day_dict = {}

	for timepoint in ts:
		relative_start_cutoff = datetime.datetime(year = timepoint.year, month = timepoint.month, day = timepoint.day, hour = cutoff_start)
		relative_stop_cutoff  = datetime.datetime(year = timepoint.year, month = timepoint.month, day = timepoint.day, hour = cutoff_stop)

		# Check if the timepoint is in the desired window.

		if is_in_window(timepoint, relative_start_cutoff, relative_stop_cutoff):

			# Add the timepoint's relative distance from the start timepoint.

			relative_time = (timepoint - relative_start_cutoff).total_seconds()

			if relative_start_cutoff in ts_by_day_dict:
				ts_by_day_dict[relative_start_cutoff].append(relative_time)
			else:
				ts_by_day_dict[relative_start_cutoff] = [relative_time]

	# From ts_by_day_dict, get out the days of interest and put them in ts_by_day.

	ts_by_day = []
	days = []

	for day_ind in range((day_stop - day_start).days + 1):
		cur_day = normalized_reference_start + datetime.timedelta(days = day_ind)

		days.append(cur_day)

		ts_by_day.append(ts_by_day_dict.get(cur_day, [None]))



	num_bins = (relative_stop_cutoff - relative_start_cutoff).total_seconds() + 1

	return ts_by_day, days, num_bins