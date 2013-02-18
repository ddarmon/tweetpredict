import datetime
import numpy
import pylab

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

def binarize_timeseries(day, num_bins):
	binarized = numpy.zeros(num_bins)

	binarized[day] = 1

	return binarized

def divide_by_day(reference_date, ts, num_days, user_id = 'NA', toplot = False):
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
				ts_by_day[-1].append((timepoint - starttime).total_seconds())
			else: # we're not in the desired window, so don't record it
				pass
		else: # we're not in the same day, so append a new day to ts_by_day
			if len(ts_by_day[-1]) != 0:
				ts_by_day.append([])

			# Update our window to the current day

			starttime = starttime.replace(day = timepoint.day, month = timepoint.month, year = timepoint.year)

			endtime = endtime.replace(day = timepoint.day, month = timepoint.month, year = timepoint.year)

			if (is_in_window(timepoint, starttime, endtime)): # We're in the desired window
				ts_by_day[-1].append((timepoint - starttime).total_seconds())
			else:
				pass

	num_bins = (endtime - starttime).total_seconds() + 1

	# if toplot:
	# 	f, axarr = pylab.subplots(num_days, sharex=True)

	# for axind, day in enumerate(ts_by_day):
	# 	if axind > num_days-1:
	# 		break

	# 	binarized = binarize_timeseries(day, num_bins)

	# 	if toplot:
	# 		axarr[axind].vlines(numpy.arange(num_bins)[binarized==1], -0.5, 0.5)
	# 		axarr[axind].yaxis.set_visible(False)

	# if toplot:
	# 	pylab.locator_params(axis = 'x', nbins = 5)
	# 	pylab.xlabel('Time (each time tick corresponds to 1 s)')
	# 	pylab.savefig('raster-{}.pdf'.format(user_id))

	# pylab.show()

	return ts_by_day, num_bins